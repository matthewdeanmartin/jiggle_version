# jiggle_version

Deterministic CLI to **discover**, **check**, and **bump** a project version without importing user code or writing
regex. Optional **autogit** (stage/commit/push). Supports **PEP 440** and **SemVer**. Includes an **auto** mode that
infers bump size from public API changes (`__all__`).

---

## Why this exists

Version values drift across `pyproject.toml`, `setup.cfg`, `setup.py`, and module files. Many tools import your package
or ask you to hand-write regex. This one does neither.

---

## Features

* **Discovery** across common sources:

    * `pyproject.toml` → `[project].version` (PEP 621) or `[tool.setuptools].version`
    * `setup.cfg` → `[metadata] version`
    * `setup.py` → static AST of `setup(version="...")`
    * Python modules → top-level `__version__ = "..."`, plus `_version.py`, `__version__.py`, `__about__.py`, package
      `__init__.py`
* **Agreement check** (CI-friendly, no writes)
* **Bump**: `major | minor | patch | auto` with `--scheme pep440|semver`
* **Auto mode**: diffs the union of `__all__` symbols to infer major/minor/patch; persists digest in
  `.jiggle_version.config`
* **Autogit**: `--autogit off|stage|commit|push` with templated commit message
* **Git-aware discovery**: honors `.gitignore`, repo excludes, and global gitignore; supports extra ignore paths
* **Zero-import** of target project; AST + safe text updates only
* **Deterministic exit codes** for automation

---

## Install

```bash
pipx install jiggle_version
# or
python -m pip install --user jiggle_version
```

**Python**: `>=3.8`

**Runtime deps** (runtime or conditional): `packaging`, `tomlkit`, `pathspec`, `rich-argparse` (help styling), `tomli`
on Python <3.11.

---

## Quick start

```bash
# From your project root
jiggle_version check
jiggle_version print
jiggle_version bump --increment patch --scheme pep440 --dry-run
jiggle_version bump --increment auto --autogit commit
```

Initialize default config:

```bash
jiggle_version init
```

---

## Configuration (pyproject.toml)

```toml
[tool.jiggle_version]
scheme = "pep440"            # "pep440" | "semver"
default_increment = "patch"  # "major" | "minor" | "patch" | "auto"
project_root = "."
ignore = ["docs/_build", "dist", ".venv"]  # optional

# Optional autogit defaults
autogit = "off"              # "off" | "stage" | "commit" | "push"
commit_message = "Release: {version}"
allow_dirty = false
```

Notes:

* CLI overrides config. Missing CLI args are filled from config.
* `ignore` is normalized to a list of relative paths.

---

## Commands

### `check`

Discover versions across sources and verify agreement. No writes.

```bash
jiggle_version check [--project-root .] [--ignore path ...]
```

### `print`

Print the normalized version if all sources agree.

```bash
jiggle_version print
```

### `inspect`

List all candidate files and run `check`.

```bash
jiggle_version inspect
```

### `bump`

Compute next version and update all writable sources.

```bash
jiggle_version bump \
  [--increment major|minor|patch|auto] \
  [--scheme pep440|semver] \
  [--set X.Y.Z] \
  [--force-write] \
  [--dry-run] \
  [--autogit off|stage|commit|push] \
  [--commit-message "Release: {version}"] \
  [--allow-dirty]
```

Behavior:

* If sources **disagree**, operation fails unless `--force-write` or `--set` is provided.
* `--set` skips bump logic and writes the explicit version everywhere.

### `hash-all`

Compute and persist API digest used by **auto** mode.

```bash
jiggle_version hash-all
# writes .jiggle_version.config (TOML)
```

### `init`

Append a default `[tool.jiggle_version]` section to `pyproject.toml`.

---

## Auto mode: how it decides

1. Walk project for `__all__` in Python modules (respecting `.gitignore` + `ignore`).
2. Build the set union of exported symbols; compare to last stored set in `.jiggle_version.config`.
3. Decide:

    * **major** if any previously exported symbol was removed
    * **minor** if new symbols were added (and nothing removed)
    * **patch** if identical or no `__all__` anywhere
