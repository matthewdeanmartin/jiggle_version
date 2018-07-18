# coding=utf-8
"""
Jiggle Version.

Usage:
  jiggle_version here
  jiggle_version find
  jiggle_version --project=<project> --source=<source> [--debug=<debug>]
  jiggle_version -h | --help
  jiggle_version --version

Options:
  here                 No config version bumping, edits source code and stops.
  find_version         Just tell me next version, like this jiggle_version find>version.txt
  --schema             pep440, semversion, guess
  --project=<project>  Project name, e.g. my_lib in src/my_lib
  --source=<source>    Source folder. e.g. src/
  --version            Show version of jiggle_version, not your apps.
  --debug=<debug>      Show diagnostic info [default: False].
  -h --help            Show this screen.

"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import logging.config
from typing import List, Optional, Dict, Any

from docopt import docopt

from jiggle_version.commands import bump_version, find_version
from jiggle_version.project_finder import ModuleFinder

logger = logging.getLogger(__name__)

# contrive usage so formatter doesn't remove the import
_ = List, Optional, Dict, Any


def console_trace(level):  # type: (int)->None
    """
    Stop using print(), messes up `jiggle_version find` command
    :param level:
    :return:
    """
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                }
            },
            "handlers": {
                "default": {"level": "DEBUG", "class": "logging.StreamHandler"}
            },
            "loggers": {
                "": {"handlers": ["default"], "level": "DEBUG", "propagate": True}
            },
        }
    )
    # logger.debug("Does this work?")

    # # define a Handler which writes INFO messages or higher to the sys.stderr
    # console = logging.StreamHandler()
    # console.setLevel(level)
    # # set a format which is simpler for console use
    # formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # # tell the handler to use this format
    # console.setFormatter(formatter)
    # # add the handler to the root logger
    # logging.getLogger('').addHandler(console)


def process_docopts():  # type: ()->None
    """
    Just process the command line options and commands
    :return:
    """
    arguments = docopt(__doc__, version="Jiggle Version 1.0")
    logger.debug(arguments)
    module_finder = ModuleFinder()

    candidates = module_finder.find_project()
    if candidates:
        project_name = candidates[0]
    else:
        project_name = ""

    if arguments["here"]:
        if arguments["--debug"] == "True":
            console_trace(logging.DEBUG)
        module_finder.validate_found_project(candidates)
        guess_src_dir = module_finder.extract_package_dir()
        if not guess_src_dir:
            guess_src_dir = ""
        bump_version(
            project=project_name, source=guess_src_dir, debug=arguments["--debug"]
        )
    elif arguments["find"]:
        # Only show errors. Rest of extraneous console output messes up this:
        # jiggle_version find>version.txt

        if arguments["--debug"] == "True":
            console_trace(logging.DEBUG)
        # else:
        #     console_trace(logging.ERROR)

        if not arguments["--project"]:
            module_finder.validate_found_project(candidates)
        find_version(project=project_name, source="", debug=arguments["--debug"])

    else:
        if arguments["--debug"] == "True":
            console_trace(logging.DEBUG)
        if not arguments["--project"]:
            module_finder.validate_found_project(candidates)
        bump_version(
            project=arguments["--project"],
            source=arguments["--source"],
            debug=arguments["--debug"],
        )


if __name__ == "__main__":
    process_docopts()
