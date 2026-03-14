from __future__ import annotations

import textwrap
from pathlib import Path

from jiggle_version.bump import bump_version
from jiggle_version.parsers.ast_parser import parse_python_module, parse_setup_py
from jiggle_version.parsers.config_parser import parse_pyproject_toml, parse_setup_cfg
from jiggle_version.update import (
    update_pyproject_toml,
    update_python_file,
    update_setup_cfg,
)


def write(path: Path, body: str) -> Path:
    path.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
    return path


def test_update_pyproject_toml_updates_project_version(tmp_path: Path):
    file_path = write(
        tmp_path / "pyproject.toml",
        """
        [project]
        name = "demo"
        version = "1.2.3"
        """,
    )

    update_pyproject_toml(file_path, "2.0.0")

    assert parse_pyproject_toml(file_path) == "2.0.0"


def test_update_pyproject_toml_updates_setuptools_fallback(tmp_path: Path):
    file_path = write(
        tmp_path / "pyproject.toml",
        """
        [tool.setuptools]
        version = "1.2.3"
        """,
    )

    update_pyproject_toml(file_path, "2.0.0")

    assert parse_pyproject_toml(file_path) == "2.0.0"


def test_update_pyproject_toml_preserves_existing_comments(tmp_path: Path):
    file_path = write(
        tmp_path / "pyproject.toml",
        """
        [project]
        # Keep this comment.
        version = "1.2.3"
        """,
    )

    update_pyproject_toml(file_path, "1.2.4")

    updated = file_path.read_text(encoding="utf-8")
    assert "# Keep this comment." in updated
    assert 'version = "1.2.4"' in updated


def test_update_setup_cfg_changes_only_metadata_version_and_keeps_comment(
    tmp_path: Path,
):
    file_path = write(
        tmp_path / "setup.cfg",
        """
        [metadata]
        version = 1.2.3  # shipped

        [tool:pytest]
        version = 9.9.9
        """,
    )

    update_setup_cfg(file_path, "2.0.0")

    updated = file_path.read_text(encoding="utf-8")
    assert "version = 2.0.0  # shipped" in updated
    assert "[tool:pytest]\nversion = 9.9.9" in updated


def test_update_setup_cfg_noop_without_metadata_version(tmp_path: Path):
    file_path = write(
        tmp_path / "setup.cfg",
        """
        [metadata]
        name = demo
        """,
    )
    before = file_path.read_text(encoding="utf-8")

    update_setup_cfg(file_path, "2.0.0")

    assert file_path.read_text(encoding="utf-8") == before


def test_update_python_file_preserves_dunder_quote_style(tmp_path: Path):
    file_path = write(
        tmp_path / "__init__.py",
        """
        __version__ = '1.2.3'
        """,
    )

    update_python_file(file_path, "2.0.0")

    updated = file_path.read_text(encoding="utf-8")
    assert "__version__ = '2.0.0'" in updated
    assert parse_python_module(file_path) == "2.0.0"


def test_update_python_file_updates_setup_py_keyword_version(tmp_path: Path):
    file_path = write(
        tmp_path / "setup.py",
        """
        from setuptools import setup

        setup(name="demo", version='1.2.3')
        """,
    )

    update_python_file(file_path, "2.0.0")

    updated = file_path.read_text(encoding="utf-8")
    assert "version='2.0.0'" in updated
    assert parse_setup_py(file_path) == "2.0.0"


def test_update_python_file_leaves_unrelated_names_alone(tmp_path: Path):
    file_path = write(
        tmp_path / "module.py",
        """
        minimum_version = "0.1.0"
        conversion = "keep me"
        __version__ = "1.2.3"
        """,
    )

    update_python_file(file_path, "2.0.0")

    updated = file_path.read_text(encoding="utf-8")
    assert 'minimum_version = "0.1.0"' in updated
    assert 'conversion = "keep me"' in updated
    assert parse_python_module(file_path) == "2.0.0"


def test_bump_version_dispatches_to_supported_schemes():
    assert bump_version("1.2.3", "patch", "pep440") == "1.2.4"
    assert bump_version("1.2.3", "minor", "semver") == "1.3.0"


def test_bump_version_rejects_unknown_scheme():
    try:
        bump_version("1.2.3", "patch", "calver")
    except ValueError as exc:
        assert "Unknown versioning scheme" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown scheme")
