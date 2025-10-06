"""
Support code for setup.py and package driven version management.

Package holds last version & we want to bump setup.py's view of version.

Yes, you could have setup.py read from __version__.py and should.

"""

from __future__ import annotations

from importlib import import_module
from typing import Any

_ = Any


# from pipdeptree.py
def guess_version_by_running_live_package(pkg_key: str, default: str = "?") -> Any:
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
