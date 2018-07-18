# coding=utf-8
"""
Creates missing files, no logic about deciding if they should exist.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

# contrive usage so black doesn't remove the import
_ = List, Optional


class FileMaker(object):
    """
    Just wrties files.
    """

    def __init__(self, project):  # type:  (str) -> None
        """
        Initialize
        :param project:
        """
        self.project = project

    def create_init(self, path):  # type: (str) -> None
        """
        Create a minimal __init__ file with enough boiler plate to not add to lint messages
        :param path:
        :return:
        """
        source = """# coding=utf-8
\"\"\"
Version
\"\"\"
__version__ = \"0.0.0\"
"""
        with io.open(path, "w", encoding="utf-8") as outfile:
            outfile.write(source)

    def create_version(self, path):  # type: (str) -> None
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
        with io.open(path, "w", encoding="utf-8") as outfile:
            outfile.write(source)

    def create_setup_cfg(self, path):  # type: (str) -> None
        """
        Just setup.cfg
        :param path:
        :return:
        """
        source = """[metadata]
name = {0}
version=0.0.1 
""".format(
            self.project
        )
        with io.open(path, "w", encoding="utf-8") as outfile:
            outfile.write(source)
