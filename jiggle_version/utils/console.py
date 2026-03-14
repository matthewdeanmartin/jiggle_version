from __future__ import annotations

import io
import sys
from typing import TextIO


def _reconfigure_stream(stream: TextIO, *, prefer_utf8: bool) -> None:
    """Best-effort hardening for text streams used by the CLI.

    We prefer UTF-8 to maximize Unicode compatibility, but always fall back to a
    non-crashing error handler so status glyphs and emojis never raise an
    encoding exception on narrow consoles.
    """
    reconfigure = getattr(stream, "reconfigure", None)
    if not callable(reconfigure):
        return

    target_encoding = "utf-8" if prefer_utf8 else None
    try:
        if target_encoding:
            reconfigure(encoding=target_encoding, errors="backslashreplace")
        else:
            reconfigure(errors="backslashreplace")
        return
    except (LookupError, TypeError, ValueError, io.UnsupportedOperation):
        pass

    try:
        reconfigure(errors="backslashreplace")
    except (LookupError, TypeError, ValueError, io.UnsupportedOperation):
        pass


def harden_standard_streams() -> None:
    """Make stdout/stderr resilient to Unicode output on hostile consoles."""
    _reconfigure_stream(sys.stdout, prefer_utf8=True)
    _reconfigure_stream(sys.stderr, prefer_utf8=True)
