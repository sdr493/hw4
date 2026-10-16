"""Append-only audit trail of agent loop activity: output/audit_trail.json.

The file is one JSON array that only ever grows. New entries are added at the end; existing
entries are never rewritten or deleted, and the file is never wiped between runs or restarts.
"""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
AUDIT_PATH = Path(os.getenv("AUDIT_PATH", ROOT / "output" / "audit_trail.json"))
MAX_TEXT = 160  # keep args/results short

_lock = threading.Lock()


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def short(value: Any, limit: int = MAX_TEXT) -> str:
    """Compact one-line text for the log."""
    if not isinstance(value, str):
        try:
            value = json.dumps(value, default=str, ensure_ascii=False)
        except (TypeError, ValueError):
            value = str(value)
    value = " ".join(value.split())
    return value if len(value) <= limit else value[: limit - 3] + "..."


def append(entry: dict) -> None:
    """Add one entry to the end of the JSON array without touching earlier entries."""
    line = json.dumps(entry, ensure_ascii=False)
    with _lock:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not AUDIT_PATH.exists() or AUDIT_PATH.stat().st_size == 0:
            AUDIT_PATH.write_text(f"[\n{line}\n]\n", encoding="utf-8")
            return
        with open(AUDIT_PATH, "r+b") as f:
            # Find the closing "]" and write the new entry in its place, then close the array again.
            f.seek(0, os.SEEK_END)
            pos = f.tell()
            while pos > 0:
                pos -= 1
                f.seek(pos)
                if f.read(1) == b"]":
                    break
            else:
                raise RuntimeError(f"{AUDIT_PATH} is not a JSON array; refusing to overwrite it")
            # Is the array still empty ("[ ]")? Then the new entry needs no leading comma.
            prev = pos
            while prev > 0:
                prev -= 1
                f.seek(prev)
                ch = f.read(1)
                if not ch.isspace():
                    break
            separator = "\n" if ch == b"[" else ",\n"
            f.seek(pos)
            f.truncate()
            f.write(f"{separator}{line}\n]\n".encode("utf-8"))


def log(request_id: str, event: str, **fields: Any) -> None:
    append({"time": now(), "request_id": request_id, "event": event, **fields})
