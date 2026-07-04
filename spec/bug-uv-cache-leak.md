# Bug: discovery leaks into `.uv/` cache dir (nested `.gitignore` not honored)

## Status

Open. Sibling of the "venv-leak" fix already in the v2.2.0 branch — same symptom
(installed-package version files producing false version conflicts) but a
**different root cause** that the venv-root pruning does not cover.

## Symptom

In a project that keeps a **project-local uv cache** at `./.uv/`, `jiggle_version
check` fails with a false conflict:

```
❌ Version conflict detected: 2 versions found (0.1.9, 1.27.0)
Found 7 potential source file(s).
-> Checking for version in '.uv\archive-v0\Uzja_...\hatchling\__about__.py'…
✅ Found version: 1.27.0        # <-- hatchling's version, from the uv cache
-> Checking for version in 'examexam\__about__.py'…
✅ Found version: 0.1.9         # <-- the actual project version
```

Discovery descends into `.uv/archive-v0/.../hatchling/__about__.py` (and would
also match `pluggy/_version.py` etc.), so the project's real `0.1.9` collides
with hatchling's `1.27.0`.

Reproduced in `C:\github\examexam` (has `[tool.uv]` in `pyproject.toml`; uv writes
its cache to `./.uv/`).

## Root cause

Two independent gaps, either of which would have prevented this:

### 1. Nested `.gitignore` files are not read (primary)

`gitignore.py::build_gitignore_spec` only reads:

- `<project_root>/.gitignore`
- `<project_root>/.git/info/exclude`
- global excludes

It does **not** read nested `.gitignore` files. uv drops a
`./.uv/.gitignore` containing a single `*`, so **git itself ignores the entire
cache**:

```console
$ git check-ignore ".uv/archive-v0/.../hatchling/__about__.py"
.uv/archive-v0/.../hatchling/__about__.py      # git ignores it
```

But jiggle_version never sees that nested rule, walks in anyway, and finds the
cached package's version file. The tool advertises ".gitignore awareness" but
only honors the top-level file, so it diverges from real git semantics whenever a
subtree carries its own `.gitignore`.

### 2. `CACHEDIR.TAG` is ignored (secondary / defense-in-depth)

`./.uv/CACHEDIR.TAG` marks the directory as a cache under the well-known
[Cache Directory Tagging Standard](https://bford.info/cachedir/):

```
Signature: 8a477f597d28d172789f06886806bc55
```

Backup and search tools skip any directory containing this file. jiggle_version
does not check for it. `discover.py::VENV_MARKER_FILES` already establishes the
"marker file means prune this directory" pattern; `CACHEDIR.TAG` is the same idea
for caches.

### Why the existing venv-leak fix misses this

The v2.2.0 branch prunes directories that contain `pyvenv.cfg`, plus
`site-packages` / `node_modules`. `.uv/` is none of those — it is a package
cache, not a venv, and its package files live under
`archive-v0/<hash>/<pkg>/…`, not under `site-packages/`. So it slips through.

## Suggested fix

Any one of these closes the reported case; doing (A) is the most correct because
it makes jiggle_version agree with git in general, and (B) is cheap
defense-in-depth. (C) is a stopgap.

- **(A) Honor nested `.gitignore` files.** During the walk, when entering a
  directory that contains a `.gitignore`, layer its patterns onto the active
  `PathSpec` (anchored to that subdir), matching git's cascading semantics. This
  also fixes the general "we claim gitignore awareness but only read the root
  file" divergence.

- **(B) Prune `CACHEDIR.TAG` directories.** In `_walk_and_discover`, skip any
  directory containing a `CACHEDIR.TAG` whose first line is
  `Signature: 8a477f597d28d172789f06886806bc55`. Mirrors the existing
  `VENV_MARKER_FILES` check; ~4 lines.

- **(C) Add `.uv` to `DEFAULT_IGNORE_DIRS`.** Narrow and uv-specific; least
  principled but trivially unblocks users. Note the venv-leak fix already had to
  special-case names, so this is consistent with current style.

Recommendation: ship **(A) + (B)** together. (A) is the real fix; (B) protects
against any other cache dir (pip, hatch, mypy, ruff, etc.) that tags itself but
isn't gitignored.

## Test ideas

Add to the discovery tests:

- Project with `./.uv/.gitignore` (`*`) containing
  `./.uv/archive-v0/x/hatchling/__about__.py` → that file is **not** discovered;
  `check` sees only the project version → exit 0.
- Project with `./somecache/CACHEDIR.TAG` (correct signature) plus a
  `__about__.py` inside it → not discovered.
- Nested `.gitignore` deeper than root (e.g. `pkg/vendored/.gitignore` with `*`)
  correctly prunes → regression guard for (A).

## Environment

- jiggle_version invoked via `uv run jiggle_version check` in `examexam`.
- Windows 11; project-local uv cache at `.\.uv\` created because
  `pyproject.toml` has a `[tool.uv]` table.
- The user (jiggle_version maintainer) confirms uv's behavior is correct and
  intended; jiggle_version should be the side that learns to skip the cache.
