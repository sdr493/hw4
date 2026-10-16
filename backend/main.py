"""Campus Customs API: products, product images, accounts and the shopping chat agent.

Run from this backend folder:  uvicorn main:app --reload --port 8000
"""

import json
import logging
import math
import os

from fastapi import Cookie, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from agent import ChatNotConfigured, run_chat
from auth import make_router, session_user_id
from models import (
    MAX_HISTORY_MESSAGES, Bootstrap, ChatHistoryMessage, ChatReply, ChatRequest, ChatTurn, PageContext, ProductCard,
    PromoCode, PromoRedeemRequest, PromoRedeemResult,
)
from promotions import applied_discount, generate_promo_code, redeem_promo_code
from safety import redact_financial
from tools import (
    AUDIENCES, IMAGES_DIR, STYLES, ShopDeps, by_popularity, connect, connect_rw, find_product, load_inventory,
    load_products,
)

MAX_PAGE_SIZE = 20
log = logging.getLogger("campus_customs")

app = FastAPI(title="Campus Customs API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("FRONTEND_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["GET", "POST"],
    allow_credentials=True,
    allow_headers=["*"],
)
app.mount("/media/products", StaticFiles(directory=IMAGES_DIR), name="product-images")
app.include_router(make_router(connect_rw))


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/filters")
def filters() -> dict:
    return {
        "styles": [{"key": k, "label": label} for k, label, _ in STYLES],
        "audiences": [{"key": k, "label": label} for k, label in AUDIENCES],
    }


@app.get("/api/bootstrap", response_model=Bootstrap)
def bootstrap() -> Bootstrap:
    """Preload tool: the whole catalogue with stock for every size, in one request, when the site opens."""
    with connect() as conn:
        products = load_products(conn)
        stock: dict[str, list[dict]] = {}
        for r in conn.execute("SELECT id AS inventory_id, product_id, size, quantity FROM inventory"):
            stock.setdefault(r["product_id"], []).append(
                {"inventory_id": r["inventory_id"], "size": r["size"], "quantity": r["quantity"], "in_stock": r["quantity"] > 0})
    order = {s: i for i, s in enumerate(["XS", "S", "M", "L", "XL", "XXL"])}
    for p in products:
        p["inventory"] = sorted(stock.get(p["product_id"], []), key=lambda s: order.get(s["size"], 9))
    return Bootstrap(
        products=products,
        filters=filters(),
        popular_ids=[p["product_id"] for p in by_popularity(products)[:5]],
    )


@app.get("/api/products/popular")
def popular(limit: int = Query(5, ge=1, le=5)) -> list[dict]:
    with connect() as conn:
        return by_popularity(load_products(conn))[:limit]


