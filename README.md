# jiggle_version

Version bumper that finds version numbers in source code and increases the build number by modifying source.

With jiggle-version, the source code is authoritative, as compared to some tools where the source control tag is authoritative, or the pyproject.toml is authoritative.

This tool was written before pyproject.toml was a well-supported standard. You should consider instead
using `poetry version patch` and looking up the `__version__` from the package metadata and not storing the version
anywhere in source code.

Special attention to making sure you don't have to write regex or do complex configuration.

```bash
# This is just a command line tool, keep your venv clean using pipx
pipx install jiggle-version
 
# bump version
jiggle-version here

# bump version of specific module
jiggle_version here --module=my_module

# just find version
git --tag $(jiggle-version find)
```

Badges
------

![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/jiggle-version) [![Downloads](https://pepy.tech/badge/jiggle-version/month)](https://pepy.tech/project/jiggle-version/month)

[![Coverage Status](https://coveralls.io/repos/github/matthewdeanmartin/jiggle_version/badge.svg?branch=master)](https://coveralls.io/github/matthewdeanmartin/jiggle_version?branch=master)
[![CodeFactor](https://www.codefactor.io/repository/github/matthewdeanmartin/jiggle_version/badge)](https://www.codefactor.io/repository/github/matthewdeanmartin/jiggle_version)

Python Versions Supported
-------------------------
3.6, 3.7, 3.8, and forward. Pypi still hosts the old version that supported python 2 and earlier.


Opinionated
-----------
A library should have one working, no-options, no questions asked scenario, e.g.

```bash
jiggle-version here
# find, bump & update version strings in source code
```

An opinionated library has an opinion about the right way to do it. That said, if the library can discover existing
conventions, it should discover them and use them. If you don't like it, see the end for competing opinionated libraries
and their philosophy, such as vcs-tag-only, regex-more-regex-all-day-regex.

The following constraints enable "drop in and go"

No Config, No Regex
-------------------
If the config is more complex than re-writing the code from scratch, there is something wrong with a library. Forcing
the developer to write regex to use a utility is a colossal cop-out.

Security
--------
Jiggle version will not execute python code other than `ast.literal_eval`. Some package versions stored in source code
can only be handled by executing `setup.py` or executing the file with dunder version. Those scenarios are not handled.

Documentation
-------------

- [Design Philosophy](docs/design_philosophy.md)
- [Prior Art](docs/prior_art.md)
- [TODO](docs/todo.md)
- [Authors](docs/AUTHORS)
- [ChangeLog](docs/ChangeLog)
- [Code of Conduct](docs/CODE_OF_CONDUCT.md)