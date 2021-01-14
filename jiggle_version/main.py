"""
Jiggle Version.

Usage:
  jiggle_version here [--module=<module>] [--init] [--signature]
  jiggle_version find [--module=<module>] [--init]
  jiggle_version --project=<project> --source=<source> [--init]
  jiggle_version -h | --help
  jiggle_version --version

Options:
  here                 No config version bumping, edits source code and stops.
  find                 Just tell me next version, like this jiggle_version find>version.txt
  --init               Force initialization. Use 0.1.0 as first version if version not found
  --signature          Write "# Jiggle Version was here" on lines with modified source
  --module=<module>    Explicitly specify which module to target
  --execute_code       infer version by parsing only, or parsing and executing?
  --strict             Don't tolerate weird states
  --project=<project>  'Central' module name, e.g. my_lib in src/my_lib
  --source=<source>    Source folder. e.g. src/
  --version            Show version of jiggle_version, not your apps.
  -h --help            Show this screen.

"""

import logging
import logging.config
from typing import Any, Dict, List, Optional

from docopt import docopt

from jiggle_version._version import __version__
from jiggle_version.central_module_finder import CentralModuleFinder
from jiggle_version.commands import bump_version, find_version
from jiggle_version.file_opener import FileOpener
from jiggle_version.module_finder import ModuleFinder

logger = logging.getLogger(__name__)

# contrive usage so formatter doesn't remove the import
_ = List, Optional, Dict, Any


def console_trace(level: int) -> None:
    """
    Stop using print(), messes up `jiggle_version find` command
    :return:
    """

    # TODO: fix logging. This is a mess.
    _ = level

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": True,  # try to silence chardet
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


def process_docopts(test: Optional[Dict[str, Any]] = None) -> None:
    """
    Just process the command line options and commands
    :return:
    """
    if test:
        arguments = test
    else:
        arguments = docopt(__doc__, version=f"Jiggle Version {__version__}")

    logger.debug(arguments)

    file_opener = FileOpener()
    central_module_finder = CentralModuleFinder(file_opener)

    if arguments["--module"]:
        central_module = arguments["--module"]
    elif arguments["--project"]:
        # soon to be deprecated in favor of module/package
        central_module = arguments["--project"]
    else:
        # infer it the best we can.
        central_module = central_module_finder.find_central_module()

    arg_name = "--init"
    force_init = extract_bool(arg_name, arguments)
    arg_name = "--signature"
    signature = extract_bool(arg_name, arguments)

    if arguments["here"]:
        # TODO: find better way to turn debugging on & off
        # console_trace(logging.DEBUG)
        module_finder = ModuleFinder(file_opener)
        guess_src_dir = module_finder.extract_package_dir()
        if not guess_src_dir:
            guess_src_dir = ""

        if not central_module:
            # check if exists first?
            central_module = "setup.py"

        bump_version(
            project=central_module,
            source=guess_src_dir,
            force_init=force_init,
            signature=signature,
        )
    elif arguments["find"]:
        # Only show errors. Rest of extraneous console output messes up this:
        # jiggle_version find>version.txt

        if arguments["--project"]:
            central_module = arguments["--project"]

        find_version(project=central_module, source="", force_init=force_init)

    else:
        bump_version(
            project=arguments["--project"],
            source=arguments["--source"],
            force_init=force_init,
            signature=signature,
        )


def extract_bool(arg_name: str, arguments: Dict[str, str]) -> bool:
    """
    Pull a bool from a arg dict
    """
    if arg_name in arguments and arguments[arg_name]:
        value = arguments[arg_name]
        if value == "False":
            return False
        if value == "True":
            return True
    else:
        return False
    return False


if __name__ == "__main__":
    process_docopts()
