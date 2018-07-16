# coding=utf-8
"""
Middle of pipeline. Preferably, no docopt concepts here.

command line -> command -> classes

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import sys

from jiggle_version.find_version_class import FindVersion
from jiggle_version.jiggle_class import JiggleVersion

if sys.version_info.major == 3:
    unicode = str
logger = logging.getLogger(__name__)


def bump_version(project, source, debug):  # type: (str, str, bool) ->None
    """
    Entry point
    :return:
    """
    print()
    print("Starting version jiggler...")
    jiggler = JiggleVersion(project, source, debug)

    if not jiggler.version_finder.validate_current_versions():
        logger.error("Versions not in sync, won't continue")
        exit(-1)
    jiggler.jiggle_source_code()
    jiggler.jiggle_config_file()


def find_version(project, source, debug):  # type: (str, str, bool) ->None
    """
    Entry point to just find a version and print next
    :return:
    """
    # quiet! no noise
    jiggler = FindVersion(project, source, debug)
    if not jiggler.validate_current_versions():
        # This is a failure.
        logger.error("Versions not in sync, won't continue")
        exit(-1)
    version = jiggler.find_any_valid_verision()
    if version:
        print(jiggler.version_to_write(unicode(version)))
    else:
        logger.error("Failed to find version")
        exit(-1)
