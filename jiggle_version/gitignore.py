# jiggle_version/gitignore.py
"""
Git-aware path ignoring built on `pathspec`'s `GitWildMatchPattern`.

Goals
-----
- Correctly honor .gitignore semantics (wildcards, directory suffix `/`,
  negation `!`, anchored vs unanchored patterns, etc.).
- Allow optional user-supplied ignore patterns to merge with repo rules.
- Provide a simple `is_path_gitignored` API usable by call sites.

Notes
-----
- We do **not** shell out to `git`.
- We merge patterns from, in order:
  1) `<project_root>/.gitignore` (if present)
  2) `<project_root>/.git/info/exclude` (if present)
  3) Global excludes file (~/.config/git/ignore or ~/.gitignore)
  4) `extra_patterns` provided by the caller
  Later rules can override earlier ones via negation (`!pattern`).

Dependency
----------
`pathspec>=0.12` (https://pypi.org/project/pathspec/)

Public functions
----------------
- `build_gitignore_spec(project_root: Path, extra_patterns: list[str] | None) -> PathSpec`
- `is_path_gitignored(path: Path, project_root: Path, spec_or_patterns: PathSpec | list[str] | None) -> bool`
- `is_path_explicitly_ignored(path: Path, ignored_paths: set[Path]) -> bool`
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

# ----------------------------- helpers -----------------------------


def _read_lines(p: Path) -> list[str]:
    """Read a text file into a list of lines, stripping trailing newlines.

    Returns empty list if the file does not exist.
    """
    if not p.is_file():
        return []
    return [ln.rstrip("\n") for ln in p.read_text(encoding="utf-8").splitlines()]


def _candidate_global_ignores() -> list[Path]:
    """Return plausible global gitignore locations (best-effort, no git call)."""
    home = Path.home()
    # Common defaults used by Git when core.excludesFile is not set explicitly
    return [
        home / ".config" / "git" / "ignore",
        home / ".gitignore",
    ]


# ----------------------------- core build -----------------------------


def build_gitignore_spec(
    project_root: Path,
    *,
    extra_patterns: list[str] | None = None,
) -> PathSpec:
    """Construct a `PathSpec` with Git-style matching semantics.

    Parameters
    ----------
    project_root: Path
        Repository/work-tree root. Patterns are interpreted relative to this folder.
    extra_patterns: list[str] | None
        Additional patterns to append **after** repo/global sources.

    Returns
    -------
    PathSpec
        Compiled spec. Safe to reuse across many `is_path_gitignored` calls.
    """
    patterns: list[str] = []

    # Root .gitignore
    patterns += _read_lines(project_root / ".gitignore")

    # Repo local excludes
    patterns += _read_lines(project_root / ".git" / "info" / "exclude")

    # Global excludes (best-effort)
    for p in _candidate_global_ignores():
        patterns += _read_lines(p)

    # User-provided patterns last (can override via negation)
    if extra_patterns:
        patterns += list(extra_patterns)

    # Normalize: drop comments/blank lines here; pathspec handles the rest
    normalized: list[str] = []
    for raw in patterns:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        normalized.append(line)

    return PathSpec.from_lines(GitWildMatchPattern, normalized)


# ----------------------------- queries -----------------------------


def is_path_gitignored(
    path: Path,
    project_root: Path,
    spec_or_patterns: PathSpec | Iterable[str] | None,
) -> bool:
    """Return True if `path` is ignored by the given spec or patterns.

    - `path` may be file or directory (existing or hypothetical).
    - `project_root` anchors relative matching.
    - `spec_or_patterns` can be a pre-built `PathSpec`, an iterable of pattern
      strings (Git semantics), or `None` (treated as empty).

    Implementation detail: `pathspec` expects POSIX-style paths. We therefore
    convert `path.relative_to(project_root)` to a forward-slash string.
    """
    rel = path.resolve().relative_to(project_root.resolve())
    rel_str = rel.as_posix()

    if isinstance(spec_or_patterns, PathSpec):
        spec = spec_or_patterns
    else:
        patterns = list(spec_or_patterns or [])
        spec = PathSpec.from_lines(GitWildMatchPattern, patterns)

    # `match_file` applies directory-aware rules correctly
    return spec.match_file(rel_str)


def is_path_explicitly_ignored(path: Path, ignored_paths: set[Path]) -> bool:
    """Return True if `path` equals or is a descendant of any path in `ignored_paths`.

    This is an explicit, non-.gitignore override that callers can use for
    user-specified absolute directories/files.
    """
    abs_path = path.resolve()
    for ip in ignored_paths:
        ip = ip.resolve()
        if abs_path == ip or ip in abs_path.parents:
            return True
    return False


# ----------------------------- convenience -----------------------------


def collect_default_spec(
    project_root: Path, extra_patterns: list[str] | None = None
) -> PathSpec:
    """One-shot helper used by callers that don't need fine control."""
    return build_gitignore_spec(project_root, extra_patterns=extra_patterns)
