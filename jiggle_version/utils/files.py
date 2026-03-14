from __future__ import annotations

import locale
import tokenize
from pathlib import Path


def read_utf8_text(path: Path) -> str:
    """Read a UTF-8 text file, tolerating an optional UTF-8 BOM."""
    return path.read_text(encoding="utf-8-sig")


def read_python_source(path: Path) -> str:
    """Read Python source using PEP 263 encoding detection."""
    with tokenize.open(path) as handle:
        return handle.read()


def decode_text_output(data: bytes | None) -> str:
    """Decode subprocess text without crashing on locale mismatches."""
    if not data:
        return ""

    for encoding in ("utf-8", locale.getpreferredencoding(False)):
        if not encoding:
            continue
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue

    return data.decode("utf-8", errors="replace")
