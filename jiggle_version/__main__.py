"""
Jiggle Version.

A tool for bumping package versions based on semantic versioning or other schemas.
"""

from __future__ import annotations

import argparse
import logging
import logging.config
import os
import sys
from pathlib import Path
from typing import Sequence

from jiggle_version.__about__ import __version__
from jiggle_version.central_module_finder import CentralModuleFinder
from jiggle_version.commands import bump_version, find_version
from jiggle_version.file_opener import FileOpener
from jiggle_version.module_finder import ModuleFinder
from jiggle_version.utils import JiggleVersionException

# It's good practice to configure logging to see the output.
# If the user of this class doesn't configure it, these messages will be silent.
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)


def console_trace(level: int) -> None:
    """
    Sets up console logging.
    """
    _ = level

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": True,
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


def main(argv: Sequence[str] | None = None) -> int:
    """
    Main entry point for the command-line interface.
    """
    # For now, we will enable logging by default for clarity.
    console_trace(logging.DEBUG)

    parser = argparse.ArgumentParser(
        description="Jiggle Version: A tool for bumping package versions."
    )
    parser.add_argument(
        "--version", action="version", version=f"jiggle_version {__version__}"
    )

    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Available commands"
    )

    # --- 'bump' command ---
    parser_bump = subparsers.add_parser(
        "bump", help="Increment the version for a package or module."
    )
    bump_subparsers = parser_bump.add_subparsers(
        dest="target", required=True, help="Target to bump"
    )

    # --- 'bump package' command ---
    parser_bump_package = bump_subparsers.add_parser(
        "package", help="Increment version for the main package."
    )
    parser_bump_package.add_argument(
        "src_folder", type=str, help="Path to the source folder."
    )
    parser_bump_package.add_argument(
        "--increment",
        type=str,
        default="patch",
        choices=["major", "minor", "patch"],
        help="The part of the version to increment.",
    )
    parser_bump_package.add_argument(
        "--schema",
        type=str,
        default=None,
        help="The versioning schema to use (e.g., semantic, pep). (Not yet implemented)",
    )
    parser_bump_package.add_argument(
        "--signature",
        action="store_true",
        help="Add a signature comment to modified lines.",
    )
    parser_bump_package.add_argument(
        "--init",
        action="store_true",
        help="Initialize version to 0.1.0 if not found.",
    )

    # --- 'bump module' command ---
    parser_bump_module = bump_subparsers.add_parser(
        "module", help="Increment version for a submodule."
    )
    parser_bump_module.add_argument(
        "src_folder", type=str, help="Path to the source folder containing the module."
    )
    parser_bump_module.add_argument(
        "--all", action="store_true", help="Increment versions in all submodules."
    )
    parser_bump_module.add_argument(
        "--signature",
        action="store_true",
        help="Add a signature comment to modified lines.",
    )
    parser_bump_module.add_argument(
        "--init",
        action="store_true",
        help="Initialize version to 0.1.0 if not found.",
    )

    # --- 'current' command ---
    parser_current = subparsers.add_parser(
        "current", help="Return the current version(s) of the package."
    )
    parser_current.add_argument(
        "src_folder", type=str, help="Path to the source folder."
    )
    parser_current.add_argument(
        "--init",
        action="store_true",
        help="Initialize version to 0.1.0 if not found.",
    )

    args = parser.parse_args(argv)

    # The finders operate on the current working directory, so we need to change to it.
    if not os.path.isdir(args.src_folder):
        raise JiggleVersionException(f"Source folder not found at '{args.src_folder}'")
    os.chdir(args.src_folder)

    file_opener = FileOpener()

    if args.command == "current":
        # For 'current', we still need to find the main project module.
        central_module_finder = CentralModuleFinder(file_opener)
        central_module = central_module_finder.find_central_module()
        if not central_module:
            raise JiggleVersionException(
                "Could not automatically determine the central module."
            )

        find_version(
            project=Path(central_module or "."), source=Path("."), force_init=args.init
        )

    elif args.command == "bump":
        if args.target == "package":
            central_module_finder = CentralModuleFinder(file_opener)
            central_module = central_module_finder.find_central_module()
            if not central_module:
                raise JiggleVersionException(
                    "Could not automatically determine the central package module."
                )

            logger.info(
                f"Bumping '{central_module}' package with increment '{args.increment}'."
            )
            # NOTE: To make this fully functional, `bump_version` and its underlying
            # classes need to be updated to accept and use the `increment` parameter.
            # The current implementation only performs a patch bump.
            bump_version(
                project=Path(central_module or "."),
                source=Path("."),  # Already in the correct directory
                force_init=args.init,
                signature=args.signature,
            )

        elif args.target == "module":
            # NOTE: Bumping specific or all modules requires new logic.
            # The existing `bump_version` works on one "project" at a time.
            module_finder = ModuleFinder(file_opener)
            all_modules = module_finder.find_by_any_method()

            if not all_modules:
                raise JiggleVersionException("No modules found to bump.")

            if args.all:
                logger.info(f"Bumping all found modules: {all_modules}")
                for module in all_modules:
                    logger.info(f"--- Bumping {module} ---")
                    bump_version(
                        project=Path(module),
                        source=Path("."),
                        force_init=args.init,
                        signature=args.signature,
                    )
            else:
                # The syntax 'bump module <src>' is ambiguous if --all is not specified.
                # Defaulting to bumping the main central module.
                central_module_finder = CentralModuleFinder(file_opener)
                central_module = central_module_finder.find_central_module()
                if not central_module:
                    raise JiggleVersionException(
                        "Could not automatically determine the central module to bump.",
                    )
                logger.info(f"Bumping the central module: {central_module}")
                bump_version(
                    project=Path(central_module or "."),
                    source=Path("."),
                    force_init=args.init,
                    signature=args.signature,
                )
    return 0


if __name__ == "__main__":
    sys.exit(main())
