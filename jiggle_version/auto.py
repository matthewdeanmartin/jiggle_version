# jiggle_version/auto.py
"""
Implements the logic for the 'auto' increment feature.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import tomlkit

from .gitignore import (
    collect_default_spec,
    is_path_explicitly_ignored,
    is_path_gitignored,
)
from .parsers.ast_parser import parse_dunder_all


def get_current_symbols(
    project_root: Path, ignore_paths: list[str] | None = None
) -> set[str]:
    """Discovers and parses all __all__ symbols in a project.

    Walks every *.py under project_root, honoring .gitignore and user-specified ignores.
    """
    symbols: set[str] = set()

    # Build ignore spec once; normalize explicit ignores to absolute paths.
    spec = collect_default_spec(project_root)
    explicit_ignores = {(project_root / p).resolve() for p in (ignore_paths or [])}

    for py_file in project_root.rglob("*.py"):
        # Respect .gitignore and explicit ignore paths.
        if is_path_gitignored(py_file, project_root, spec):
            continue
        if is_path_explicitly_ignored(py_file, explicit_ignores):
            continue

        symbols.update(parse_dunder_all(py_file))

    return symbols


def read_digest_data(digest_path: Path) -> dict[str, Any]:
    """Reads the stored digest data from the config file."""
    if not digest_path.is_file():
        return {}
    return tomlkit.parse(digest_path.read_text(encoding="utf-8"))


def write_digest_data(digest_path: Path, symbols: set[str]) -> None:
    """Writes the current symbols to the digest file."""
    sorted_symbols = sorted(list(symbols))

    # Per the PEP, we store the symbols themselves to allow for comparison.
    # A composite digest is also stored for quick checks.
    sha256 = hashlib.sha256("".join(sorted_symbols).encode("utf-8")).hexdigest()

    doc = tomlkit.document()
    doc.add("digest", f"sha256:{sha256}")  # type: ignore[arg-type]
    doc.add("symbols", sorted_symbols)  # type: ignore[arg-type]

    digest_path.write_text(tomlkit.dumps(doc), encoding="utf-8")


def determine_auto_increment(
    project_root: Path, digest_path: Path, ignore_paths: list[str] | None = None
) -> str:
    """
    Determines the increment by comparing current and stored __all__ symbols.
    """
    current_symbols = get_current_symbols(project_root, ignore_paths)
    digest_data = read_digest_data(digest_path)
    stored_symbols = set(digest_data.get("symbols", []))

    if not stored_symbols and not current_symbols:
        print("Auto-increment: No public API (`__all__`) found. Defaulting to 'patch'.")
        return "patch"

    removed_symbols = stored_symbols - current_symbols
    added_symbols = current_symbols - stored_symbols

    if removed_symbols:
        print(
            f"Auto-increment: Detected breaking change (removed: {', '.join(sorted(removed_symbols))}). Bumping 'major'."
        )
        return "major"

    if added_symbols:
        print(
            f"Auto-increment: Detected new features (added: {', '.join(sorted(added_symbols))}). Bumping 'minor'."
        )
        return "minor"

    print("Auto-increment: No public API changes detected. Bumping 'patch'.")
    return "patch"
