# coding=utf-8
"""
Make dupe file lists go away.
"""
import os


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
        self.project_root = os.path.join(self.src, self.project)

        self.source_files = [
            "__init__.py",  # required.
            "__version__.py",  # required.
            "_version.py",  # optional
            "version.py",  # uncommon
            "__about__.py",  # uncommon
            "__meta__.py",  # uncommon
        ]
        replacement = []
        for file in self.source_files:
            replacement.append(os.path.join(self.project_root, file))
        self.source_files = replacement

        self.config_files = [os.path.join(self.src, "setup.cfg")]

        self.text_files = [
            os.path.join(self.src, "version.txt"),
            os.path.join(self.src, "VERSION.txt"),
            os.path.join(self.src, "VERSION"),
            os.path.join(self.src, "version"),
            os.path.join(self.src, ".version"),
            os.path.join(self.src, ".VERSION"),
        ]
