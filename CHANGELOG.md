# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-10-06

### Added

- Checks pypi to see if current version is published. Don't bump if unpublished. Otherwise, if you run this on every
  time you run your Makefile or Justfile, you'll have version number gaps

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