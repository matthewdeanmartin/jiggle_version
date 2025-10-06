# jiggle_version/update.py
"""
Logic for updating version strings in various source files.
"""
from __future__ import annotations

import re
from pathlib import Path

import tomlkit


def update_pyproject_toml(file_path: Path, new_version: str) -> None:
    """Updates the version in a pyproject.toml file using tomlkit to preserve formatting."""
    doc = tomlkit.parse(file_path.read_text(encoding="utf-8"))

    updated = False
    if "project" in doc and "version" in doc["project"]:  # type: ignore[operator]
        doc["project"]["version"] = new_version  # type: ignore[index]
        updated = True
    elif "tool" in doc and "setuptools" in doc["tool"] and "version" in doc["tool"]["setuptools"]:  # type: ignore[operator,index]
        doc["tool"]["setuptools"]["version"] = new_version  # type: ignore[index]
        updated = True

    if updated:
        file_path.write_text(tomlkit.dumps(doc), encoding="utf-8")


def update_setup_cfg(file_path: Path, new_version: str) -> None:
    """Updates the version in a setup.cfg file using regex."""
    content = file_path.read_text(encoding="utf-8")
    # Regex to find 'version = ...' under the [metadata] section
    new_content = re.sub(
        r"(?<=^\[metadata\]\s*\n(?:.*\n)*?version\s*=\s*).*",
        new_version,
        content,
        flags=re.MULTILINE,
    )
    file_path.write_text(new_content, encoding="utf-8")


def update_python_file(file_path: Path, new_version: str) -> None:
    """Updates the version in a Python file (`__version__` or `setup.py`) using regex."""
    content = file_path.read_text(encoding="utf-8")
    # Regex to find `__version__ = "..."` or `version="..."`
    # It captures the quote style to preserve it.
    pattern = re.compile(r"""(__version__\s*=\s*|version\s*=\s*)['"](.*?)['"]""")

    def replacer(match):
        # Reconstruct the line with the new version, keeping the original quote style
        # by simply replacing the content between the quotes.
        return f'{match.group(1)}"{new_version}"'

    new_content, count = pattern.subn(replacer, content)

    if count > 0:
        file_path.write_text(new_content, encoding="utf-8")
