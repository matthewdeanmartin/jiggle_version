from __future__ import annotations

from pathlib import Path

from jiggle_version.discover import find_source_files


def write(p: Path, text: str = "") -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def test_find_source_files_skips_unreadable_directory(
    tmp_path: Path, monkeypatch
) -> None:
    root = tmp_path
    write(root / "pyproject.toml", '[project]\nversion = "0.1.0"\n')
    blocked_dir = root / ".tmp" / "pytest"
    blocked_dir.mkdir(parents=True)
    write(blocked_dir / "__version__.py", "__version__='9.9.9'")

    original_iterdir = Path.iterdir

    def fake_iterdir(self: Path):
        if self == blocked_dir:
            raise PermissionError("[WinError 5] Access is denied")
        return original_iterdir(self)

    monkeypatch.setattr(Path, "iterdir", fake_iterdir)

    files = find_source_files(root)

    names = {p.relative_to(root).as_posix() for p in files}
    assert "pyproject.toml" in names
    assert ".tmp/pytest/__version__.py" not in names
