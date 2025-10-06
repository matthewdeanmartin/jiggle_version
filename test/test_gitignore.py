from __future__ import annotations

from pathlib import Path

import pytest

from jiggle_version.gitignore import (
    build_gitignore_spec,
    collect_default_spec,
    is_path_explicitly_ignored,
    is_path_gitignored,
)

# ----------------------------- helpers -----------------------------


def write(p: Path, text: str) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


# ----------------------------- build / collect -----------------------------


def test_collect_default_spec_reads_root_gitignore_and_exclude(tmp_path: Path):
    root = tmp_path
    write(root / ".gitignore", "build/\n*.log\n!keep.log\n")
    write(root / ".git/info/exclude", "dist/\n")

    spec = collect_default_spec(root)

    # Files under build/ and dist/ ignored; negation for keep.log works
    assert is_path_gitignored(root / "build" / "x.txt", root, spec)
    assert is_path_gitignored(root / "dist" / "y.txt", root, spec)
    assert is_path_gitignored(root / "output.log", root, spec)
    assert not is_path_gitignored(root / "keep.log", root, spec)


def test_build_gitignore_spec_extra_patterns_override_with_negation(tmp_path: Path):
    root = tmp_path
    write(root / ".gitignore", "vendor/\n*.tmp\n")

    # Extra patterns add a negation to re-include a specific file
    spec = build_gitignore_spec(root, extra_patterns=["!README.tmp"])

    assert is_path_gitignored(root / "vendor" / "lib.a", root, spec)
    assert is_path_gitignored(root / "notes.tmp", root, spec)
    assert not is_path_gitignored(root / "README.tmp", root, spec)


# ----------------------------- semantics -----------------------------


def test_directory_suffix_only_matches_directory(tmp_path: Path):
    root = tmp_path
    write(root / ".gitignore", "cache/\n")
    spec = collect_default_spec(root)

    # Directory tree under cache/ ignored
    assert is_path_gitignored(root / "cache" / "a" / "b.txt", root, spec)

    # But a file literally named "cache" at project root is NOT a directory; not ignored by the trailing slash rule
    write(root / "cache", "not a dir")
    assert not is_path_gitignored(root / "cache", root, spec)


def test_wildcards_and_anchoring(tmp_path: Path):
    root = tmp_path
    # Leading slash anchors to project root; recursive glob for *.pyc anywhere
    write(root / ".gitignore", "/secrets.env\n**/*.pyc\n")
    spec = collect_default_spec(root)

    assert is_path_gitignored(root / "secrets.env", root, spec)
    assert not is_path_gitignored(root / "sub" / "secrets.env", root, spec)
    assert is_path_gitignored(
        root / "pkg" / "__pycache__" / "m.cpython-311.pyc", root, spec
    )


def test_negation_last_rule_wins(tmp_path: Path):
    root = tmp_path
    # Ignore all .env, but re-include one file later
    write(root / ".gitignore", "*.env\n!allow.env\n")
    spec = collect_default_spec(root)

    assert is_path_gitignored(root / "x.env", root, spec)
    assert not is_path_gitignored(root / "allow.env", root, spec)


def test_global_ignore_files(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    # Simulate a home directory with a global ignore
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    write(fake_home / ".config" / "git" / "ignore", "*.DS_Store\nthumbs.db\n")

    # Monkeypatch Path.home() to our fake home
    monkeypatch.setattr(Path, "home", lambda: fake_home)

    root = tmp_path / "repo"
    root.mkdir()
    spec = collect_default_spec(root)

    assert is_path_gitignored(root / "foo.DS_Store", root, spec)
    assert is_path_gitignored(root / "thumbs.db", root, spec)


def test_windows_like_paths_normalize_to_posix(tmp_path: Path):
    # We can't fabricate OS path separators, but we can ensure nested subpaths
    # resolve and match using as_posix() conversion.
    root = tmp_path
    write(root / ".gitignore", "logs/**\n!logs/keep/\n")
    spec = collect_default_spec(root)

    # Deep path ignored
    p = root / "logs" / "2025" / "10" / "run.txt"
    assert is_path_gitignored(p, root, spec)

    # Re-include subtree via negation
    q = root / "logs" / "keep" / "run.txt"
    assert not is_path_gitignored(q, root, spec)


# ----------------------------- explicit absolute ignores -----------------------------


def test_is_path_explicitly_ignored_exact_and_descendant(tmp_path: Path):
    root = tmp_path
    a = root / "data"
    b = a / "sub" / "file.txt"
    a.mkdir(parents=True)
    write(b, "x")

    ignored = {a.resolve()}

    assert is_path_explicitly_ignored(a, ignored)
    assert is_path_explicitly_ignored(b, ignored)
    assert not is_path_explicitly_ignored(root / "other" / "file.txt", ignored)


# ----------------------------- defensive -----------------------------


def test_empty_patterns_mean_not_ignored(tmp_path: Path):
    root = tmp_path
    spec = build_gitignore_spec(root, extra_patterns=[])
    assert not is_path_gitignored(root / "any" / "file.txt", root, spec)


def test_nonexistent_paths_still_match_by_name(tmp_path: Path):
    # Matching should not require the file to exist
    root = tmp_path
    write(root / ".gitignore", "generated/**\n")
    spec = collect_default_spec(root)
    assert is_path_gitignored(root / "generated" / "x" / "y.z", root, spec)
