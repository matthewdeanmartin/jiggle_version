# v2.2.0 — Release Spec

## Goal

Ship the venv-leak bug fix from the current branch together with one meaningful
new feature so the release is worth the version bump.

---

## Bug fix already in branch

**Venv root pruning** (`discover.py`)

- Directories containing `pyvenv.cfg` are now recognized as virtual-environment
  roots and skipped entirely during file discovery.
- `site-packages` and `node_modules` added to the unconditional prune list.
- Effect: eliminates false version-conflict errors caused by installed-package
  `_version.py` / `__version__.py` files in ad-hoc venvs (`.blerg`, custom
  named envs not covered by `.gitignore`).

---

## New feature for v2.2.0 — Git tag awareness (check command)

### Problem

After `jiggle_version bump` writes a new version to source files, there is no
check that the version is consistent with the git tag that will be (or was)
created for the release.  Projects that push a `vX.Y.Z` tag manually can end up
with the tag and the source files disagreeing silently.

### What to build

Extend `check` with an optional `--git-tag` flag:

```
jiggle_version check --git-tag
```

Behaviour:

1. Run normal multi-file agreement check as today.
2. Ask git for the most recent tag reachable from `HEAD`
   (`git describe --tags --abbrev=0`).
3. If a tag exists, strip a leading `v` / `V` and compare the normalized version
   to the agreed source version.
4. On mismatch → print a clear warning and exit `102` (VERSION_DISAGREEMENT),
   same code as a source-file conflict.
5. If no tag exists → print an informational note and exit `0` (not an error;
   many projects tag only at release time).
6. `--git-tag` is opt-in so existing CI pipelines are unaffected.

### Why this feature

- Directly addresses the "git tag awareness/sync" item in `docs/todo.md`.
- Additive, opt-in, no breaking changes.
- Small surface area: one new flag, one new call into the existing `git.py`
  wrapper, a handful of lines in `handle_check`.
- Gives users a single command that validates both file-level and tag-level
  consistency before a release.

### Implementation sketch

**`git.py`** — add one function:
```python
def get_latest_tag(project_root: Path) -> str | None:
    """Return the most recent tag reachable from HEAD, or None."""
    # git describe --tags --abbrev=0
    # return None on CalledProcessError (no tags)
```

**`__main__.py` — `handle_check`**:
- Add `--git-tag` boolean arg to the `check` subparser.
- After the existing agreement block, if `args.git_tag`:
  - Call `get_latest_tag`.
  - Normalize the tag (strip `v`/`V`, run through `packaging.version.Version`).
  - Compare to `agreed_version`; emit warning + return `VERSION_DISAGREEMENT`
    on mismatch.

**Tests** — add to `test/test_git.py` or a new `test/test_check_git_tag.py`:
- Repo with matching tag → exit 0.
- Repo with mismatched tag → exit 102.
- Repo with no tags → exit 0.
- Tag with leading `v` → normalized correctly.

### Exit-code table addition

| Code | Meaning |
|------|---------|
| 102  | Version disagreement (files, or files vs git tag) |

No new exit code needed; 102 already covers "versions disagree."

---

## What is explicitly deferred

The following ideas came up in research but are **not** in this release:

| Item | Why deferred |
|------|-------------|
| Scheme normalization before string comparison (TODO at `__main__.py:180`) | Correctness gain is real but the normalization rules interact with SemVer vs PEP 440 selection; warrants its own release to avoid regressions. |
| Pre-commit hook integration | Useful but purely additive docs/config work; no code change needed now. |
| `init` comment-preservation improvements | Low user impact; tomlkit already handles the common case. |
| Coverage push to 50 %+ | Ongoing; not blocking a release. |

---

## Release checklist

- [ ] Venv-leak fix merged and tested (all existing + new `test_skips_venv_roots` pass)
- [ ] `--git-tag` flag implemented and tested
- [ ] CHANGELOG.md entry written for 2.2.0
- [ ] `__about__.py` / `pyproject.toml` version bumped to 2.2.0
- [ ] `jiggle_version check` passes on this repo itself
