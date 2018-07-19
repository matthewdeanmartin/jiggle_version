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
import logging
import sys
from typing import Any, Tuple, Optional, Union

import parver
import semantic_version
from versio import version as versio_version
from versio.version_scheme import Pep440VersionScheme, Simple4VersionScheme

from jiggle_version.utils import JiggleVersionException

if sys.version_info.major == 3:
    unicode = str
logger = logging.getLogger(__name__)

_ = Any, Tuple, Optional, Union
versio_version.Version.supported_version_schemes = [
    Pep440VersionScheme,
    Simple4VersionScheme,
]


def version_object_and_next(
    string
):  # type: (str) -> Tuple[Union[semantic_version.Version,parver.Version, versio_version.Version],Union[semantic_version.Version, parver.Version, versio_version.Version],str]
    """
    Try three parsing strategies, favoring semver, then pep440, then whatev.
    :param string:
    :return:
    """
    if string == "" or string is None:
        raise JiggleVersionException("No version string, can only use default logic.")

    if string[0] == "v":
        string = string[1:]
    if len(string.split(".")) == 1:
        # convert 2 part to 3 part.
        string = string + ".0.0"
    elif len(string.split(".")) == 2:
        # convert 2 part to 3 part, e.g. 1.1 -> 1.1.0
        string = string + ".0"

    try:
        version = semantic_version.Version(string)
        next_version = version.next_patch()
        _ = semantic_version.Version(str(string))
        return version, next_version, "semantic_version"
    except:
        logger.debug("Not sem_ver:" + unicode(string))
        try:
            version = parver.Version.parse(string)
            next_version = version.bump_dev()
            _ = parver.Version.parse(str(next_version))
            return version, next_version, "pep440 (parver)"
        except:
            try:
                logger.debug("Not par_ver:" + unicode(string))
                # Version.supported_version_schemes = [Pep440VersionScheme, Simple4VersionScheme]
                version = versio_version.Version(string, scheme=Simple4VersionScheme)
                version.bump()
                return (
                    versio_version.Version(string, scheme=Simple4VersionScheme),
                    version,
                    "simple-4 part (versio)",
                )
            except:
                logger.debug("Not versio:" + unicode(string))
                # versio only does pep440 by default
                # print(versio.version.Version.supported_version_schemes)
                raise
