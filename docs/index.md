# jiggle_version

`jiggle_version` discovers version declarations in a Python project, checks that
they agree, and can update them together. It reads source files without importing
the target project or relying on a user-written regex.

Install with `pipx install jiggle_version` or `python -m pip install jiggle_version`.
Python 3.11 or newer is required.

```shell
jiggle_version check
jiggle_version print
jiggle_version bump --increment patch --scheme pep440 --dry-run
```

`check` and `print` are read-only. The `--dry-run` example previews a bump without
writing. For commands that write to files, see the [CLI guide](cli.md).

The [homepage](https://matthewdeanmartin.github.io/jiggle_version/) illustrates
the version agreement workflow. The [source repository](https://github.com/matthewdeanmartin/jiggle_version)
contains the full README, tests, and changelog.
