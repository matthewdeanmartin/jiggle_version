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
from typing import List, Optional, Dict, Any

from docopt import docopt

from jiggle_version.commands import bump_version, find_version
from jiggle_version.project_finder import find_project

logger = logging.getLogger(__name__)

# contrive usage so formatter doesn't remove the import
_ = List, Optional, Dict, Any


def validate_found_project(candidates):  # type: (List[str]) -> None
    """

    :param candidates:
    :return:
    """
    if len(candidates) > 1:
        logger.error("Found multiple possible projects : " + str(candidates))
        exit(-1)
        return
    if not candidates:
        logger.error(
            "Found no project. Expected a folder in current directory to contain a __init__.py "
            "file. Use --source, --project for other scenarios"
        )
        exit(-1)
        return


def console_trace(level):  # type: (int)->None
    # set up logging to file - see previous section for more details
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        datefmt="%m-%d %H:%M",
        # filename='/temp/myapp.log',
        # filemode='w'
    )
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
    arguments = docopt(__doc__, version="Jiggle Version 1.0")
    logger.debug(arguments)
    candidates = find_project()
    if candidates:
        project_name = candidates[0]
    else:
        project_name = None

    if arguments["here"]:
        if arguments["--debug"]:
            console_trace(logging.DEBUG)
        validate_found_project(candidates)
        bump_version(project=project_name, source="", debug=arguments["--debug"])
    elif arguments["find"]:
        # Only show errors. Rest of extraneous console output messes up this:
        # jiggle_version find>version.txt

        if arguments["--debug"] == "True":
            console_trace(logging.DEBUG)
        else:
            console_trace(logging.ERROR)
        if not arguments["--project"]:
            validate_found_project(candidates)
        find_version(project=project_name, source="", debug=arguments["--debug"])

    else:
        if arguments["--debug"] == "True":
            console_trace(logging.DEBUG)
        if not arguments["--project"]:
            validate_found_project(candidates)
        bump_version(
            project=arguments["--project"],
            source=arguments["--source"],
            debug=arguments["--debug"],
        )


if __name__ == "__main__":
    process_docopts()
