"""Catalogue data access and the tools the shopping agent can call.

Every fact the agent states about a product (price, stock, sizes, colors) must come from
these tools, which read the local SQLite database. Tools are read-only.
"""

from __future__ import annotations

import json
import os
import sqlite3
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from pydantic_ai import RunContext

from models import (
    AccountInfo, EmailCheck, ProductCard, ProductComparison, ProductInfo, PromoCode, SizeStock, StockReport,
)
from promotions import generate_promo_code

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("CAMPUS_DB_PATH", ROOT / "data" / "campus_customs.db"))
IMAGES_DIR = Path(os.getenv("CAMPUS_IMAGES_DIR", ROOT / "data" / "products"))

# Shopper-facing style groups, matched against catalogue.garment_type (checked in order).
STYLES = [
    ("quarter-zips", "Quarter-Zips", ("quarter-zip",)),
    ("jackets-fleece", "Jackets & Fleece", ("jacket", "fleece", "full-zip")),
    ("hoodies", "Hoodies", ("hood",)),
    ("t-shirts", "T-Shirts", ("t-shirt",)),
    ("long-sleeve", "Long Sleeve", ("long-sleeve",)),
    ("crewnecks", "Crewnecks", ("crew", "mockneck")),
]

# The catalogue has no gender field, so audience comes from words in the product name.
MENS_WORDS = {"mens", "dad", "grandpa", "uncle", "brother"}
WOMENS_WORDS = {"womens", "mom", "grandma", "aunt"}
AUDIENCES = [("mens", "Men's"), ("womens", "Women's"), ("unisex", "Unisex")]
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]
MAX_SEARCH_RESULTS = 12
SEARCH_DESCRIPTION_CHARS = 90


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def connect_rw() -> sqlite3.Connection:
    """Writable connection, used only for accounts and saving chat history."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def style_of(garment_type: str) -> str:
    g = garment_type.lower()
    for key, _, words in STYLES:
        if any(w in g for w in words):
            return key
    return "other"


def audience_of(name: str) -> str:
    words = set(name.lower().replace("'", "").split())
    if words & MENS_WORDS:
        return "mens"
    if words & WOMENS_WORDS:
        return "womens"
    return "unisex"


def popularity(conn: sqlite3.Connection) -> Counter:
    """There is no sales table, so popularity = how often a product was shown to shoppers in chat."""
    counts: Counter = Counter()
    for (raw,) in conn.execute("SELECT products_json FROM chat_messages WHERE products_json IS NOT NULL"):
        try:
            counts.update(p["product_id"] for p in json.loads(raw))
        except (ValueError, KeyError, TypeError):
            continue
    return counts


def load_products(conn: sqlite3.Connection) -> list[dict]:
    stock = {r["product_id"]: r["total"] for r in conn.execute(
        "SELECT product_id, SUM(quantity) AS total FROM inventory GROUP BY product_id")}
    pop = popularity(conn)
    products = []
    for r in conn.execute("SELECT * FROM catalogue"):
        products.append({
            "product_id": r["product_id"],
            "name": r["name"],
            "garment_type": r["garment_type"],
            "style": style_of(r["garment_type"]),
            "audience": audience_of(r["name"]),
            "description": r["description"],
            "colors": json.loads(r["colors"]),
            "search_tags": json.loads(r["search_tags"]),
            "image_url": "/media/" + r["image_file_path"],
            "price": r["price"],
            "total_stock": stock.get(r["product_id"], 0),
            "popularity": pop.get(r["product_id"], 0),
        })
    return products


def by_popularity(products: list[dict]) -> list[dict]:
    return sorted(products, key=lambda p: (-p["popularity"], p["name"]))


def load_inventory(conn: sqlite3.Connection, product_id: str) -> list[dict]:
    rows = conn.execute(
        "SELECT id AS inventory_id, size, quantity FROM inventory WHERE product_id = ?", (product_id,)).fetchall()
    rank = {s: i for i, s in enumerate(SIZE_ORDER)}
    sizes = sorted((dict(r) for r in rows), key=lambda r: rank.get(r["size"], len(SIZE_ORDER)))
    for s in sizes:
        s["in_stock"] = s["quantity"] > 0
    return sizes


def find_product(conn: sqlite3.Connection, product_id: str) -> dict | None:
    return next((p for p in load_products(conn) if p["product_id"] == product_id), None)


def to_card(p: dict) -> ProductCard:
    return ProductCard(
        product_id=p["product_id"], name=p["name"], price=p["price"], image_url=p["image_url"],
        description=p["description"], in_stock=p["total_stock"] > 0,
    )


def cards_for(product_ids: list[str]) -> list[ProductCard]:
    """Look up product cards by ID, keeping order and silently dropping unknown IDs."""
    with connect() as conn:
        by_id = {p["product_id"]: p for p in load_products(conn)}
    seen: set[str] = set()
    cards = []
    for pid in product_ids:
        if pid in by_id and pid not in seen:
            seen.add(pid)
            cards.append(to_card(by_id[pid]))
    return cards


# ---------------------------------------------------------------------------
# Agent tools
# ---------------------------------------------------------------------------

@dataclass
class ShopDeps:
    """Per-request context for the agent: who the shopper is and what page they're on."""
    # Customer fields, set only when the shopper is logged in (from the users table).
    user_id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    discount_percent: int = 0  # set once the shopper has applied their promo code
    manager: bool = False  # True when the manager model is answering this request
    # Page context, sent by the front end and checked against the catalogue.
    page_path: str = "/"
    viewing_product_id: str | None = None
    viewing_product_name: str | None = None
    # Product IDs the tools actually returned this turn. Only these may be shown as cards.
    seen_product_ids: set[str] = field(default_factory=set)


