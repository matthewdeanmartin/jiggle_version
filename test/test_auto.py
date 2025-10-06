from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from jiggle_version.auto import (
    determine_auto_increment,
    get_current_symbols,
    read_digest_data,
    write_digest_data,
)


def w(p: Path, text: str = "") -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


# ---------- get_current_symbols ----------


def test_get_current_symbols_collects_all_from_python_sources(tmp_path: Path):
    root = tmp_path
    # package with __all__
    w(root / "pkg" / "__init__.py", "__all__ = ['A', 'B']")
    # submodule also contributes
    w(root / "pkg" / "mod.py", "__all__ = ('C',)")
    # a non-python target that discover might find; should be ignored by get_current_symbols
    w(root / "pyproject.toml", "[project]\nname='x'\nversion='0.1.0'\n")

    symbols = get_current_symbols(root)
    assert symbols == {"A", "B", "C"}


def test_get_current_symbols_respects_ignore_paths(tmp_path: Path):
    root = tmp_path
    w(root / "pkg" / "__init__.py", "__all__ = ['A']")
    w(root / "pkg" / "mod.py", "__all__ = ['B']")
    # ignored folder
    symbols = get_current_symbols(root, ignore_paths=["pkg"])
    assert symbols == set()


# ---------- read / write digest ----------


def test_read_digest_data_missing_returns_empty(tmp_path: Path):
    assert read_digest_data(tmp_path / "digest.toml") == {}


def test_write_and_read_digest_roundtrip(tmp_path: Path):
    digest = tmp_path / "digest.toml"
    symbols = {"beta", "alpha"}
    write_digest_data(digest, symbols)

    data = read_digest_data(digest)
    # symbols preserved as sorted list
    assert data["symbols"] == ["alpha", "beta"]
    # digest format and correctness
    assert isinstance(data["digest"], str) and data["digest"].startswith("sha256:")
    expected = hashlib.sha256("".join(sorted(symbols)).encode("utf-8")).hexdigest()
    assert data["digest"] == f"sha256:{expected}"


# ---------- determine_auto_increment ----------


def test_auto_increment_defaults_to_patch_when_no_api_and_no_digest(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    root = tmp_path
    decision = determine_auto_increment(root, root / "digest.toml")
    assert decision == "patch"
    out = capsys.readouterr().out
    assert "Defaulting to 'patch'" in out


def test_auto_increment_major_on_removed_symbols(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    root = tmp_path
    # Initial API has A,B
    initial_symbols = {"A", "B"}
    digest_path = root / "digest.toml"
    write_digest_data(digest_path, initial_symbols)
    # Current tree only has A (B removed -> breaking)
    w(root / "pkg" / "__init__.py", "__all__ = ['A']")

    decision = determine_auto_increment(root, digest_path)
    assert decision == "major"
    out = capsys.readouterr().out
    assert "breaking change" in out.lower()
    assert "removed: B" in out


def test_auto_increment_minor_on_added_symbols(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    root = tmp_path
    # Stored API has A
    digest_path = root / "digest.toml"
    write_digest_data(digest_path, {"A"})
    # Current adds B
    w(root / "pkg" / "__init__.py", "__all__ = ['A', 'B']")

    decision = determine_auto_increment(root, digest_path)
    assert decision == "minor"
    out = capsys.readouterr().out
    assert "new features" in out.lower()
    assert "added: B" in out


def test_auto_increment_patch_when_no_change(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    root = tmp_path
    digest_path = root / "digest.toml"
    write_digest_data(digest_path, {"A", "B"})
    # Same current symbols (order should not matter)
    w(root / "pkg" / "__init__.py", "__all__ = ['B', 'A']")

    decision = determine_auto_increment(root, digest_path)
    assert decision == "patch"
    out = capsys.readouterr().out
    assert "no public api changes" in out.lower()
