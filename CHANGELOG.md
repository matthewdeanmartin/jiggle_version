# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Pin to Python 3.13 support

## [2.2.0] - 2026-05-24

### Added

- Git tag checking via `check --git-tag` command: compares the agreed source version against the most recent git tag reachable from HEAD (`git describe --tags --abbrev=0`). A leading `v`/`V` is stripped before comparison. Exits `102` on mismatch; exits `0` with an informational note when no tags exist. Opt-in flag; existing pipelines are unaffected.

### Fixed

- Version discovery no longer walks into virtual-environment roots. Any directory containing a `pyvenv.cfg` file (the standard venv marker written by pip, uv, and virtualenv) is skipped entirely, eliminating false version-conflict errors from installed-package `_version.py` / `__version__.py` files in ad-hoc venvs not covered by `.gitignore`. `site-packages` and `node_modules` are also added to the unconditional prune list.

## [2.1.1] - 2026-03-27

### Added

- Quiet option

### Fixed

- UTF-8 error on printing output

## [2.1.0] - 2025-10-20

### Added

- Python 3.14 support
- Checks PyPI to see if current version is published. Skips bump if version is unpublished to avoid version number gaps when running on every Makefile or Justfile invocation.

### Fixed

- Missing packaging library dependency

## [2.0.1] - 2025-10-06

### Fixed

- Missing dependency in pyproject.toml

## [2.0.0] - 2025-10-06

### Added

- 100% code rewrite with new commands

### Changed

- Command signature changed

### Removed

- Removed current command, replaced with others

## [1.2.0] - 2025-10-05

### Added

- Python 3.14 compatibility

### Changed

- Replace die() utility with JiggleVersionException for cleaner error propagation
- Switch version metadata to __about__.py and use Path-based arguments internally
- Fix keyword typo in package metadata (verision-numbers → version-numbers)

## [1.1.0] - 2023-05-28

### Added

- Update to Python 3.11 and Actions
- MyPyC compilation support

### Changed

- Build script improvements

## [1.0.77] - 2021-12-11

### Added

- Vendor versio library (comparable_mixin, version, version_scheme) to support version comparison logic

## [1.0.76] - 2021-12-06

### Added

- New build script

### Changed

- Documentation improvements

## [1.0.71] - 2020-05-23

### Fixed

- Close file handles

## [1.0.70] - 2020-02-09

### Added

- Python 3 only support

### Fixed

- Fix formatting issues

## [1.0.68] - 2019-01-11

### Added

- Force choice of module option
- Init feature for version file initialization

### Fixed

- Fix bug causing incorrect behavior on certain path configurations
- Remove extraneous PyCharm IDE files accidentally included in the PyPI distribution

## [0.1.2] - 2025-10-05

### Fixed

- Python 3.13 support
- Last version before complete rewrite

[Unreleased]: https://github.com/matthewdeanmartin/jiggle_version/compare/v2.2.0...HEAD
[2.2.0]: https://github.com/matthewdeanmartin/jiggle_version/compare/v2.1.1...v2.2.0
[2.1.1]: https://github.com/matthewdeanmartin/jiggle_version/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/matthewdeanmartin/jiggle_version/compare/v2.0.1...v2.1.0
[2.0.1]: https://github.com/matthewdeanmartin/jiggle_version/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/matthewdeanmartin/jiggle_version/compare/v1.2.0...v2.0.0
[1.2.0]: https://github.com/matthewdeanmartin/jiggle_version/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/matthewdeanmartin/jiggle_version/compare/v1.0.77...v1.1.0
[1.0.77]: https://github.com/matthewdeanmartin/jiggle_version/compare/v1.0.76...v1.0.77
[1.0.76]: https://github.com/matthewdeanmartin/jiggle_version/compare/v1.0.71...v1.0.76
[1.0.71]: https://github.com/matthewdeanmartin/jiggle_version/compare/v1.0.70...v1.0.71
[1.0.70]: https://github.com/matthewdeanmartin/jiggle_version/compare/v1.0.68...v1.0.70
[1.0.68]: https://github.com/matthewdeanmartin/jiggle_version/releases/tag/v1.0.68
