# coding=utf-8
"""
Jiggle Version.

Usage:
  jiggle_version here
  jiggle_version --project=<project> --source=<source> [--debug=<debug>]
  jiggle_version -h | --help
  jiggle_version --version

Options:
  --project=<project>  Project name, e.g. my_lib in src/my_lib
  --source=<source>  Source folder. e.g. src/
  -h --help     Show this screen.
  --version     Show version.
  --debug=<debug>  Show diagnostic info [default: False].
"""

import logging
import os

from docopt import docopt

from jiggle_version.jiggle_class import JiggleVersion

logger = logging.getLogger(__name__)


def go(project, source, debug):  # type: (str, str, bool) ->None
    """
    Entry point
    :return:
    """
    jiggler = JiggleVersion(project, source, debug)
    jiggler.jiggle_source_code()
    jiggler.jiggle_config_file()


def process_docopts():  # type: ()->None
    arguments = docopt(__doc__, version="Jiggle Version 1.0")
    logger.debug(arguments)
    if arguments["here"]:
        folders = files = [f for f in os.listdir(".") if os.path.isdir(f)]
        found = 0
        candidates = []
        for folder in folders:
            if os.path.isfile(folder + "/__init__.py"):
                project = folder
                candidates.append(folder)
        if len(candidates) > 1:
            print("Found multiple possible projects : " + str(candidates))
            exit(-1)
            return
        if not candidates:
            print(
                "Found no project. Expected a folder in current directory to contain a __init__.py "
                "file. Use --source, --project for other scenarios"
            )
            exit(-1)
            return

        go(project=candidates[0], source="", debug=arguments["--debug"])
    else:
        go(
            project=arguments["--project"],
            source=arguments["--source"],
            debug=arguments["--debug"],
        )


if __name__ == "__main__":
    process_docopts()
