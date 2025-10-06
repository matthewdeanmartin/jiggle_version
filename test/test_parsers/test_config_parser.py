from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from jiggle_version.parsers.config_parser import parse_pyproject_toml, parse_setup_cfg

# ---------- helpers ----------


def write(tmp: Path, name: str, body: str) -> Path:
    p = tmp / name
    p.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
    return p


# ---------- parse_pyproject_toml ----------


def test_parse_pyproject_toml_project_version(tmp_path: Path):
    f = write(
        tmp_path,
        "pyproject.toml",
        """
        [project]
        name = "demo"
        version = "1.2.3"
        """,
    )
    assert parse_pyproject_toml(f) == "1.2.3"


def test_parse_pyproject_toml_tool_setuptools_version(tmp_path: Path):
    f = write(
        tmp_path,
        "pyproject.toml",
        """
        [tool.setuptools]
        version = "9.9.9"
        """,
    )
    assert parse_pyproject_toml(f) == "9.9.9"


def test_parse_pyproject_toml_priority_project_over_tool(tmp_path: Path):
    f = write(
        tmp_path,
        "pyproject.toml",
        """
        [project]
        version = "1.0.0"
        [tool.setuptools]
        version = "2.0.0"
        """,
    )
    # project wins
    assert parse_pyproject_toml(f) == "1.0.0"


def test_parse_pyproject_toml_missing_file_returns_none(tmp_path: Path):
    assert parse_pyproject_toml(tmp_path / "missing.toml") is None


def test_parse_pyproject_toml_invalid_toml_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    f = write(tmp_path, "bad.toml", "project = { version = }")
    assert parse_pyproject_toml(f) is None
    err = capsys.readouterr().err
    assert "Could not parse" in err
    assert "bad.toml" in err


def test_parse_pyproject_toml_no_version_returns_none(tmp_path: Path):
    f = write(
        tmp_path,
        "pyproject.toml",
        """
        [project]
        name = "no_version"
        """,
    )
    assert parse_pyproject_toml(f) is None


# ---------- parse_setup_cfg ----------


def test_parse_setup_cfg_metadata_version(tmp_path: Path):
    f = write(
        tmp_path,
        "setup.cfg",
        """
        [metadata]
        version = 0.5.0
        """,
    )
    assert parse_setup_cfg(f) == "0.5.0"


def test_parse_setup_cfg_missing_file_returns_none(tmp_path: Path):
    assert parse_setup_cfg(tmp_path / "none.cfg") is None


def test_parse_setup_cfg_invalid_ini_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    f = write(
        tmp_path,
        "bad.cfg",
        """
        [metadata
        version = 2.3.4
        """,
    )
    assert parse_setup_cfg(f) is None
    err = capsys.readouterr().err
    assert "Could not parse" in err
    assert "bad.cfg" in err


def test_parse_setup_cfg_no_version_returns_none(tmp_path: Path):
    f = write(
        tmp_path,
        "setup.cfg",
        """
        [metadata]
        name = "example"
        """,
    )
    assert parse_setup_cfg(f) is None
