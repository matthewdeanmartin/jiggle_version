# jiggle_version/update.py
"""
Logic for updating version strings in various source files.
"""
from __future__ import annotations

import re
from pathlib import Path

import tomlkit

_PYTHON_DUNDER_VERSION_RE = re.compile(
    r"""(?m)^(\s*__version__\s*=\s*)(['"])(.*?)(\2)"""
)
_PYTHON_SETUP_VERSION_RE = re.compile(r"""(?<![\w.])(version\s*=\s*)(['"])(.*?)(\2)""")


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
    """Updates the version in the [metadata] section of setup.cfg."""
    lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)

    in_metadata = False
    updated = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_metadata = stripped == "[metadata]"
            continue

        if not in_metadata or "=" not in line:
            continue

        key, value = line.split("=", 1)
        if key.strip() != "version":
            continue

        line_ending = (
            "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        )
        leading = line[: len(line) - len(line.lstrip())]
        trailing_comment = ""
        value_without_newline = value.rstrip("\r\n")
        if "#" in value_without_newline:
            _, comment = value_without_newline.split("#", 1)
            trailing_comment = f"  #{comment}"

        lines[index] = (
            f"{leading}version = {new_version}{trailing_comment}{line_ending}"
        )
        updated = True
        break

    if updated:
        file_path.write_text("".join(lines), encoding="utf-8")


def update_python_file(file_path: Path, new_version: str) -> None:
    """Updates the version in a Python file (`__version__` or `setup.py`) using regex."""
    content = file_path.read_text(encoding="utf-8")

    def replacer(match: re.Match[str]) -> str:
        return f"{match.group(1)}{match.group(2)}{new_version}{match.group(2)}"

    new_content, dunder_count = _PYTHON_DUNDER_VERSION_RE.subn(replacer, content)
    new_content, setup_count = _PYTHON_SETUP_VERSION_RE.subn(replacer, new_content)

    if dunder_count > 0 or setup_count > 0:
        file_path.write_text(new_content, encoding="utf-8")
