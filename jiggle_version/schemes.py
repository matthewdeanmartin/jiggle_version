# jiggle_version/schemes.py
"""
Implements the version bumping logic for different versioning schemes.
"""
from __future__ import annotations

from packaging.version import InvalidVersion, Version


def bump_pep440(version_string: str, increment: str) -> str:
    """
    Bumps a version string that follows PEP 440.

    Args:
        version_string: The current version string (e.g., "1.2.3.rc1").
        increment: The part to increment ('major', 'minor', 'patch').

    Returns:
        The new version string.
    """
    try:
        v = Version(version_string)
        major, minor, patch = (
            v.release[0],
            v.release[1] if len(v.release) > 1 else 0,
            v.release[2] if len(v.release) > 2 else 0,
        )

        if increment == "major":
            major += 1
            minor = 0
            patch = 0
        elif increment == "minor":
            minor += 1
            patch = 0
        elif increment == "patch":
            patch += 1

        # By default, pre-release, dev, and post-release tags are dropped on a standard bump.
        return f"{major}.{minor}.{patch}"

    except (InvalidVersion, IndexError):
        raise ValueError(f"'{version_string}' is not a valid PEP 440 version.")


def bump_semver(version_string: str, increment: str) -> str:
    """
    Bumps a version string that follows SemVer 2.0.0.

    Args:
        version_string: The current version string (e.g., "1.2.3-alpha.1").
        increment: The part to increment ('major', 'minor', 'patch').

    Returns:
        The new version string.
    """
    # SemVer can have pre-release tags, which we strip for a standard bump.
    main_version = version_string.split("-")[0].split("+")[0]

    try:
        parts = [int(p) for p in main_version.split(".")]
        if len(parts) != 3:
            raise ValueError("SemVer requires a MAJOR.MINOR.PATCH structure.")

        major, minor, patch = parts

        if increment == "major":
            major += 1
            minor = 0
            patch = 0
        elif increment == "minor":
            minor += 1
            patch = 0
        elif increment == "patch":
            patch += 1

        return f"{major}.{minor}.{patch}"

    except (ValueError, IndexError):
        raise ValueError(f"'{version_string}' is not a valid SemVer string.")
