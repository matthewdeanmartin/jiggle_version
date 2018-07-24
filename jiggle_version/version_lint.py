# coding=utf-8
"""
Give advice on versions as found, e.g.

jiggle_version lint

- no versions found & not vcs
- package name != central module name
- package and central module out of sync
- version are expressions not constants
- __version_info__ is a constant. (should be derived)
- __version_info__ not found, isn't derived from __version__
- __version__.py maybe a bad idea
- uncommon convenion (__VERSION__ or version as constant name)
- single file module should have __version__

"""

# List files to version

# List files to create (setup.py, init)