def search_products(
    ctx: RunContext[ShopDeps],
    query: str = "",
    style: str | None = None,
    audience: str | None = None,
    max_price: float | None = None,
    in_stock_only: bool = False,
    size: str | None = None,
) -> list[ProductCard]:
    """Search the Campus Customs catalogue.

    Args:
        query: Words to match against name, description, colors and tags, e.g. "hockey", "Saybrook", "gray".
            Every word must match. Leave empty to browse.
        style: One of quarter-zips, jackets-fleece, hoodies, t-shirts, long-sleeve, crewnecks.
        audience: mens or womens (both include unisex items), or unisex.
        max_price: Only items at or below this price in USD.
        in_stock_only: Only items with at least one size in stock.
        size: Only items with this size (XS, S, M, L, XL, XXL) in stock. Use this instead of checking
            stock item by item when the shopper names a size.

    Returns up to 12 matches, most popular first, with exact price and whether any size is in stock.
    """
    with connect() as conn:
        items = load_products(conn)
    if style:
        items = [p for p in items if p["style"] == style]
    if audience in ("mens", "womens"):
        items = [p for p in items if p["audience"] in (audience, "unisex")]
    elif audience == "unisex":
        items = [p for p in items if p["audience"] == "unisex"]
    if max_price is not None:
        items = [p for p in items if p["price"] <= max_price]
    if in_stock_only:
        items = [p for p in items if p["total_stock"] > 0]
    if size:
        with connect() as conn:
            have = {r["product_id"] for r in conn.execute(
                "SELECT product_id FROM inventory WHERE size = ? AND quantity > 0", (size.strip().upper(),))}
        items = [p for p in items if p["product_id"] in have]
    for word in query.lower().split():
        items = [p for p in items if word in " ".join(
            [p["name"], p["garment_type"], p["description"], *p["colors"], *p["search_tags"]]).lower()]
    results = [to_card(p) for p in by_popularity(items)[:MAX_SEARCH_RESULTS]]
    # Short descriptions keep each step cheap; page cards are rebuilt from the database in full.
    for card in results:
        if len(card.description) > SEARCH_DESCRIPTION_CHARS:
            card.description = card.description[:SEARCH_DESCRIPTION_CHARS].rsplit(" ", 1)[0] + "..."
    ctx.deps.seen_product_ids.update(c.product_id for c in results)
    return results


def get_product_info(ctx: RunContext[ShopDeps], product_id: str) -> ProductInfo | str:
    """Get one product's description, garment type, colors and exact price from the database.

    Use this whenever the shopper asks what an item is like or how much it costs.

    Args:
        product_id: The product_id from a search result.
    """
    with connect() as conn:
        product = find_product(conn, product_id)
    if product is None:
        return f"No product with id {product_id!r}. Search the catalogue to find the right id."
    ctx.deps.seen_product_ids.add(product_id)
    return ProductInfo(**to_card(product).model_dump(), garment_type=product["garment_type"], colors=product["colors"])


