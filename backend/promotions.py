"""Promo codes: one unique, single-use 10% off code per registered user.

Codes live in their own database (data/promotions.db) so the original campus_customs.db
tables stay unchanged. The database and table are created automatically on first use.
"""

from __future__ import annotations

import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from models import PromoCode, PromoRedeemResult

ROOT = Path(__file__).resolve().parent.parent
PROMO_DB_PATH = Path(os.getenv("PROMO_DB_PATH", ROOT / "data" / "promotions.db"))
DISCOUNT_PERCENT = 10
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no 0/O or 1/I, easy to read

_SCHEMA = """
CREATE TABLE IF NOT EXISTS promo_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,          -- users.id in campus_customs.db; one code per user
    code TEXT NOT NULL UNIQUE,
    discount_percent INTEGER NOT NULL DEFAULT 10,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    used_at TEXT                              -- NULL until the code is redeemed
)
"""


def _connect() -> sqlite3.Connection:
    PROMO_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(PROMO_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(_SCHEMA)
    return conn


def _new_code() -> str:
    part = lambda: "".join(secrets.choice(CODE_ALPHABET) for _ in range(4))
    return f"CC{DISCOUNT_PERCENT}-{part()}-{part()}"


def _to_model(row: sqlite3.Row) -> PromoCode:
    return PromoCode(code=row["code"], discount_percent=row["discount_percent"],
                     created_at=row["created_at"], used=row["used_at"] is not None, used_at=row["used_at"])


def generate_promo_code(user_id: int) -> PromoCode:
    """Tool 1 (generation): return the user's code, creating a unique random one the first time."""
    with _connect() as conn:
        row = conn.execute("SELECT * FROM promo_codes WHERE user_id = ?", (user_id,)).fetchone()
        while row is None:
            try:
                conn.execute("INSERT INTO promo_codes (user_id, code, discount_percent) VALUES (?, ?, ?)",
                             (user_id, _new_code(), DISCOUNT_PERCENT))
            except sqlite3.IntegrityError:
                pass  # code collision (or another request created it first); look again and retry
            row = conn.execute("SELECT * FROM promo_codes WHERE user_id = ?", (user_id,)).fetchone()
        return _to_model(row)


def applied_discount(user_id: int) -> int:
    """Percent off the shopper's prices: their code's discount once it has been applied, else 0."""
    with _connect() as conn:
        row = conn.execute("SELECT discount_percent, used_at FROM promo_codes WHERE user_id = ?", (user_id,)).fetchone()
    return row["discount_percent"] if row and row["used_at"] else 0


def redeem_promo_code(user_id: int, code: str) -> PromoRedeemResult:
    """Tool 2 (one use only): mark the user's own code as used. A second use is refused."""
    code = code.strip().upper()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with _connect() as conn:
        # Check and mark in one statement, so two simultaneous attempts can't both succeed.
        cur = conn.execute(
            "UPDATE promo_codes SET used_at = ? WHERE user_id = ? AND code = ? AND used_at IS NULL",
            (now, user_id, code))
        if cur.rowcount == 1:
            return PromoRedeemResult(ok=True, message=f"Code applied: {DISCOUNT_PERCENT}% off your order.",
                                     discount_percent=DISCOUNT_PERCENT)
        row = conn.execute("SELECT used_at FROM promo_codes WHERE user_id = ? AND code = ?", (user_id, code)).fetchone()
    if row is None:
        return PromoRedeemResult(ok=False, message="That code isn't valid for your account.")
    return PromoRedeemResult(ok=False, message=f"This code was already used on {row['used_at'][:10]}.")
