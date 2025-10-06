# tests/test_discover_integration.py
from __future__ import annotations

from pathlib import Path

from jiggle_version.discover import find_source_files


def write(p: Path, text: str = "") -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def test_respects_gitignore_and_finds_targets(tmp_path: Path):
    root = tmp_path
    # gitignore excludes build/ and any *.tmp
    write(root / ".gitignore", "build/\n*.tmp\n")
    # Create typical version sources
    write(root / "pyproject.toml", '[project]\nversion = "0.1.0"\n')
    write(root / "setup.cfg", "[metadata]\nversion = 0.1.0\n")
    write(root / "setup.py", "from setuptools import setup\nsetup(version='0.1.0')\n")
    write(root / "pkg" / "__init__.py", "")
    write(root / "pkg" / "__version__.py", "__version__='0.1.0'")
    write(root / "pkg" / "_version.py", "__version__='0.1.0'")
    write(root / "other" / "__about__.py", "__version__='0.1.0'")
    # Ignored stuff
    write(root / "build" / "__version__.py", "__version__='bad'")
    write(root / "notes.tmp", "ignore me")

    files = find_source_files(root)

    # Should include root statics + recursive files outside ignored dirs
    names = {p.relative_to(root).as_posix() for p in files}
    assert "pyproject.toml" in names
    assert "setup.cfg" in names
    assert "setup.py" in names
    assert "pkg/__init__.py" in names
    assert "pkg/__version__.py" in names
    assert "pkg/_version.py" in names
    assert "other/__about__.py" in names

    # Should exclude ignored paths
    assert "build/__version__.py" not in names
    assert "notes.tmp" not in names


def test_explicit_ignore_paths_override(tmp_path: Path):
    root = tmp_path
    write(root / "pkg" / "__init__.py", "")
    write(root / "pkg" / "__version__.py", "__version__='0.1.0'")
    files = find_source_files(root, ignore_paths=["pkg"])
    names = {p.relative_to(root).as_posix() for p in files}
    assert not any(n.startswith("pkg/") for n in names)
