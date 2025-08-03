"""
Creates missing files, no logic about deciding if they should exist.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class FileMaker:
    """
    Just writes files.
    """

    def __init__(self, project: str) -> None:
        """
        Initialize
        """
        self.project = project

    def create_init(self, path: str) -> None:
        """
        Create a minimal __init__ file with enough boiler plate to not add to lint messages
        """
        source = """# coding=utf-8
\"\"\"
Version
\"\"\"
__version__ = \"0.0.0\"
"""
        with open(path, "w", encoding="utf-8") as outfile:
            outfile.write(source)

    def create_version(self, path: str) -> None:
        """
        Create a minimal __version__ file with enough boiler plate to not add to lint messages
        :param path:
        :return:
        """
        source = """# coding=utf-8
\"\"\"
Init
\"\"\"
__version__ = \"0.0.0\"
"""
        with open(path, "w", encoding="utf-8") as outfile:
            outfile.write(source)

    def create_setup_cfg(self, path: str) -> None:
        """
        Just setup.cfg
        """
        source = f"""[metadata]
name = {self.project}
version=0.0.1
"""
        with open(path, "w", encoding="utf-8") as outfile:
            outfile.write(source)
