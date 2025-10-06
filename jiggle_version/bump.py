# jiggle_version/bump.py
"""
Main controller for bumping a version string.
"""
from __future__ import annotations

from .schemes import bump_pep440, bump_semver


def bump_version(version_string: str, increment: str, scheme: str = "pep440") -> str:
    """
    Dispatches to the correct bumping function based on the scheme.

    Args:
        version_string: The current version string.
        increment: The part to increment ('major', 'minor', 'patch').
        scheme: The versioning scheme ('pep440' or 'semver').

    Returns:
        The new, bumped version string.
    """
    if scheme == "pep440":
        return bump_pep440(version_string, increment)
    if scheme == "semver":
        return bump_semver(version_string, increment)

    raise ValueError(f"Unknown versioning scheme: '{scheme}'")
