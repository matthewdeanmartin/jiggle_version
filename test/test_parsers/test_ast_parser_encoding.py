from __future__ import annotations

from pathlib import Path

from jiggle_version.parsers.ast_parser import parse_dunder_all, parse_python_module


def test_parse_python_module_honors_pep263_encoding_cookie(tmp_path: Path):
    f = tmp_path / "module.py"
    source = (
        "# -*- coding: cp1252 -*-\n" '__version__ = "1.0.0"\n' 'LABEL = "caf\xe9"\n'
    )
    f.write_bytes(source.encode("cp1252"))

    assert parse_python_module(f) == "1.0.0"


def test_parse_dunder_all_honors_utf8_bom(tmp_path: Path):
    f = tmp_path / "__init__.py"
    f.write_text('__all__ = ["alpha", "beta"]\n', encoding="utf-8-sig")

    assert parse_dunder_all(f) == {"alpha", "beta"}
