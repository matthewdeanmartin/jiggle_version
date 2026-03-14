from __future__ import annotations

import shutil
import textwrap
from pathlib import Path
from uuid import uuid4

import pytest
from hypothesis import given
from hypothesis import strategies as st

from jiggle_version.parsers.ast_parser import parse_python_module, parse_setup_py
from jiggle_version.parsers.config_parser import parse_setup_cfg
from jiggle_version.schemes import bump_pep440, bump_semver
from jiggle_version.update import update_python_file, update_setup_cfg

IDENTIFIER = st.from_regex(r"[A-Za-z_][A-Za-z0-9_]{0,10}", fullmatch=True)
NON_VERSION_IDENTIFIER = IDENTIFIER.filter(
    lambda name: name != "__version__" and not name.endswith("version")
)
SEMVER_PART = st.integers(min_value=0, max_value=1_000_000)
INCREMENT = st.sampled_from(["major", "minor", "patch"])
SAFE_VERSION = st.from_regex(r"[0-9]+(?:\.[0-9A-Za-z]+){0,3}", fullmatch=True)
SAFE_CFG_TEXT = st.text(
    alphabet=st.characters(
        blacklist_characters="[]#\r\n", min_codepoint=32, max_codepoint=126
    ),
    min_size=0,
    max_size=30,
)
SCRATCH_ROOT = Path(__file__).resolve().parents[1] / "tmp_hypothesis_runtime"


def write(tmp_path: Path, name: str, body: str) -> Path:
    file_path = tmp_path / name
    file_path.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
    return file_path


def make_scratch_dir() -> Path:
    path = SCRATCH_ROOT / uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    return path


def cleanup_scratch_dir(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)


@given(major=SEMVER_PART, minor=SEMVER_PART, patch=SEMVER_PART, increment=INCREMENT)
def test_bump_semver_matches_manual_increment(
    major: int, minor: int, patch: int, increment: str
):
    start = f"{major}.{minor}.{patch}"
    expected = {
        "major": f"{major + 1}.0.0",
        "minor": f"{major}.{minor + 1}.0",
        "patch": f"{major}.{minor}.{patch + 1}",
    }[increment]
    assert bump_semver(start, increment) == expected


@given(major=SEMVER_PART, minor=SEMVER_PART, patch=SEMVER_PART, increment=INCREMENT)
def test_bump_pep440_matches_manual_increment_for_release_versions(
    major: int, minor: int, patch: int, increment: str
):
    start = f"{major}.{minor}.{patch}"
    expected = {
        "major": f"{major + 1}.0.0",
        "minor": f"{major}.{minor + 1}.0",
        "patch": f"{major}.{minor}.{patch + 1}",
    }[increment]
    assert bump_pep440(start, increment) == expected


@pytest.mark.parametrize("increment", ["", "build", "MAJOR", "patches"])
def test_bump_functions_reject_unknown_increment(increment: str):
    with pytest.raises(ValueError):
        bump_pep440("1.2.3", increment)

    with pytest.raises(ValueError):
        bump_semver("1.2.3", increment)


@given(
    shadow_name=NON_VERSION_IDENTIFIER,
    shadow_version=SAFE_VERSION,
    new_version=SAFE_VERSION,
)
def test_update_python_file_does_not_touch_non_version_identifiers(
    shadow_name: str, shadow_version: str, new_version: str
):
    scratch_dir = make_scratch_dir()
    try:
        file_path = write(
            scratch_dir,
            "module.py",
            f"""
            {shadow_name} = "{shadow_version}"
            minimum_version = "{shadow_version}"
            __version__ = "0.1.0"
            """,
        )

        update_python_file(file_path, new_version)

        updated = file_path.read_text(encoding="utf-8")
        assert f'{shadow_name} = "{shadow_version}"' in updated
        assert f'minimum_version = "{shadow_version}"' in updated
        assert parse_python_module(file_path) == new_version
    finally:
        cleanup_scratch_dir(scratch_dir)


@given(start_version=SAFE_VERSION, new_version=SAFE_VERSION)
def test_update_python_file_round_trips_setup_py_literal_version(
    start_version: str, new_version: str
):
    scratch_dir = make_scratch_dir()
    try:
        file_path = write(
            scratch_dir,
            "setup.py",
            f"""
            from setuptools import setup

            setup(name="pkg", version="{start_version}")
            """,
        )

        update_python_file(file_path, new_version)
        assert parse_setup_py(file_path) == new_version
    finally:
        cleanup_scratch_dir(scratch_dir)


@given(
    original_version=SAFE_VERSION,
    new_version=SAFE_VERSION,
    other_section_version=SAFE_VERSION,
    noise=SAFE_CFG_TEXT,
)
def test_update_setup_cfg_only_updates_metadata_version(
    original_version: str,
    new_version: str,
    other_section_version: str,
    noise: str,
):
    scratch_dir = make_scratch_dir()
    try:
        file_path = write(
            scratch_dir,
            "setup.cfg",
            f"""
            [metadata]
            name = demo
            summary = {noise or "demo"}
            version = {original_version}

            [tool:pytest]
            version = {other_section_version}
            """,
        )

        update_setup_cfg(file_path, new_version)

        assert parse_setup_cfg(file_path) == new_version
        updated = file_path.read_text(encoding="utf-8")
        assert f"[tool:pytest]\nversion = {other_section_version}" in updated
    finally:
        cleanup_scratch_dir(scratch_dir)
