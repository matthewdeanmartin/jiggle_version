# CLI guide

Run commands from the root of the Python project whose version you want to manage.

## Inspect before changing

```shell
jiggle_version inspect
jiggle_version check
jiggle_version print
```

`inspect` lists candidate files and checks agreement. `check` verifies that all
discovered version declarations agree. `print` emits the agreed version. Pass
`--git-tag` to `check` to compare against the nearest reachable Git tag.

## Preview and bump

```shell
jiggle_version bump --increment patch --scheme pep440 --dry-run
jiggle_version bump --increment patch --scheme pep440
```

The first command previews the next version. The second updates recognized
version declarations. If sources disagree, a bump fails unless `--force-write`
or `--set` is provided. `--set X.Y.Z` writes an explicit version.

`--autogit off` is the default. Opt-in values `stage`, `commit`, and `push` can
perform the corresponding Git operations after a bump. Review the file changes
before choosing one of those modes.

## Configuration

```toml
[tool.jiggle_version]
scheme = "pep440"
default_increment = "patch"
ignore = ["docs/_build", "dist", ".venv"]
autogit = "off"
```

`jiggle_version init` adds a default configuration section to `pyproject.toml`.
`hash-all` writes the API digest used by auto increment mode to
`.jiggle_version.config`. See the repository
[README](https://github.com/matthewdeanmartin/jiggle_version#readme) for the full
option and exit-code reference.
