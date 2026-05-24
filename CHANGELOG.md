# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-05-24

### Added

- `check --git-tag`: compares the agreed source version against the most recent
  git tag reachable from HEAD (`git describe --tags --abbrev=0`). A leading
  `v`/`V` is stripped before comparison. Exits `102` on mismatch; exits `0`
  with an informational note when no tags exist. Opt-in flag; existing pipelines
  are unaffected.

### Fixed

- Version discovery no longer walks into virtual-environment roots. Any
  directory containing a `pyvenv.cfg` file (the standard venv marker written by
  pip, uv, and virtualenv) is skipped entirely, eliminating false
  version-conflict errors from installed-package `_version.py` /
  `__version__.py` files in ad-hoc venvs that are not covered by `.gitignore`
  (e.g. `.blerg`, custom-named envs). `site-packages` and `node_modules` are
  also added to the unconditional prune list.

## [2.1.1] - 2026-3-14

### Added

- `--quiet` option

### Fixed

- UTF error on some machines on printing output with UTF-8.

## [2.1.0] - 2025-10-06

### Added

- Checks pypi to see if current version is published. Don't bump if unpublished. Otherwise, if you run this on every
  time you run your Makefile or Justfile, you'll have version number gaps
- Fixed another missing dependency.

## [2.0.1] - 2025-10-05

### Fixed

- Fixed missing dependency in pyproject.toml

## [2.0.0] - 2025-10-05

### Added

- New commands, 100% code rewrite, same general design goals.

### Changed

- signature of bump command changed

### Removed

- current command removed replaced with others

## [0.1.2] - 2025-10-05

### Fixed

- Python 3.13 support.
- Last version before complete rewrite.