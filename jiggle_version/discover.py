# jiggle_version/discover.py
"""
Logic for discovering all potential version source files in a project,
while respecting .gitignore and default ignore patterns.
"""
from __future__ import annotations

import logging
from pathlib import Path

# Use the new gitignore API
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

from .gitignore import (
    build_gitignore_spec,
    is_path_explicitly_ignored,
    is_path_gitignored,
    nested_gitignore_patterns,
)

# Files to search for recursively in the project root.
RECURSIVE_SEARCH_FILES = ["_version.py", "__version__.py", "__about__.py"]

# Statically named files to check for in the project root.
STATIC_SEARCH_FILES = ["pyproject.toml", "setup.cfg", "setup.py"]

# Default directories to always ignore.
DEFAULT_IGNORE_DIRS = {
    ".git",
    ".tox",
    ".venv",
    "__pycache__",
    "site-packages",
    "node_modules",
}

# Marker files whose presence means the directory is a virtual environment root.
# We skip walking into venv roots entirely (they contain installed packages, not
# the project's own version declarations).
VENV_MARKER_FILES = {"pyvenv.cfg"}

# Cache Directory Tagging Standard (https://bford.info/cachedir/). A directory
# containing a CACHEDIR.TAG with this signature is a cache (uv, pip, mypy, ruff,
# hatch, ...) and should be skipped entirely.
CACHEDIR_TAG_FILE = "CACHEDIR.TAG"
CACHEDIR_TAG_SIGNATURE = "Signature: 8a477f597d28d172789f06886806bc55"

LOGGER = logging.getLogger(__name__)


def find_source_files(
    project_root: Path, ignore_paths: list[str] | None = None
) -> list[Path]:
    """
    Scans a project directory and returns a list of all potential version
    source files, ignoring gitignored and user-specified paths.

    Args:
        project_root: The root directory of the project to scan.
        ignore_paths: A list of relative paths to explicitly ignore.

    Returns:
        A sorted list of Path objects for all found source files.
    """
    LOGGER.debug("project root %s, ignore_paths %s", project_root, ignore_paths)
    found_files: set[Path] = set()

    # Build the base spec with repo/global ignores. Nested .gitignore files are
    # layered on top as the walk descends into the directories that contain them.
    base_spec = build_gitignore_spec(project_root)

    # Resolve user-provided ignore paths to absolute form for reliable comparison
    explicit_ignore_set = {(project_root / p).resolve() for p in (ignore_paths or [])}

    _walk_and_discover(
        current_dir=project_root,
        project_root=project_root,
        found_files=found_files,
        spec=base_spec,
        explicit_ignore_set=explicit_ignore_set,
    )

    return sorted(found_files)


def _is_cache_dir(directory: Path) -> bool:
    """Return True if `directory` contains a valid CACHEDIR.TAG marker file."""
    tag = directory / CACHEDIR_TAG_FILE
    try:
        if not tag.is_file():
            return False
        with tag.open("r", encoding="utf-8", errors="replace") as fh:
            first_line = fh.readline().rstrip("\n").rstrip("\r")
        return first_line == CACHEDIR_TAG_SIGNATURE
    except OSError as exc:
        LOGGER.warning("Skipping unreadable cache tag %s: %s", tag, exc)
        return False


def _walk_and_discover(
    *,
    current_dir: Path,
    project_root: Path,
    found_files: set[Path],
    spec,
    explicit_ignore_set: set[Path],
) -> None:
    """Recursively walk directories to find source files."""
    # Layer any nested .gitignore in this directory onto the active spec, matching
    # git's cascading semantics (e.g. uv drops `./.uv/.gitignore` containing `*`).
    nested = nested_gitignore_patterns(current_dir, project_root)
    if nested:
        spec = PathSpec(
            list(spec.patterns) + list(PathSpec.from_lines(GitWildMatchPattern, nested).patterns)
        )

    try:
        items = list(current_dir.iterdir())
    except OSError as exc:
        LOGGER.warning("Skipping unreadable directory %s: %s", current_dir, exc)
        return

    for item in items:
        # Check against default, .gitignore (via PathSpec), and user-specified ignore paths
        if (
            item.name in DEFAULT_IGNORE_DIRS
            or is_path_gitignored(item, project_root, spec)
            or is_path_explicitly_ignored(item, explicit_ignore_set)
        ):
            continue

        try:
            is_dir = item.is_dir()
            is_file = item.is_file()
        except OSError as exc:
            LOGGER.warning("Skipping unreadable path %s: %s", item, exc)
            continue

        if is_dir:
            # Skip virtual environment roots (contain installed packages, not project versions).
            if any((item / marker).is_file() for marker in VENV_MARKER_FILES):
                LOGGER.debug("Skipping venv root: %s", item)
                continue

            # Skip cache directories tagged per the Cache Directory Tagging Standard.
            if _is_cache_dir(item):
                LOGGER.debug("Skipping tagged cache dir: %s", item)
                continue

            # If top-level package dir has __init__.py, include it
            init_file = item / "__init__.py"
            try:
                has_init = init_file.is_file()
            except OSError as exc:
                LOGGER.warning("Skipping unreadable path %s: %s", init_file, exc)
                has_init = False

            if has_init and current_dir == project_root:
                found_files.add(init_file)

            _walk_and_discover(
                current_dir=item,
                project_root=project_root,
                found_files=found_files,
                spec=spec,
                explicit_ignore_set=explicit_ignore_set,
            )

        elif is_file:
            # Root-only statics
            if item.name in STATIC_SEARCH_FILES and item.parent == project_root:
                found_files.add(item)
            # Recursive targets
            elif item.name in RECURSIVE_SEARCH_FILES:
                found_files.add(item)
