"""
Make dupe file lists go away.
"""
import logging
import os

logger = logging.getLogger(__name__)


class FileInventory:
    """
    Container for list of files that might have bumpable versions
    """

    def __init__(self, project: str, src: str) -> None:
        """
        Init object
        """
        self.project = project
        self.src = src

        # the files we will attempt to manage
        # This path expects a package with 1 module in a folder
        # not an edge case like setup.py only or file only module
        # or multiple modules in one package
        # or submodules that you might want to version
        self.project_root = os.path.join(self.src, self.project)

        # TODO: sometimes the __version__ is in ANY FILE.
        self.source_files = [
            "__init__.py",  # required.
            "__version__.py",  # this creates confusing import patterns
            "_version.py",  # optional
            "version.py",  # uncommon
            "__about__.py",  # uncommon
            "__meta__.py",  # uncommon
            "__pkg__.py",  # rare
        ]
        replacement = []
        if os.path.isdir(self.project_root):
            for file in self.source_files:
                replacement.append(os.path.join(self.project_root, file))

        self.source_files = replacement

        self.config_files = [os.path.join(self.src, "setup.cfg")]

        self.default_text_file = [os.path.join(self.src, "VERSION.txt")]
        # [_,,.][version|VERSION|Version][,.txt]

        self.text_files = [
            os.path.join(self.src, "version.txt"),
            os.path.join(self.src, "VERSION.txt"),
            os.path.join(self.src, "_version.txt"),
            os.path.join(self.src, "_VERSION.txt"),
            os.path.join(self.src, "VERSION"),
            os.path.join(self.src, "version"),
            os.path.join(self.src, "_VERSION"),
            os.path.join(self.src, "_version"),
            os.path.join(self.src, ".version"),
            os.path.join(self.src, ".VERSION"),
        ]
