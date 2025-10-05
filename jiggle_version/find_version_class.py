from __future__ import annotations

import configparser
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, cast

# Assuming these imports are from the original project structure
from semantic_version import Version

from jiggle_version.file_inventory import FileInventory
from jiggle_version.file_opener import FileOpener
from jiggle_version.parse_version import parse_dunder_version as dunder_version
from jiggle_version.parse_version import parse_kwarg_version as kwarg_version
from jiggle_version.parse_version.schema_guesser import version_object_and_next
from jiggle_version.utils import (
    JiggleVersionException,
    first_value_in_dict,
    merge_two_dicts,
)

logger = logging.getLogger(__name__)


# ==============================================================================
# 1. Version Parsers - Each function has a single job: parse a string.
# ==============================================================================


def parse_version_from_setup_py(content: str) -> Optional[str]:
    """Parses version from setup.py content, checking for kwarg and dunder."""
    if "use_scm_version=True" in content:
        raise JiggleVersionException(
            "Project uses use_scm_version=True; manual versioning is disabled."
        )
    for line in content.splitlines():
        version = kwarg_version.find_in_line(line)
        if version:
            return version
        version = dunder_version.find_in_line(line)[0]
        if version:
            return version
    return None


def parse_version_from_dunder(content: str) -> Optional[str]:
    """Parses `__version__` from a Python file's content."""
    for line in content.splitlines():
        version = dunder_version.find_in_line(line)[0]
        if version:
            return version
    return None


def parse_version_from_cfg(content: str) -> Optional[str]:
    """Parses version from a .cfg or .ini file's [metadata] section."""
    config = configparser.ConfigParser()
    try:
        config.read_string(content)
        return config.get("metadata", "version", fallback=None)
    except (configparser.Error, KeyError):
        return None


def parse_version_from_text(content: str) -> Optional[str]:
    """Parses version from a plain text file (e.g., version.txt)."""
    return content.strip() if content else None


# ==============================================================================
# 2. Version Consolidator - Validates and reconciles multiple versions.
# ==============================================================================


class VersionConsolidator:
    """
    Takes a dictionary of found versions, validates them, and finds the
    single canonical version for the project.
    """

    def _filter_valid_versions(
        self, versions: Dict[Path, str | None]
    ) -> Tuple[Dict[Path, str | None], Dict[Path, str | None]]:
        """Separates valid semantic versions from invalid ones."""
        valid_versions: Dict[Path, str | None] = {}
        invalid_versions: Dict[Path, str | None] = {}
        for source, version_str in versions.items():
            try:
                # Use schema guesser to validate the version format
                version_object_and_next(version_str or "")
                valid_versions[source] = version_str
            except Exception:
                invalid_versions[source] = version_str
        return valid_versions, invalid_versions

    def _find_highest_patch(self, versions: List[str]) -> Optional[str]:
        """If two versions differ only by a patch, returns the higher one."""
        if len(versions) != 2:
            return None

        try:
            v1 = Version(versions[0])
            v2 = Version(versions[1])
        except ValueError:
            return None  # Not valid SemVer

        # Check if they are identical except for the patch
        if v1.major == v2.major and v1.minor == v2.minor:
            # Check if they are consecutive patches
            if abs(v1.patch - v2.patch) == 1:
                return str(max(v1, v2))
        return None

    def consolidate(self, versions: Dict[Path, str | None], force_init: bool) -> str:
        """
        Consolidates found versions into a single, trusted version string.

        Args:
            versions: A dictionary mapping file paths to version strings.
            force_init: If true, returns '0.1.0' if no versions are found.

        Returns:
            The single canonical version string.

        Raises:
            JiggleVersionException: If no versions are found (and not force_init)
                                    or if inconsistent versions are found.
        """
        valid_versions, invalid_versions = self._filter_valid_versions(versions)

        if invalid_versions:
            logger.warning(f"Found and ignored invalid versions: {invalid_versions}")

        if not valid_versions:
            if force_init:
                logger.info("No valid versions found. Using --init default '0.1.0'.")
                return "0.1.0"
            raise JiggleVersionException(
                "No valid versions found. Use --init to create one."
            )

        unique_versions = set(valid_versions.values())

        if len(unique_versions) == 1:
            return unique_versions.pop() or ""

        # Handle acceptable inconsistencies, like a minor patch difference
        higher_version = self._find_highest_patch(list(_ for _ in unique_versions if _))
        if higher_version:
            logger.warning(
                f"Versions differ only by a patch level {unique_versions}. "
                f"Using the highest: {higher_version}"
            )
            return higher_version

        # Unacceptable inconsistency
        error_msg = (
            f"Found multiple, inconsistent versions: {valid_versions}. Cannot proceed."
        )
        logger.error(error_msg)
        raise JiggleVersionException(error_msg)


# ==============================================================================
# 3. Version Discoverer - The orchestrator.
# ==============================================================================


class VersionDiscoverer:
    """
    Orchestrates the discovery of the project's current version by
    coordinating file searching, parsing, and consolidation.
    """

    def __init__(
        self, project: Path, source: Path, file_opener: FileOpener, force_init: bool
    ):
        if source is None:
            raise JiggleVersionException("Source directory cannot be None.")

        self.file_inventory = FileInventory(project, source)
        self.file_opener = file_opener
        self.force_init = force_init
        self.consolidator = VersionConsolidator()

        # Optional: Add project layout validation if needed
        self._validate_project_structure(project, source)

    def _validate_project_structure(self, project: Path, source: Path) -> None:
        """Confirms that a project structure (module, file, or setup.py) exists."""
        is_folder = os.path.isdir(os.path.join(source, project))
        is_file = os.path.isfile(os.path.join(source, str(project) + ".py"))
        is_setup_only = os.path.isfile(os.path.join(source, "setup.py"))

        if not any([is_folder, is_file, is_setup_only]):
            raise JiggleVersionException(
                f"Cannot find project structure for '{project}' in '{source}'."
            )

    def discover_version(self) -> str:
        """
        Finds all potential version strings from the project files and
        returns the single, consolidated version.

        Returns:
            The canonical version string for the project.
        """
        versions: Dict[Path, str | None] = {}

        # 1. Check setup.py
        if Path("setup.py").exists():
            setup_py = Path("setup.py")
            content = self.file_opener.read_this(setup_py)
            version = parse_version_from_setup_py(content)
            if version:
                versions[setup_py] = version

        # 2. Check config files (setup.cfg, etc.)
        for cfg_file in self.file_inventory.config_files:
            if os.path.exists(cfg_file):
                content = self.file_opener.read_this(cfg_file)
                version = parse_version_from_cfg(content)
                if version:
                    versions[cfg_file] = version

        # 3. Check source files for __version__
        for src_file in self.file_inventory.source_files:
            if os.path.exists(src_file):
                content = self.file_opener.read_this(src_file)
                version = parse_version_from_dunder(content)
                if version:
                    # Avoid overwriting a more specific parse (e.g., from setup.py)
                    if src_file not in versions:
                        versions[src_file] = version

        # 4. Check special text files (version.txt)
        for txt_file in self.file_inventory.text_files:
            if os.path.exists(txt_file):
                content = self.file_opener.read_this(txt_file)
                version = parse_version_from_text(content)
                if version:
                    versions[txt_file] = version

        # TODO: Implement risky strategies like version_by_import if necessary,
        # but keep them isolated and clearly marked.

        return self.consolidator.consolidate(versions, self.force_init)
