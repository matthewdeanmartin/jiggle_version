# jiggle_version/pypi.py
"""
Implements a pre-flight check against PyPI to prevent bumping an unpublished version.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
import tomlkit
from packaging.version import Version

# Handle Python < 3.11 needing tomli
if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib


# --- Custom Exception ---
class UnpublishedVersionError(Exception):
    """Raised when attempting to bump a version that is unpublished on PyPI."""


# --- Caching Configuration ---
CACHE_TTL = timedelta(days=1)


def get_package_name(project_root: Path) -> str | None:
    """
    Finds the package name from pyproject.toml [project].name.
    """
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.is_file():
        return None
    try:
        config = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        return config.get("project", {}).get("name")
    except tomllib.TOMLDecodeError:
        return None


def get_latest_published_version(package_name: str, config_path: Path) -> str | None:
    """
    Fetches the latest published version of a package from PyPI, caching the
    result in the project's .jiggle_version.config file.
    """
    # --- Read from TOML cache ---
    doc = (
        tomlkit.parse(config_path.read_text(encoding="utf-8"))
        if config_path.is_file()
        else tomlkit.document()
    )
    jiggle_tool_config = doc.get("tool", {}).get("jiggle_version", {})
    pypi_cache = jiggle_tool_config.get("pypi_cache", {})
    last_checked_str = pypi_cache.get("timestamp")

    if last_checked_str:
        last_checked = datetime.fromisoformat(last_checked_str)
        if datetime.now(timezone.utc) - last_checked < CACHE_TTL:
            print(
                f"   (from cache created at {last_checked.strftime('%Y-%m-%d %H:%M')})"
            )
            return pypi_cache.get("latest_version")

    # --- Fetch from PyPI ---
    print("   (querying pypi.org...)")
    url = f"https://pypi.org/pypi/{package_name}/json"
    latest_version = None
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            latest_version = None  # Package not on PyPI at all
        elif response.status_code == 200:
            data = response.json()
            latest_version = data.get("info", {}).get("version")
        # On other errors, we return None to skip the check gracefully

        # --- Update TOML cache ---
        cache_table = tomlkit.table()
        cache_table.add("timestamp", datetime.now(timezone.utc).isoformat())
        cache_table.add("latest_version", latest_version)

        if "tool" not in doc:
            doc.add("tool", tomlkit.table())
        if "jiggle_version" not in doc.get("tool", {}):  # type: ignore
            doc["tool"].add("jiggle_version", tomlkit.table())  # type: ignore

        doc["tool"]["jiggle_version"]["pypi_cache"] = cache_table  # type: ignore
        config_path.write_text(tomlkit.dumps(doc), encoding="utf-8")

    except requests.RequestException:
        # Network error, skip the check
        pass

    return latest_version


def check_pypi_publication(
    package_name: str, current_version: str, new_version: str, config_path: Path
) -> None:
    """
    Checks if the current version is published and allows bumping under specific rules.
    """
    latest_published_str = get_latest_published_version(package_name, config_path)

    if not latest_published_str:
        # NEW BEHAVIOR: If the package has never been published, block the bump.
        raise UnpublishedVersionError(
            f"Package '{package_name}' is not on PyPI. Publish the initial version first."
        )

    current_v = Version(current_version)
    published_v = Version(latest_published_str)
    new_v = Version(new_version)

    if current_v > published_v:
        if new_v > current_v:
            print(
                f"🟡 Current version '{current_v}' is unpublished (PyPI has '{published_v}'). "
                f"Allowing bump to '{new_v}'."
            )
            return
        raise UnpublishedVersionError(
            f"Current version '{current_v}' is not published on PyPI (latest is '{published_v}').\n"
            "Cannot perform a redundant bump."
        )
    elif new_v > published_v:
        print(f"✅ PyPI version is '{published_v}'. Bump to '{new_v}' is allowed.")
        return
    else:
        raise UnpublishedVersionError(
            f"New version '{new_v}' is not greater than the latest published version on PyPI ('{published_v}')."
        )
