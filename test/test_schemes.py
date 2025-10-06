# tests/test_version_bump.py
from __future__ import annotations

import pytest

from jiggle_version.schemes import bump_pep440, bump_semver

# ---------- PEP 440 ----------


@pytest.mark.parametrize(
    "start,inc,expected",
    [
        ("0.0.0", "patch", "0.0.1"),
        ("0.0.9", "minor", "0.1.0"),
        ("0.9.9", "major", "1.0.0"),
        ("1.2.3", "patch", "1.2.4"),
        ("1.2.3", "minor", "1.3.0"),
        ("1.2.3", "major", "2.0.0"),
        # missing minor/patch components are treated as 0
        ("1", "patch", "1.0.1"),
        ("1", "minor", "1.1.0"),
        ("1", "major", "2.0.0"),
        ("1.2", "patch", "1.2.1"),
        ("1.2", "minor", "1.3.0"),
        ("1.2", "major", "2.0.0"),
        # drops pre/dev/post segments on normal bump
        ("1.2.3rc1", "patch", "1.2.4"),
        ("1.2.3.dev2", "minor", "1.3.0"),
        ("1.2.3.post4", "major", "2.0.0"),
        ("1.2.3rc1.post2.dev3", "patch", "1.2.4"),
    ],
)
def test_bump_pep440_happy_paths(start: str, inc: str, expected: str):
    assert bump_pep440(start, inc) == expected


@pytest.mark.parametrize(
    "bad",
    [
        "not-a-version",
        "1.2.bad",
        "1..2",
        "",  # empty
    ],
)
def test_bump_pep440_invalid_raises(bad: str):
    with pytest.raises(ValueError) as ei:
        bump_pep440(bad, "patch")
    assert bad in str(ei.value)


# ---------- SemVer 2.0.0 ----------


@pytest.mark.parametrize(
    "start,inc,expected",
    [
        ("0.0.0", "patch", "0.0.1"),
        ("0.0.9", "minor", "0.1.0"),
        ("0.9.9", "major", "1.0.0"),
        ("1.2.3", "patch", "1.2.4"),
        ("1.2.3", "minor", "1.3.0"),
        ("1.2.3", "major", "2.0.0"),
        # pre-release/build metadata are stripped before bump
        ("1.2.3-alpha.1", "patch", "1.2.4"),
        ("1.2.3+build.5", "minor", "1.3.0"),
        ("1.2.3-alpha.1+exp.sha.5114f85", "major", "2.0.0"),
    ],
)
def test_bump_semver_happy_paths(start: str, inc: str, expected: str):
    assert bump_semver(start, inc) == expected


@pytest.mark.parametrize(
    "bad",
    [
        "1.2",  # missing patch
        "1",  # missing minor+patch
        "1.2.a",  # non-integer
        "a.b.c",  # non-integer
        "1..2",  # malformed
        "",  # empty
        "1.2.3.4",  # too many components
    ],
)
def test_bump_semver_invalid_raises(bad: str):
    with pytest.raises(ValueError) as ei:
        bump_semver(bad, "patch")
    assert bad in str(ei.value)
