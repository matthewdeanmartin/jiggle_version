from __future__ import annotations

import subprocess  # nosec
import sys
from pathlib import Path

import pytest

# Adjust if your module path differs
from jiggle_version.git import (
    _run_git_command,
    commit_changes,
    get_current_branch,
    is_repo_dirty,
    push_changes,
    stage_files,
)


class FakeCompleted:
    def __init__(self, stdout: str = "", returncode: int = 0):
        self.stdout = stdout
        self.returncode = returncode
        self.stderr = ""


# ---------- _run_git_command ----------


def test_run_git_command_invokes_git_with_args_and_returns_stdout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    calls: list[list[str]] = []

    def fake_which(cmd: str) -> str | None:
        assert cmd == "git"
        return "/usr/bin/git"

    def fake_run(argv, **kwargs):
        # capture invocation
        calls.append(argv)
        assert argv[:2] == ["git", "status"]  # prefix & first arg
        # typical kwargs expectations
        assert kwargs.get("cwd") == tmp_path
        assert kwargs.get("capture_output") is True
        assert kwargs.get("text") is True
        assert kwargs.get("check") is True
        return FakeCompleted(stdout="ok out\n")

    monkeypatch.setattr("jiggle_version.git.shutil.which", fake_which)
    monkeypatch.setattr("jiggle_version.git.subprocess.run", fake_run)

    out = _run_git_command(["status"], tmp_path)
    assert out == "ok out"
    assert calls == [["git", "status"]]


def test_run_git_command_raises_if_git_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr("jiggle_version.git.shutil.which", lambda _: None)
    with pytest.raises(RuntimeError, match="Git command not found"):
        _run_git_command(["status"], tmp_path)


def test_run_git_command_propagates_calledprocesserror(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr("jiggle_version.git.shutil.which", lambda _: "/usr/bin/git")

    def fake_run(*args, **kwargs):
        raise subprocess.CalledProcessError(
            returncode=128, cmd=args[0], output="", stderr="fatal"
        )

    monkeypatch.setattr("jiggle_version.git.subprocess.run", fake_run)

    with pytest.raises(subprocess.CalledProcessError):
        _run_git_command(["rev-parse", "HEAD"], tmp_path)


# ---------- is_repo_dirty ----------


def test_is_repo_dirty_true_when_status_has_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    # monkeypatch internal helper to avoid re-testing it
    monkeypatch.setattr(
        "jiggle_version.git._run_git_command", lambda args, cwd: " M file.py\n"
    )
    assert is_repo_dirty(tmp_path) is True


def test_is_repo_dirty_false_when_status_clean(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr("jiggle_version.git._run_git_command", lambda args, cwd: "")
    assert is_repo_dirty(tmp_path) is False


def test_is_repo_dirty_false_on_calledprocesserror(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    def raiser(*_, **__):
        raise subprocess.CalledProcessError(returncode=128, cmd=["git", "status"])

    monkeypatch.setattr("jiggle_version.git._run_git_command", raiser)
    assert is_repo_dirty(tmp_path) is False


# ---------- get_current_branch ----------


def test_get_current_branch_returns_stripped_stdout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(
        "jiggle_version.git._run_git_command", lambda args, cwd: "main\n"
    )
    assert get_current_branch(tmp_path).strip() == "main"


# ---------- stage/commit/push wiring ----------
@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows, slashes")
def test_stage_files_uses_relative_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    root = tmp_path
    a = root / "pkg" / "a.py"
    b = root / "pkg" / "sub" / "b.py"
    a.parent.mkdir(parents=True, exist_ok=True)
    a.write_text("x")
    b.parent.mkdir(parents=True, exist_ok=True)
    b.write_text("y")

    recorded: dict[str, list[str]] = {}

    def fake_run_git_command(args: list[str], cwd: Path) -> str:
        recorded["args"] = args
        recorded["cwd"] = [str(cwd)]
        return ""

    monkeypatch.setattr("jiggle_version.git._run_git_command", fake_run_git_command)

    stage_files(root, [a, b])
    # Expect: ["add", "pkg/a.py", "pkg/sub/b.py"]
    assert recorded["args"][0] == "add"
    assert set(recorded["args"][1:]) == {"pkg/a.py", "pkg/sub/b.py"}
    assert recorded["cwd"] == [str(root)]


def test_commit_changes_passes_message(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    captured = {}

    def fake(cmd: list[str], cwd: Path) -> str:
        captured["cmd"] = cmd
        captured["cwd"] = cwd
        return ""

    monkeypatch.setattr("jiggle_version.git._run_git_command", fake)
    commit_changes(tmp_path, "feat: add cool thing")
    assert captured["cmd"][:2] == ["commit", "-m"]
    assert captured["cmd"][2] == "feat: add cool thing"
    assert captured["cwd"] == tmp_path


def test_push_changes_passes_remote_and_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    captured = {}

    def fake(cmd: list[str], cwd: Path) -> str:
        captured["cmd"] = cmd
        captured["cwd"] = cwd
        return ""

    monkeypatch.setattr("jiggle_version.git._run_git_command", fake)
    push_changes(tmp_path, "origin", "main")
    assert captured["cmd"] == ["push", "origin", "main"]
    assert captured["cwd"] == tmp_path
