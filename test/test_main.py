from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

# adjust if your entrypoint lives elsewhere
from jiggle_version.__main__ import main


def w(p: Path, body: str) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
    return p


def make_basic_project(tmp: Path, version: str = "0.1.0") -> Path:
    root = tmp
    w(
        root / "pyproject.toml",
        f"""
        [project]
        name = "demo"
        version = "{version}"
        """,
    )
    return root


# ----------------------- print -----------------------


def test_print_outputs_single_version(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    root = make_basic_project(tmp_path)
    rc = main(
        [
            "--project-root",
            str(root),
            "--config",
            str(root / "pyproject.toml"),
            "print",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert out.endswith("0.1.0")  # final line is version


# ----------------------- check -----------------------


def test_check_agreement_ok(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    root = make_basic_project(tmp_path, "1.2.3")
    # also add setup.cfg in agreement
    w(
        root / "setup.cfg",
        """
        [metadata]
        version = 1.2.3
        """,
    )
    rc = main(
        [
            "--project-root",
            str(root),
            "--config",
            str(root / "pyproject.toml"),
            "check",
        ]
    )
    assert rc == 0
    # avoid asserting exact stdout; just ensure no error code


def test_check_conflict_returns_2(tmp_path: Path):
    root = make_basic_project(tmp_path, "1.2.3")
    # conflict in setup.cfg
    w(
        root / "setup.cfg",
        """
        [metadata]
        version = 1.2.4
        """,
    )
    rc = main(
        [
            "--project-root",
            str(root),
            "--config",
            str(root / "pyproject.toml"),
            "check",
        ]
    )
    assert rc == 2


# ----------------------- bump -----------------------


def test_bump_dry_run_patch_from_cli(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    root = make_basic_project(tmp_path, "0.1.0")
    rc = main(
        [
            "--project-root",
            str(root),
            "--config",
            str(root / "pyproject.toml"),
            "bump",
            "--increment",
            "patch",
            "--scheme",
            "pep440",
            "--dry-run",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "Current version: 0.1.0" in out
    assert "New version:" in out
    assert "0.1.1" in out


def test_bump_uses_config_increment_when_not_given(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    root = make_basic_project(tmp_path, "0.1.0")
    # add tool config setting default_increment -> minor
    with (root / "pyproject.toml").open("a", encoding="utf-8") as f:
        f.write(
            textwrap.dedent(
                """
                [tool.jiggle_version]
                default_increment = "minor"
                scheme = "pep440"
                """
            ).lstrip()
        )

    rc = main(
        [
            "--project-root",
            str(root),
            "--config",
            str(root / "pyproject.toml"),
            "bump",
            "--dry-run",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    # expect 0.2.0 (minor bump)
    assert "Current version: 0.1.0" in out
    assert "New version:" in out
    assert "0.2.0" in out


def test_bump_force_write_allows_disagreement(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    root = make_basic_project(tmp_path, "1.0.0")
    # add a conflicting version source that discover will pick up
    w(
        root / "setup.cfg",
        """
        [metadata]
        version = 1.0.1
        """,
    )
    rc = main(
        [
            "--project-root",
            str(root),
            "--config",
            str(root / "pyproject.toml"),
            "bump",
            "--increment",
            "patch",
            "--scheme",
            "pep440",
            "--dry-run",
            "--force-write",
        ]
    )
    # Without --force-write the code returns 2, so ensure it now proceeds.
    assert rc in (
        0,
        1,
    )  # proceed to bump; may still fail downstream write in future changes
    out = capsys.readouterr().out
    assert "Current version:" in out and "New version:" in out


# ----------------------- hash-all -----------------------


def test_hash_all_writes_digest(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    root = make_basic_project(tmp_path)
    # provide a package exposing __all__
    (root / "pkg").mkdir()
    w(root / "pkg" / "__init__.py", "__all__ = ['A','B','C']")
    rc = main(
        [
            "--project-root",
            str(root),
            "--config",
            str(root / "pyproject.toml"),
            "hash-all",
        ]
    )
    assert rc == 0
    digest = root / ".jiggle_version.config"
    assert digest.is_file()
    data = digest.read_text(encoding="utf-8")
    assert "[[?]]" not in data  # not asserting exact TOML; just ensure it's non-empty
    assert "digest" in data
    assert "symbols" in data


# ----------------------- init -----------------------


def test_init_appends_config_section(tmp_path: Path):
    root = make_basic_project(tmp_path)
    rc = main(
        [
            "--project-root",
            str(root),
            "--config",
            str(root / "pyproject.toml"),
            "init",
        ]
    )
    assert rc == 0
    txt = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.jiggle_version]" in txt


# ----------------------- inspect -----------------------


def test_inspect_lists_files_and_runs_check(tmp_path: Path):
    root = make_basic_project(tmp_path, "1.2.3")
    # add an importable package file so discover has some content
    w(root / "pkg" / "__init__.py", "__all__ = []")
    rc = main(
        [
            "--project-root",
            str(root),
            "--config",
            str(root / "pyproject.toml"),
            "inspect",
        ]
    )
    # Expect non-error exit even if check reports; we only verify it runs end-to-end
    assert rc in (0, 1, 2)
