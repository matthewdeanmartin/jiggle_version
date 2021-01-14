"""
Middle of pipeline. Preferably, no docopt concepts here.

command line -> command -> classes

"""

import logging

from jiggle_version.file_opener import FileOpener
from jiggle_version.find_version_class import FindVersion
from jiggle_version.jiggle_class import JiggleVersion
from jiggle_version.utils import die

logger = logging.getLogger(__name__)


def bump_version(project: str, source: str, force_init: bool, signature: bool) -> int:
    """
    Entry point
    :return:
    """
    file_opener = FileOpener()
    # logger.debug("Starting version jiggler...")
    jiggler = JiggleVersion(project, source, file_opener, force_init, signature)

    logger.debug(
        f"Current, next : {jiggler.current_version} -> {jiggler.version} "
        f": {jiggler.schema}"
    )
    if not jiggler.version_finder.validate_current_versions():
        logger.debug(str(jiggler.version_finder.all_current_versions()))
        logger.error("Versions not in sync, won't continue")
        die(-1, "Versions not in sync, won't continue")
    changed = jiggler.jiggle_all()
    logger.debug(f"Changed {changed} files")
    return changed


def find_version(project: str, source: str, force_init: bool) -> None:
    """
    Entry point to just find a version and print next
    :return:
    """
    # quiet! no noise
    file_opener = FileOpener()
    finder = FindVersion(project, source, file_opener, force_init=force_init)
    if finder.PROJECT is None:
        raise TypeError("Next step will fail without project name")
    if not finder.validate_current_versions():
        # This is a failure.
        logger.debug(str(finder.all_current_versions()))
        logger.error("Versions not in sync, won't continue")
        die(-1, "Versions not in sync, won't continue")

    version = finder.find_any_valid_version()
    if version:
        print(finder.version_to_write(str(version)))
    else:
        logger.error("Failed to find version")
        die(-1, "Failed to find version")
