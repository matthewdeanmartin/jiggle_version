"""
Middle of pipeline. Preferably, no docopt concepts here.

command line -> command -> classes

"""

from __future__ import annotations

import logging
from pathlib import Path

from jiggle_version.file_opener import FileOpener
from jiggle_version.find_version_class import VersionDiscoverer
from jiggle_version.jiggle_class import JiggleVersion
from jiggle_version.parse_version.schema_guesser import version_object_and_next
from jiggle_version.utils import JiggleVersionException

logger = logging.getLogger(__name__)


def bump_version(project: Path, source: Path, force_init: bool, signature: bool) -> int:
    """
    Entry point
    """
    file_opener = FileOpener()
    # logger.debug("Starting version jiggler...")
    jiggler = JiggleVersion(project, source, file_opener, force_init, signature)

    logger.debug(
        f"Current, next : {jiggler.current_version} -> {jiggler.version} "
        f": {jiggler.schema}"
    )
    changed = jiggler.jiggle_all()
    logger.debug(f"Changed {changed} files")
    return changed


def find_version(project: Path, source: Path, force_init: bool) -> None:
    """
    Entry point to find the project's version and determine the next version.

    This function uses the VersionDiscoverer to handle the complexities of
    finding and validating the version from various project files.
    """
    file_opener = FileOpener()
    try:
        # 1. Instantiate the discoverer. It handles all file searching,
        #    parsing, and validation internally.
        discoverer = VersionDiscoverer(
            project, source, file_opener, force_init=force_init
        )

        # 2. discover_version() returns the single, canonical version string
        #    or raises an exception if versions are inconsistent or not found.
        current_version_str = discoverer.discover_version()

        # 3. If a version is found, calculate the next version.
        #    The original version_object_and_next utility can still be used here.
        _, next_version, schema = version_object_and_next(current_version_str)

        # 4. Log the results for the user.
        logger.info(f"Successfully found version: {current_version_str}")
        logger.info(f"Detected schema: {schema}")
        logger.info(f"Next logical version would be: {next_version}")

    except JiggleVersionException as e:
        # Catch exceptions for known failure cases (e.g., no version found,
        # or inconsistent versions) and report them clearly.
        logger.error(f"Failed to determine a consistent version: {e}")
        raise  # Re-raise to signal failure to the calling process
