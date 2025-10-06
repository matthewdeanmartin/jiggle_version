# jiggle_version/git.py
"""
Wrappers for executing Git commands via subprocess.
"""
from __future__ import annotations

import shutil
import subprocess  # nosec
from pathlib import Path


def _run_git_command(args: list[str], cwd: Path) -> str:
    """Helper to run a Git command and return its output."""
    if not shutil.which("git"):
        raise RuntimeError(
            "Git command not found. Please ensure Git is installed and in your PATH."
        )

    result = subprocess.run(  # nosec
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,  # Raise an exception if the command fails
    )
    return result.stdout.strip()


def is_repo_dirty(project_root: Path) -> bool:
    """Checks if the Git repository has uncommitted changes."""
    try:
        status_output = _run_git_command(["status", "--porcelain"], project_root)
        return bool(status_output)
    except subprocess.CalledProcessError:
        # This can happen if not in a git repo
        return False


def get_current_branch(project_root: Path) -> str:
    """Gets the current Git branch name."""
    return _run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], project_root)


def stage_files(project_root: Path, files: list[Path]) -> None:
    """Stages the specified files in Git."""
    file_paths = [str(f.relative_to(project_root)) for f in files]
    _run_git_command(["add", *file_paths], project_root)


def commit_changes(project_root: Path, message: str) -> None:
    """Creates a commit with the given message."""
    _run_git_command(["commit", "-m", message], project_root)


def push_changes(project_root: Path, remote: str, branch: str) -> None:
    """Pushes changes to the specified remote and branch."""
    _run_git_command(["push", remote, branch], project_root)
