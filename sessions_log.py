"""Session event logging.

One logger writes to *two* rotating-free files so the same event is available
both as machine-parseable key=value lines and as human-friendly prose:

* ``events.log``   - structured: ``time=... event=... field=value ...``
* ``session.log``  - plaintext:  ``[local time] message (field=value, ...)``

Both files are append-only and never truncated. Paths come from the
config.yaml ``logging`` section (``event_log`` / ``plain_log``) and default
to the program's ``logs/`` folder (next to the repo in dev, beside the .exe
when frozen). Runtime logs are gitignored, so nothing sensitive is committed.
"""

import logging
from datetime import datetime
from pathlib import Path

from config import log_path_for  # resolves config-configured log file paths

logger = logging.getLogger("timer")
logger.setLevel(logging.INFO)
logger.propagate = False

_configured = False


def _local_now():
    """Current local time as an ISO-8601 string with the UTC offset."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


class StructuredFormatter(logging.Formatter):
    """Renders a record as ``time=... event=... key=value ...`` on one line."""

    def format(self, record):
        fields = getattr(record, "fields", {})
        parts = [f"time={_local_now()}", f"event={record.event}"]
        parts += [f"{k}={v}" for k, v in fields.items()]
        return " ".join(parts)


class PlainFormatter(logging.Formatter):
    """Renders a record as ``[local time] message (key=value, ...)``."""

    def format(self, record):
        line = f"[{_local_now()}] {record.getMessage()}"
        fields = getattr(record, "fields", {})
        if fields:
            line += " (" + ", ".join(f"{k}={v}" for k, v in fields.items()) + ")"
        return line


def _ensure_configured():
    global _configured
    if _configured:
        return

    event_path = log_path_for("event_log", "events.log")
    plain_path = log_path_for("plain_log", "session.log")
    event_path.parent.mkdir(parents=True, exist_ok=True)
    plain_path.parent.mkdir(parents=True, exist_ok=True)

    event_handler = logging.FileHandler(event_path, encoding="utf-8", mode="a")
    event_handler.setFormatter(StructuredFormatter())
    plain_handler = logging.FileHandler(plain_path, encoding="utf-8", mode="a")
    plain_handler.setFormatter(PlainFormatter())

    logger.addHandler(event_handler)
    logger.addHandler(plain_handler)
    _configured = True


def _flush():
    """Push buffered log lines to disk. Safe to call any time."""
    for handler in logger.handlers:
        try:
            handler.flush()
        except Exception:
            pass


def log_event(event: str, message: str, **fields) -> None:
    """Record one session event to both log files.

    ``event`` is the machine-readable name (e.g. ``session_start``);
    ``message`` is a short human sentence for the plaintext log; ``fields``
    are extra key=value pairs included in both formats.

    Every write is flushed immediately so a long-running program that is
    killed (or crashes) never loses recent events from the buffer.
    """
    _ensure_configured()
    logger.info(message, extra={"event": event, "fields": fields})
    _flush()


def flush() -> None:
    """Flush any buffered log output to disk."""
    _ensure_configured()
    _flush()


def close() -> None:
    """Flush and close both log files. Call once during shutdown."""
    _ensure_configured()
    for handler in logger.handlers:
        try:
            handler.flush()
            handler.close()
        except Exception:
            pass
        logger.removeHandler(handler)
