# coding=utf-8
"""
Support code for setup.py and package driven version management.

Package holds last version & we want to bump setup.py's view of version.

Yes, you could have setup.py read from __version__.py and should.

"""

import pkg_resources

def pkg_resources_version(package): # type: (str) -> str
    """
    Look up version from current package. This will read from egg folder if not pip installed.
    :param package:
    :return:
    """
    try:
        return pkg_resources.get_distribution(package).version
    except Exception:
        return 'unknown'


if __name__  == "__main__":
    print(pkg_resources_version("setuptools"))
    print(pkg_resources_version("jiggle_version"))