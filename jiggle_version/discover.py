# jiggle_version/discover.py
"""
Logic for discovering all potential version source files in a project,
while respecting .gitignore and default ignore patterns.
"""
from __future__ import annotations

import logging
from pathlib import Path

# Use the new gitignore API
from .gitignore import (
    collect_default_spec,
    is_path_explicitly_ignored,
    is_path_gitignored,
)

# Files to search for recursively in the project root.
RECURSIVE_SEARCH_FILES = ["_version.py", "__version__.py", "__about__.py"]

# Statically named files to check for in the project root.
STATIC_SEARCH_FILES = ["pyproject.toml", "setup.cfg", "setup.py"]

# Default directories to always ignore.
DEFAULT_IGNORE_DIRS = {".git", ".tox", ".venv", "__pycache__"}

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

    # Build a single PathSpec with repo/global ignores and any future extras
    spec = collect_default_spec(project_root)

    # Resolve user-provided ignore paths to absolute form for reliable comparison
    explicit_ignore_set = {(project_root / p).resolve() for p in (ignore_paths or [])}

    _walk_and_discover(
        current_dir=project_root,
        project_root=project_root,
        found_files=found_files,
        spec=spec,
        explicit_ignore_set=explicit_ignore_set,
    )

    return sorted(found_files)


def _walk_and_discover(
    *,
    current_dir: Path,
    project_root: Path,
    found_files: set[Path],
    spec,
    explicit_ignore_set: set[Path],
) -> None:
    """Recursively walk directories to find source files."""
    for item in current_dir.iterdir():
        # Check against default, .gitignore (via PathSpec), and user-specified ignore paths
        if (
            item.name in DEFAULT_IGNORE_DIRS
            or is_path_gitignored(item, project_root, spec)
            or is_path_explicitly_ignored(item, explicit_ignore_set)
        ):
            continue

        if item.is_dir():
            # If top-level package dir has __init__.py, include it
            init_file = item / "__init__.py"
            if init_file.is_file() and current_dir == project_root:
                found_files.add(init_file)

            _walk_and_discover(
                current_dir=item,
                project_root=project_root,
                found_files=found_files,
                spec=spec,
                explicit_ignore_set=explicit_ignore_set,
            )

        elif item.is_file():
            # Root-only statics
            if item.name in STATIC_SEARCH_FILES and item.parent == project_root:
                found_files.add(item)
            # Recursive targets
            elif item.name in RECURSIVE_SEARCH_FILES:
                found_files.add(item)
