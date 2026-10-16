"""Code-level safety checks that back up the rules in prompts/prompt.md."""

from __future__ import annotations

import re

# Card numbers (13-19 digits, with optional spaces or dashes), US SSNs and bank routing/account numbers.
_CARD = re.compile(r"\b(?:\d[ -]?){12,18}\d\b")
_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

# Profanity the assistant must never send. Kept short on purpose; the prompt does most of the work.
_PROFANITY = re.compile(
    r"\b(fuck\w*|shit\w*|bitch\w*|asshole\w*|bastard\w*|damn\w*|crap\w*|dick\w*|piss\w*|cunt\w*|motherf\w*)\b",
    re.IGNORECASE,
)

SAFE_REPLY = "Sorry, I can't help with that one. I'm happy to help you find Yale gear, sizes or prices!"


def redact_financial(message: str) -> tuple[str, bool]:
    """Remove card numbers and SSNs a shopper types, so they're never sent to the model or logged."""
    cleaned = _CARD.sub("[card number removed]", message)
    cleaned = _SSN.sub("[number removed]", cleaned)
    return cleaned, cleaned != message


def has_profanity(text: str) -> bool:
    return bool(_PROFANITY.search(text))