def check_stock(ctx: RunContext[ShopDeps], product_id: str, size: str | None = None) -> StockReport | str:
    """Get exact stock from the inventory table: quantity for each size, or for one size if given.

    Use this for every question about availability, sizes or how many are left.

    Args:
        product_id: The product_id from a search result.
        size: One of XS, S, M, L, XL, XXL. Leave empty to get every size.
    """
    with connect() as conn:
        product = find_product(conn, product_id)
        if product is None:
            return f"No product with id {product_id!r}. Search the catalogue to find the right id."
        all_sizes = [SizeStock(**s) for s in load_inventory(conn, product_id)]
    ctx.deps.seen_product_ids.add(product_id)
    wanted = size.strip().upper() if size else None
    sizes, note = all_sizes, None
    if wanted:
        sizes = [s for s in all_sizes if s.size == wanted]
        if not sizes:
            sizes = all_sizes
            note = f"This product doesn't come in size {wanted}. Showing every size instead."
    return StockReport(
        product_id=product_id, name=product["name"], price=product["price"], requested_size=wanted,
        sizes=sizes, total_in_stock=sum(s.quantity for s in all_sizes), note=note,
    )


def compare_products(
    ctx: RunContext[ShopDeps], product_ids: list[str], size: str | None = None,
) -> list[ProductComparison]:
    """Compare up to 8 products side by side to choose the best one for the shopper.

    Returns, for each: exact price, shopper interest (popularity), total stock, sizes in stock and,
    if a size is given, units left in that size. Use it when the shopper asks for the best or a recommendation.

    Args:
        product_ids: product_ids from search results (up to 8).
        size: The shopper's size (XS, S, M, L, XL, XXL), if they gave one.
    """
    wanted = size.strip().upper() if size else None
    results = []
    with connect() as conn:
        by_id = {p["product_id"]: p for p in load_products(conn)}
        for pid in product_ids[:8]:
            p = by_id.get(pid)
            if p is None:
                continue
            sizes = load_inventory(conn, pid)
            results.append(ProductComparison(
                product_id=pid, name=p["name"], price=p["price"], shopper_interest=p["popularity"],
                total_stock=p["total_stock"], sizes_in_stock=[s["size"] for s in sizes if s["quantity"] > 0],
                requested_size_quantity=next((s["quantity"] for s in sizes if s["size"] == wanted), 0) if wanted else None,
            ))
            ctx.deps.seen_product_ids.add(pid)
    return results


def get_my_account(ctx: RunContext[ShopDeps]) -> AccountInfo | str:
    """Get the logged-in shopper's own name and email, to address them or confirm which account they're on.

    Only ever returns the current shopper's account. Returns a message if nobody is logged in.
    """
    if ctx.deps.user_id is None:
        return "The shopper is not logged in."
    with connect() as conn:
        row = conn.execute(
            "SELECT id, name, first_name, last_name, email FROM users WHERE id = ?", (ctx.deps.user_id,)).fetchone()
    if row is None:
        return "The shopper is not logged in."
    first, last = row["first_name"], row["last_name"]
    if not first:
        first, _, last = row["name"].partition(" ")
    return AccountInfo(user_id=row["id"], first_name=first, last_name=last or "", email=row["email"])


def verify_account_email(ctx: RunContext[ShopDeps], email: str) -> EmailCheck | str:
    """Check whether an email the shopper gives matches the account they're logged in to.

    Only says yes or no. Never use this to look up or reveal other accounts.

    Args:
        email: The email address the shopper typed.
    """
    if ctx.deps.user_id is None:
        return "The shopper is not logged in, so there is no account to verify."
    with connect() as conn:
        row = conn.execute("SELECT email FROM users WHERE id = ?", (ctx.deps.user_id,)).fetchone()
    return EmailCheck(matches=bool(row) and row["email"].lower() == email.strip().lower())


def list_styles(ctx: RunContext[ShopDeps]) -> list[dict]:
    """List the clothing styles the store carries, with how many products are in each."""
    with connect() as conn:
        counts = Counter(p["style"] for p in load_products(conn))
    return [{"style": key, "label": label, "products": counts.get(key, 0)} for key, label, _ in STYLES]


def get_my_promo_code(ctx: RunContext[ShopDeps]) -> PromoCode | str:
    """Get the logged-in shopper's own 10% off promo code and whether it has been used.

    Only ever returns the current shopper's code. Guests are told to create an account to get one.
    """
    if ctx.deps.user_id is None:
        return "The shopper is not logged in. Registered shoppers get a personal 10% off code; they can create an account."
    return generate_promo_code(ctx.deps.user_id)


AGENT_TOOLS = [
    search_products, get_product_info, check_stock, compare_products, list_styles, get_my_account,
    verify_account_email, get_my_promo_code,
]
