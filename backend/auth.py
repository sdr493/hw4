"""Account sign-up and log-in for Campus Customs.

Passwords use PBKDF2-HMAC-SHA256 with 120,000 iterations and are stored as
pbkdf2_sha256$<salt>$<hex digest>. Sign-up and log-in share hash_password(), so both
always use the same function, salt handling and iteration count.
"""

import hashlib
import hmac
import re
import secrets
import sqlite3
from dataclasses import dataclass

from fastapi import APIRouter, Cookie, HTTPException, Response
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 120_000
SALT_BYTES = 8  # 16 hex characters, matching the seeded accounts
MIN_PASSWORD_LENGTH = 8
SESSION_COOKIE = "cc_session"

router = APIRouter(prefix="/api/auth", tags=["auth"])


def hash_password(password: str, salt: str) -> str:
    """Hash a password with the given salt. The salt is used as its UTF-8 text."""
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), ITERATIONS)
    return f"{ALGORITHM}${salt}${digest.hex()}"


def new_password_hash(password: str) -> str:
    """Sign-up only: create a fresh random salt, then hash."""
    return hash_password(password, secrets.token_hex(SALT_BYTES))


def verify_password(password: str, stored: str) -> bool:
    """Log-in: never un-hash. Read the salt from the stored value, re-hash what was typed, compare."""
    try:
        algorithm, salt, _ = stored.split("$")
    except ValueError:
        return False
    if algorithm != ALGORITHM:
        return False
    return hmac.compare_digest(hash_password(password, salt), stored)


# A dummy hash so a log-in for an unknown email takes as long as one for a real email.
_DUMMY_HASH = new_password_hash(secrets.token_hex(16))


@dataclass
class Session:
    user_id: int


# Sessions live in memory: restarting the backend logs everyone out.
_sessions: dict[str, Session] = {}


class SignupRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=60)
    last_name: str = Field(min_length=1, max_length=60)
    email: EmailStr
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=128)
    confirm_password: str

    @field_validator("first_name", "last_name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        v = re.sub(r"\s+", " ", v).strip()
        if not v:
            raise ValueError("Name cannot be blank")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "SignupRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


def _user_out(row: sqlite3.Row) -> UserOut:
    first, last = row["first_name"], row["last_name"]
    if not first:
        first, _, last = row["name"].partition(" ")
    return UserOut(id=row["id"], first_name=first, last_name=last or "", email=row["email"])


def session_user_id(token: str | None) -> int | None:
    """The logged-in user's id for a session cookie, or None."""
    session = _sessions.get(token or "")
    return session.user_id if session else None


def _start_session(response: Response, user_id: int) -> None:
    token = secrets.token_urlsafe(32)
    _sessions[token] = Session(user_id=user_id)
    response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax", max_age=60 * 60 * 24 * 7)


def make_router(connect_rw):
    """Build the auth routes. connect_rw() must return a writable sqlite3 connection with Row factory."""

    @router.post("/signup", response_model=UserOut, status_code=201)
    def signup(body: SignupRequest, response: Response) -> UserOut:
        email = body.email.lower()
        with connect_rw() as conn:
            if conn.execute("SELECT 1 FROM users WHERE lower(email) = ?", (email,)).fetchone():
                raise HTTPException(status_code=409, detail="An account with that email already exists")
            cur = conn.execute(
                "INSERT INTO users (name, first_name, last_name, email, password_hash) VALUES (?, ?, ?, ?, ?)",
                (f"{body.first_name} {body.last_name}", body.first_name, body.last_name, email,
                 new_password_hash(body.password)),
            )
            row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
        _start_session(response, row["id"])
        return _user_out(row)

    @router.post("/login", response_model=UserOut)
    def login(body: LoginRequest, response: Response) -> UserOut:
        with connect_rw() as conn:
            row = conn.execute("SELECT * FROM users WHERE lower(email) = ?", (body.email.lower(),)).fetchone()
        stored = row["password_hash"] if row else _DUMMY_HASH
        if not verify_password(body.password, stored) or row is None:
            # Same message for unknown email and wrong password, so emails can't be probed.
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        _start_session(response, row["id"])
        return _user_out(row)

    @router.get("/me", response_model=UserOut)
    def me(cc_session: str | None = Cookie(default=None)) -> UserOut:
        session = _sessions.get(cc_session or "")
        if session is None:
            raise HTTPException(status_code=401, detail="Not logged in")
        with connect_rw() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (session.user_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=401, detail="Not logged in")
        return _user_out(row)

    @router.post("/logout", status_code=204)
    def logout(response: Response, cc_session: str | None = Cookie(default=None)) -> None:
        _sessions.pop(cc_session or "", None)
        response.delete_cookie(SESSION_COOKIE)

    return router
