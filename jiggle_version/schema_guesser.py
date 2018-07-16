# coding=utf-8
"""
Take a string, guess the schema.

IDEA: Each library gets to try to parse string in this order:

sem_ver - because I *think* any bumped sem ver is a valid pep440
pep440 - just because we are assuming python world.

If the above can't do it, try:

par ver

cmp ver

disutils.version

"""

from distutils.version import Version, LooseVersion, StrictVersion

from jiggle_version.vendorized.versio.version import Version, VersionScheme, Pep440VersionScheme
from jiggle_version.vendorized.versio.version_scheme import Simple3VersionScheme, Simple4VersionScheme, \
    Simple5VersionScheme, Pep440VersionScheme, PerlVersionScheme, VersionSplitScheme


def guess(version_string, scheme): # type: (str) -> str
    v = Version(version_str=version_string, scheme=scheme)
    return str(v)

# par ver

# sem ver

# cmp-version

if __name__  == "__main__":
    for scheme in [Pep440VersionScheme, Simple5VersionScheme, Simple4VersionScheme, Simple3VersionScheme, PerlVersionScheme]:
        for s in ["1.1","1.1.1", "1.1.1b", "1.1.1beta", "1.1.1.1", "pre-1.1.1"]:
            try:
                print(guess(s, scheme=scheme))
            except AttributeError as ae:
                print(scheme.name, str(ae))
            except TypeError as te:
                print(scheme.name, s)