@app.get("/api/products")
def list_products(
    style: str | None = None,
    audience: str | None = None,
    q: str | None = None,
    sort: str = Query("popular", pattern="^(popular|price_asc|price_desc|name)$"),
    in_stock: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(MAX_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> dict:
    with connect() as conn:
        items = load_products(conn)
    if style:
        items = [p for p in items if p["style"] == style]
    if audience in ("mens", "womens"):
        # Men's and women's views include unisex styles, which fit everyone.
        items = [p for p in items if p["audience"] in (audience, "unisex")]
    elif audience == "unisex":
        items = [p for p in items if p["audience"] == "unisex"]
    if in_stock:
        items = [p for p in items if p["total_stock"] > 0]
    if q:
        needle = q.lower()
        items = [p for p in items if needle in " ".join(
            [p["name"], p["description"], *p["colors"], *p["search_tags"]]).lower()]

    if sort == "price_asc":
        items.sort(key=lambda p: (p["price"], p["name"]))
    elif sort == "price_desc":
        items.sort(key=lambda p: (-p["price"], p["name"]))
    elif sort == "name":
        items.sort(key=lambda p: p["name"])
    else:
        items = by_popularity(items)

    total = len(items)
    pages = max(1, math.ceil(total / page_size))
    start = (page - 1) * page_size
    return {"items": items[start:start + page_size], "total": total, "page": page, "pages": pages}


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict:
    with connect() as conn:
        product = find_product(conn, product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        product["inventory"] = load_inventory(conn, product_id)
    return product


# ---------------------------------------------------------------------------
# Promo codes (logged-in shoppers only)
# ---------------------------------------------------------------------------

def _require_user(cc_session: str | None) -> int:
    user_id = session_user_id(cc_session)
    if not user_id:
        raise HTTPException(status_code=401, detail="Log in to see your promo code")
    return user_id


@app.get("/api/promo", response_model=PromoCode)
def my_promo(cc_session: str | None = Cookie(default=None)) -> PromoCode:
    """The logged-in shopper's own code, generated the first time they ask (right after sign-up or log-in)."""
    return generate_promo_code(_require_user(cc_session))


@app.post("/api/promo/redeem", response_model=PromoRedeemResult)
def redeem_promo(body: PromoRedeemRequest, cc_session: str | None = Cookie(default=None)) -> PromoRedeemResult:
    return redeem_promo_code(_require_user(cc_session), body.code)


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

def _load_history(user_id: int) -> list[ChatHistoryMessage]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT role, content, products_json FROM chat_messages WHERE user_id = ? "
            "ORDER BY id DESC LIMIT ?", (user_id, MAX_HISTORY_MESSAGES),
        ).fetchall()
    history = []
    for r in reversed(rows):
        products = []
        if r["products_json"]:
            try:
                # Older rows store total_stock instead of in_stock.
                products = [ProductCard.model_validate({"in_stock": p.get("total_stock", 0) > 0, **p})
                            for p in json.loads(r["products_json"])]
            except (ValueError, TypeError, AttributeError):
                products = []
        history.append(ChatHistoryMessage(role=r["role"], content=r["content"], products=products))
    return history


def _save_turn(user_id: int, message: str, reply: ChatReply) -> None:
    products_json = json.dumps([p.model_dump() for p in reply.products]) if reply.products else None
    with connect_rw() as conn:
        conn.execute("INSERT INTO chat_messages (user_id, role, content) VALUES (?, 'user', ?)", (user_id, message))
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'assistant', ?, ?)",
            (user_id, reply.reply, products_json),
        )


def _build_deps(user_id: int | None, page: PageContext | None) -> ShopDeps:
    """Agent context: the logged-in shopper's name and email, plus the page they're on."""
    deps = ShopDeps()
    with connect() as conn:
        if user_id:
            row = conn.execute("SELECT name, first_name, last_name, email FROM users WHERE id = ?", (user_id,)).fetchone()
            if row:
                first, last = row["first_name"], row["last_name"]
                if not first:
                    first, _, last = row["name"].partition(" ")
                deps.user_id, deps.first_name, deps.last_name, deps.email = user_id, first, last or None, row["email"]
                deps.discount_percent = applied_discount(user_id)
        if page:
            deps.page_path = page.path
            # Only trust a product id that exists in the catalogue.
            product = find_product(conn, page.product_id) if page.product_id else None
            if product:
                deps.viewing_product_id, deps.viewing_product_name = product["product_id"], product["name"]
    return deps


@app.get("/api/chat/history", response_model=list[ChatHistoryMessage])
def chat_history(cc_session: str | None = Cookie(default=None)) -> list[ChatHistoryMessage]:
    """Recent chat for the logged-in shopper (empty for guests)."""
    user_id = session_user_id(cc_session)
    return _load_history(user_id) if user_id else []


@app.post("/api/chat", response_model=ChatReply)
async def chat(body: ChatRequest, cc_session: str | None = Cookie(default=None)) -> ChatReply:
    user_id = session_user_id(cc_session)
    if user_id:
        # Logged-in memory comes from the database, never from the browser.
        history = [ChatTurn(role=m.role, content=m.content) for m in _load_history(user_id)]
    else:
        # Guests: only this visit's messages, sent by the browser and never saved.
        history = body.history
    deps = _build_deps(user_id, body.page)

    try:
        # Card numbers / SSNs are removed before the message goes anywhere (model, history, audit trail).
        message, _ = redact_financial(body.message.strip())
        reply = await run_chat(message, history, deps)
    except ChatNotConfigured:
        raise HTTPException(status_code=503, detail="The chat assistant isn't configured yet")
    except Exception:
        log.exception("Chat agent failed")
        raise HTTPException(status_code=502, detail="The chat assistant is having trouble right now")

    if user_id:
        _save_turn(user_id, message, reply)
    return reply
