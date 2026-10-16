"""Pydantic and PydanticAI structured types for the Campus Customs chat."""

from typing import Literal

from pydantic import BaseModel, Field

MAX_MESSAGE_CHARS = 1000
MAX_HISTORY_MESSAGES = 10
MAX_PAGE_MATCHES = 12


class ProductCard(BaseModel):
    """A product as shown on a card in the chat or on the page. Values come from the database."""
    product_id: str
    name: str
    price: float
    image_url: str
    description: str
    in_stock: bool


class SizeStock(BaseModel):
    """One inventory row: a product in one size. Read from the inventory table."""
    inventory_id: int = Field(description="inventory.id")
    size: str
    quantity: int
    in_stock: bool


class ProductInfo(ProductCard):
    """Tool result: a product's description and exact price."""
    garment_type: str
    colors: list[str]


class StockReport(BaseModel):
    """Tool result: how many of a product are in stock, by size."""
    product_id: str
    name: str
    price: float
    requested_size: str | None = Field(default=None, description="The size asked about, if any.")
    sizes: list[SizeStock] = Field(description="Stock for the requested size, or every size if none was asked.")
    total_in_stock: int = Field(description="Units across all sizes.")
    note: str | None = Field(default=None, description="Set when the requested size doesn't exist for this product.")


class ProductComparison(BaseModel):
    """Tool result: the facts used to pick the best product. All values come from the database."""
    product_id: str
    name: str
    price: float
    shopper_interest: int = Field(description="How many times this product has been shown to shoppers in chat (popularity).")
    total_stock: int
    sizes_in_stock: list[str]
    requested_size_quantity: int | None = Field(default=None, description="Units in the requested size, if a size was given.")


class AccountInfo(BaseModel):
    """Tool result: the logged-in shopper's own account. Never includes the password hash."""
    user_id: int
    first_name: str
    last_name: str
    email: str


class EmailCheck(BaseModel):
    """Tool result: whether an email matches the logged-in shopper's account."""
    matches: bool


class AgentOutput(BaseModel):
    """What the agent returns each turn (structured, not free text)."""
    reply: str = Field(description="The answer to the shopper, in the Campus Customs voice. Plain text or light markdown.")
    product_ids: list[str] = Field(
        default_factory=list,
        max_length=MAX_PAGE_MATCHES,
        description="Matching products to show on the page as cards, best match first. Only IDs returned by tools this turn.",
    )
    results_title: str | None = Field(
        default=None,
        max_length=60,
        description='Short heading for the matches shown on the page, e.g. "Navy hoodies" or "Saybrook gear under $60".',
    )


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)


class PageContext(BaseModel):
    """Where the shopper is on the site when they send a message."""
    path: str = Field(default="/", max_length=200, description='Current page path, e.g. "/products/basic-hoodie-big-yale".')
    product_id: str | None = Field(default=None, max_length=120, description="Set when the shopper is on a single item page.")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)
    # Guests send this visit's messages from the browser (never saved). Logged-in history comes from the database.
    history: list[ChatTurn] = Field(default_factory=list, max_length=50)
    page: PageContext | None = None


class ChatReply(BaseModel):
    """API contract for POST /api/chat. The front end renders `products` as cards on the page."""
    reply: str
    products: list[ProductCard] = Field(
        default_factory=list, description="Structured product matches, re-read from the database. Empty = leave the page as is.")
    results_title: str | None = Field(default=None, description="Heading for the matches on the page.")
    stopped: bool = Field(default=False, description="True when a stopping rule ended the turn early.")
    manager: bool = Field(default=False, description="True when the stronger manager model answered this request.")


class ChatHistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    products: list[ProductCard] = Field(default_factory=list)


class PromoCode(BaseModel):
    """A shopper's personal single-use promo code (stored in data/promotions.db)."""
    code: str
    discount_percent: int
    created_at: str
    used: bool
    used_at: str | None = None


class PromoRedeemRequest(BaseModel):
    code: str = Field(min_length=4, max_length=32)


class PromoRedeemResult(BaseModel):
    ok: bool
    message: str
    discount_percent: int | None = None


class Bootstrap(BaseModel):
    """Everything the store pages need, loaded once when the site opens."""
    products: list[dict]
    filters: dict
    popular_ids: list[str]