4. After a successful, non–`--dry-run` bump, the digest is updated.

You can pre-seed the digest with `jiggle_version hash-all`.

---

## Git behavior

* No shelling out to `git` for ignore logic; uses `pathspec` with:

    * `<root>/.gitignore`
    * `<root>/.git/info/exclude`
    * `~/.config/git/ignore` or `~/.gitignore`
* Autogit uses `subprocess.run(..., check=True)`:

    * `stage` → `git add <changed files>`
    * `commit` → stage + `git commit -m "<message>"`
    * `push` → commit + `git push origin <current-branch>`
* Refuses to proceed if repo is dirty and autogit is requested, unless `--allow-dirty`.

---

## Exit codes (stable for CI)

**User / project issues (treated as “expected” for tests):**

* `100` — no version declarations found
* `102` — discovered versions disagree
* `103` — git repo dirty and `--allow-dirty` not set
* `104` — config not found where required

**Tool / unexpected failures:**

* `1` — unexpected error
* `2` — discovery error (I/O, traversal)
* `3` — auto-increment analysis error
* `4` — bump calculation error (invalid version/scheme)
* `5` — failed to update a file
* `6` — autogit failed
* `7` — hash/digest generation failed
* `8` — argparse error (invalid CLI)

Contract for test runners:

* Treat **>=100** as **user error** (assertable, not a tool crash).
* Treat **<100** as **application failure** (potential bug).

---

## Safety model

* Never imports or executes target project code.
* Python parsed via `ast`; setup parsing limited to literal `version="..."`.
* TOML via `tomllib`/`tomli`, INI via `configparser`, `tomlkit` used to preserve formatting on write.

---

## Semantics (bumping)

* **PEP 440** (default): increments numeric release segments; drops pre/dev/post markers on standard bump.
* **SemVer**: enforces `MAJOR.MINOR.PATCH`; strips pre-release/build on standard bump. (Flags to preserve/annotate can
  be added later.)

---

## CLI quality-of-life

* **Typo suggestions** for choice arguments (e.g., wrong subcommand/value).
* **Verbose logging**: `-v` → INFO, `-vv` → DEBUG; or `--log-level DEBUG`.
* Rich help text when `rich-argparse` is available.

---

## CI usage examples (GitHub Actions)

**Drift check (no writes):**

```yaml
- run: pipx install jiggle_version
- run: jiggle_version check
```

**Release bump (auto + autogit):**

```yaml
- run: pipx install jiggle_version
- run: jiggle_version hash-all
- run: jiggle_version bump --increment auto --autogit push
```

---

## Known limitations / non-goals

* Won’t evaluate dynamic `setup.py` logic (files, env, computed constants).
* Only updates known patterns; exotic version locations aren’t modified.
* Single, project-wide version policy (per-module versioning is out-of-scope for now).

---

## Troubleshooting

* **“No version found”**: ensure one of the supported sources exists and is literal.
* **“Versions disagree”**: run `jiggle_version inspect` to see sources; reconcile or use `--force-write` once.
* **Auto mode always “patch”**: ensure you actually export a public API via `__all__`.
* **Ignored paths not respected**: confirm entries in `pyproject.toml` under `[tool.jiggle_version].ignore` (list or
  string), and that `.gitignore` covers generated trees.

---

## Contributing

1. Add/adjust unit tests (no tests for logging needed).
2. Keep exit codes and CLI surfaces stable.
3. Prefer AST/TOML/INI approaches over regex.
4. Windows paths: avoid `shell=True`, prefer `Path` APIs.

---

## License

MIT. See `LICENSE`.

---

## Minimal API surface (for importers)

This is a CLI-first tool. Internal modules may change. If you import, prefer:

* `jiggle_version.__about__.__version__`
* Running via `python -m jiggle_version`
