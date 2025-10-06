# jiggle_version/parsers/config_parser.py
"""
Parsers for configuration files like pyproject.toml and setup.cfg.
"""
from __future__ import annotations

import configparser
import sys
from pathlib import Path

# Handle Python < 3.11 needing tomli
if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib


def parse_pyproject_toml(file_path: Path) -> str | None:
    """
    Finds and returns the version string from a pyproject.toml file.

    It checks for the version in the following order of priority:
    1. [project].version (PEP 621)
    2. [tool.setuptools].version

    Args:
        file_path: The path to the pyproject.toml file.

    Returns:
        The version string if found, otherwise None.
    """
    if not file_path.is_file():
        return None

    try:
        config = tomllib.loads(file_path.read_text(encoding="utf-8"))

        # 1. Check for PEP 621 project metadata
        if version := config.get("project", {}).get("version"):
            return str(version)

        # 2. Check for setuptools-specific metadata
        if version := config.get("tool", {}).get("setuptools", {}).get("version"):
            return str(version)

    except tomllib.TOMLDecodeError:
        # Handle cases with invalid TOML
        print(f"Warning: Could not parse '{file_path}'. Invalid TOML.", file=sys.stderr)
        return None

    return None


def parse_setup_cfg(file_path: Path) -> str | None:
    """
    Finds and returns the version string from a setup.cfg file.

    It checks for the version in [metadata].version.

    Args:
        file_path: The path to the setup.cfg file.

    Returns:
        The version string if found, otherwise None.
    """
    if not file_path.is_file():
        return None

    try:
        config = configparser.ConfigParser()
        config.read(file_path, encoding="utf-8")
        return config.get("metadata", "version", fallback=None)
    except configparser.Error:
        # Handle cases with invalid INI format
        print(f"Warning: Could not parse '{file_path}'.", file=sys.stderr)
        return None
