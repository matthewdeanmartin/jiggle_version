# coding=utf-8
"""
Middle of pipeline. Preferably, no docopt concepts here.

command line -> command -> classes

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from jiggle_version.find_version_class import FindVersion
from jiggle_version.jiggle_class import JiggleVersion

import logging
import sys

from jiggle_version.utils import die

if sys.version_info.major == 3:
    unicode = str
logger = logging.getLogger(__name__)


def bump_version(project, source, debug):  # type: (str, str, bool) ->None
    """
    Entry point
    :return:
    """
    # logger.debug("Starting version jiggler...")
    jiggler = JiggleVersion(project, source, debug)
    logger.debug(
        "Current, next : {0} -> {1} : {2}".format(
            jiggler.current_version, jiggler.version, jiggler.schema
        )
    )
    if not jiggler.version_finder.validate_current_versions():

        logger.debug(str(jiggler.version_finder.all_current_versions()))
        logger.error("Versions not in sync, won't continue")
        die(-1,"Versions not in sync, won't continue")
    changed = jiggler.jiggle_all()
    logger.debug("Changed {0} files".format(changed))


def find_version(project, source, debug):  # type: (str, str, bool) ->None
    """
    Entry point to just find a version and print next
    :return:
    """
    # quiet! no noise
    finder = FindVersion(project, source, debug)
    if not finder.validate_current_versions():
        # This is a failure.
        logger.debug(str(finder.all_current_versions()))
        logger.error("Versions not in sync, won't continue")
        die(-1,"Versions not in sync, won't continue")

    version = finder.find_any_valid_version()
    if version:
        print(finder.version_to_write(unicode(version)))
    else:
        logger.error("Failed to find version")
        die(-1, "Failed to find version")
