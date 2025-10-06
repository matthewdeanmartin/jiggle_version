from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from jiggle_version.config import load_config_from_path


def write(p: Path, body: str) -> Path:
    p.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
    return p


def test_missing_file_returns_empty_dict(tmp_path: Path):
    cfg = load_config_from_path(tmp_path / "pyproject.toml")
    assert cfg == {}


def test_valid_config_basic_and_increment_normalization(tmp_path: Path):
    f = write(
        tmp_path / "pyproject.toml",
        """
        [tool.jiggle_version]
        default_increment = "minor"
        """,
    )
    cfg = load_config_from_path(f)
    # normalized key
    assert cfg.get("increment") == "minor"
    assert "default_increment" not in cfg


@pytest.mark.parametrize(
    "rhs,expected",
    [
        ('"pkg"', ["pkg"]),  # str -> [str]
        ('["a", "b/sub"]', ["a", "b/sub"]),  # list -> list
        # ('("x", "y")', ["x", "y"]),                # tuple -> list  -- why not?
        ('["one"] # comment', ["one"]),  # comment tolerated by toml
    ],
)
def test_ignore_normalization_valid_types(
    tmp_path: Path, rhs: str, expected: list[str]
):
    f = write(
        tmp_path / "pyproject.toml",
        f"""
        [tool.jiggle_version]
        ignore = {rhs}
        """,
    )
    cfg = load_config_from_path(f)
    assert cfg.get("ignore") == expected


def test_ignore_normalization_set_becomes_list(tmp_path: Path):
    # TOML has no set literal; emulate by array-of-unique values then ensure pass-through.
    f = write(
        tmp_path / "pyproject.toml",
        """
        [tool.jiggle_version]
        ignore = ["a", "b"]
        """,
    )
    cfg = load_config_from_path(f)
    assert cfg.get("ignore") == ["a", "b"]


def test_ignore_invalid_type_warns_and_is_dropped(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    # Force a non-list, non-str by nesting under a table (invalid for our contract)
    f = write(
        tmp_path / "pyproject.toml",
        """
        [tool.jiggle_version.ignore]
        x = 1
        """,
    )
    # After parsing, jiggle_config["ignore"] will be a dict -> invalid -> dropped
    cfg = load_config_from_path(f)
    err = capsys.readouterr().err
    assert "ignore must be a list of paths or a string" in err
    assert "ignore" not in cfg


def test_invalid_toml_emits_warning_and_returns_empty(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    f = write(
        tmp_path / "pyproject.toml",
        "tool = { jiggle_version = { default_increment = } }",
    )
    cfg = load_config_from_path(f)
    assert cfg == {}
    err = capsys.readouterr().err
    assert "Could not parse" in err
    assert "pyproject.toml" in err


def test_no_tool_jiggle_version_returns_empty(tmp_path: Path):
    f = write(
        tmp_path / "pyproject.toml",
        """
        [project]
        name = "demo"
        version = "0.1.0"
        """,
    )
    cfg = load_config_from_path(f)
    assert cfg == {}
