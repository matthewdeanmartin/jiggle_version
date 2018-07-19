# coding=utf-8
"""
Make dupe file lists go away.
"""
import io
import logging
import os
import sys
from typing import List, Optional, Any

import chardet

_ = List, Optional, Any
if sys.version_info.major == 3:
    unicode = str
logger = logging.getLogger(__name__)


class FileInventory(object):
    """
    Container for list of files that might have bumpable versions
    """

    def __init__(self, project, src):  # type: (str,str) -> None
        """
        Init object
        :param project:
        :param src:
        """
        self.project = project
        self.src = src

        # the files we will attempt to manage
        # This path expects a package with 1 module in a folder
        # not an edge case like setup.py only or file only module
        # or multiple modules in one package
        # or submodules that you might want to version
        self.project_root = os.path.join(self.src, self.project)

        self.source_files = [
            "__init__.py",  # required.
            # "__version__.py",  # this creates confusing import patterns
            "_version.py",  # optional
            "version.py",  # uncommon
            "__about__.py",  # uncommon
            "__meta__.py",  # uncommon
        ]
        replacement = []
        if os.path.isdir(self.project_root):
            for file in self.source_files:
                replacement.append(os.path.join(self.project_root, file))

        self.source_files = replacement

        self.config_files = [os.path.join(self.src, "setup.cfg")]

        self.default_text_file = [os.path.join(self.src, "VERSION.txt")]
        self.text_files = [
            os.path.join(self.src, "version.txt"),
            os.path.join(self.src, "VERSION.txt"),
            os.path.join(self.src, "VERSION"),
            os.path.join(self.src, "version"),
            os.path.join(self.src, ".version"),
            os.path.join(self.src, ".VERSION"),
        ]
