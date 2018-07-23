# coding=utf-8
"""
Support code for setup.py and package driven version management.

Package holds last version & we want to bump setup.py's view of version.

Yes, you could have setup.py read from __version__.py and should.

"""

# py2 prob here!
from importlib import import_module
from typing import Any

import pkg_resources

from jiggle_version.utils import execute_get_text

_ = Any

# These are not expected unless you unzip a package and do development on *that* code base.
# TODO- Parent folder, e.g. mypackage-1.2.3
# TODO- PKG-INFO


def pkg_resources_version(package):  # type: (str) -> str
    """
    Look up version from current package. This will read from egg folder if not pip installed.
    :param package:
    :return:
    """
    # ref https://stackoverflow.com/questions/7079735/how-do-i-get-the-version-of-an-installed-module-in-python-programatically
    try:
        return pkg_resources.get_distribution(package).version
    except Exception:
        return "unknown"


# command lines


def version_by_pip(package):
    """
    Don't use this for bumping code, unless it is dot installed,
    this is going to look at pip installed packages?
    :param package:
    :return:
    """
    command = "pip show {0}".format(package)
    result = execute_get_text(command)
    for line in result.split("\n"):
        if line.startswith("Version"):
            return line.split(":")[0]
    return None


# from pipdeptree.py
def guess_version_by_running_live_package(
    pkg_key, default="?"
):  # type: (str,str) -> Any
    """Guess the version of a pkg when pip doesn't provide it.

    :param str pkg_key: key of the package
    :param str default: default version to return if unable to find
    :returns: version
    :rtype: string

    """
    try:
        m = import_module(pkg_key)
    except ImportError:
        return default
    else:
        return getattr(m, "__version__", default)


if __name__ == "__main__":
    print(pkg_resources_version("setuptools"))
    print(pkg_resources_version("jiggle_version"))
