from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from jiggle_version.parsers.ast_parser import (
    parse_dunder_all,
    parse_python_module,
    parse_setup_py,
)

# ---------- helpers ----------


def write(tmp: Path, name: str, body: str) -> Path:
    p = tmp / name
    p.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
    return p


# ---------- parse_setup_py ----------


def test_parse_setup_py_literal_version(tmp_path: Path):
    f = write(
        tmp_path,
        "setup.py",
        """
        from setuptools import setup
        setup(name="pkg", version="1.2.3")
        """,
    )
    assert parse_setup_py(f) == "1.2.3"


def test_parse_setup_py_attribute_call(tmp_path: Path):
    f = write(
        tmp_path,
        "setup.py",
        """
        import setuptools
        setuptools.setup(name="x", version="0.0.9")
        """,
    )
    assert parse_setup_py(f) == "0.0.9"


def test_parse_setup_py_non_literal_version_warns_and_returns_none(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    f = write(
        tmp_path,
        "setup.py",
        """
        from setuptools import setup
        VERSION = "3.4.5"
        setup(name="pkg", version=VERSION)
        """,
    )
    assert parse_setup_py(f) is None
    out = capsys.readouterr().out  # warning is printed via print(), not logging
    assert "Could not statically parse 'version' in setup.py" in out


def test_parse_setup_py_missing_file_returns_none(tmp_path: Path):
    assert parse_setup_py(tmp_path / "nope_setup.py") is None


def test_parse_setup_py_syntax_error_returns_none_and_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    f = write(
        tmp_path,
        "setup.py",
        """
        from setuptools import setup
        setup(name="x", version="1.2.3"  # missing closing paren
        """,
    )
    assert parse_setup_py(f) is None
    err = capsys.readouterr().err
    assert "Could not parse" in err
    assert "setup.py" in err


# ---------- parse_python_module (for __version__) ----------


def test_parse_python_module_literal_dunder_version(tmp_path: Path):
    f = write(
        tmp_path,
        "module.py",
        """
        __version__ = "0.1.0"
        """,
    )
    assert parse_python_module(f) == "0.1.0"


def test_parse_python_module_last_assignment_wins(tmp_path: Path):
    f = write(
        tmp_path,
        "module.py",
        """
        __version__ = "0.1.0"
        __version__ = "0.2.0"
        """,
    )
    # AST visit order sets to the last seen literal
    assert parse_python_module(f) == "0.2.0"


def test_parse_python_module_non_literal_warns_and_returns_none(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    f = write(
        tmp_path,
        "module.py",
        """
        VERSION = "9.9.9"
        __version__ = VERSION
        """,
    )
    assert parse_python_module(f) is None
    out = capsys.readouterr().out
    assert "Found `__version__` but its value was not a literal." in out


def test_parse_python_module_ignores_other_assignments(tmp_path: Path):
    f = write(
        tmp_path,
        "module.py",
        """
        something_else = "1.0.0"
        """,
    )
    assert parse_python_module(f) is None


def test_parse_python_module_missing_file_returns_none(tmp_path: Path):
    assert parse_python_module(tmp_path / "nope.py") is None


def test_parse_python_module_syntax_error_returns_none_and_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    f = write(
        tmp_path,
        "module.py",
        """
        __version__ = "0.1.0
        """,
    )
    assert parse_python_module(f) is None
    err = capsys.readouterr().err
    assert "Could not parse" in err
    assert "module.py" in err


# ---------- parse_dunder_all ----------


@pytest.mark.parametrize(
    "rhs,expected",
    [
        ("['a', 'b', 'c']", {"a", "b", "c"}),
        ("('a', 'b')", {"a", "b"}),
        ("[]", set()),
        ("()", set()),
    ],
)
def test_parse_dunder_all_list_and_tuple_literals(
    tmp_path: Path, rhs: str, expected: set[str]
):
    f = write(
        tmp_path,
        "mod.py",
        f"""
        __all__ = {rhs}
        """,
    )
    assert parse_dunder_all(f) == expected


def test_parse_dunder_all_non_literal_warns_and_returns_empty(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    f = write(
        tmp_path,
        "mod.py",
        """
        NAMES = ["x", "y"]
        __all__ = ["a"] + NAMES
        """,
    )
    # literal_eval fails -> warning printed -> symbols remain empty
    assert parse_dunder_all(f) == set()
    out = capsys.readouterr().out
    assert "Found `__all__` but its value was not a literal list/tuple." in out


def test_parse_dunder_all_no_assignment_returns_empty(tmp_path: Path):
    f = write(
        tmp_path,
        "mod.py",
        """
        def f(): pass
        """,
    )
    assert parse_dunder_all(f) == set()


def test_parse_dunder_all_syntax_error_returns_empty(tmp_path: Path):
    f = write(
        tmp_path,
        "mod.py",
        """
        __all__ = ["a", 
        """,
    )
    assert parse_dunder_all(f) == set()
