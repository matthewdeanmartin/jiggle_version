# coding=utf-8
"""
Detect encoding, read file, remember encoding
"""
import io
import logging
import sys
from typing import List, Optional, Any, Dict

import chardet

try:
    import configparser
except ImportError:
    # Python 2.x fallback
    import ConfigParser as configparser

_ = List, Optional, Any, Dict

if sys.version_info.major == 3:
    unicode = str
logger = logging.getLogger(__name__)


class FileOpener(object):
    """
    Container for list of files that might have bumpable versions
    """

    def __init__(self):  # type: () -> None
        """
        Init object
        :param project:
        :param src:
        """
        self.found_encoding = {}  # type: Dict[str,str]

    def is_python_inside(self, file_path):  # type: (str) -> bool
        """
        If .py, yes. If extensionless, open file and check shebang


        TODO: support variations on this: #!/usr/bin/env python

        :param file_path:
        :return:
        """
        if file_path.endswith(".py"):
            return True  # duh.

        # not supporting surprising extensions, ege. .py2, .python, .corn_chowder

        # extensionless
        if not "." in file_path:
            try:
                firstline = self.open_this(file_path, "r").readline()
                if firstline.startswith("#") and "python" in firstline:
                    return True
            except:
                pass
        return False

    def read_this(self, file):  # type: (str) -> Any
        """
        Return file text.
        :param file:
        :return:
        """
        with self.open_this(file, "r") as file_handler:
            return file_handler.read()

    def open_this(self, file, how):  # type: (str,str) -> Any
        """
        Open file while detecting encoding. Use cached when possible.
        :param file:
        :param how:
        :return:
        """
        # BUG: risky code here, allowing relative
        if not file.startswith("/"):
            # raise TypeError("this isn't absolute! We're siths, ya' know.")
            pass
        if file in self.found_encoding:

            encoding = self.found_encoding[file]
        else:
            file_bytes = io.open(file, "rb").read()
            if not file_bytes:
                encoding = "utf-8"
            else:
                encoding_info = chardet.detect(file_bytes)
                encoding = encoding_info["encoding"]
            logger.debug(unicode(encoding))
            try:
                io.open(file, how, encoding=encoding).read()
            except UnicodeDecodeError:
                print(file)
                print(file_bytes)

            self.found_encoding[file] = encoding

        return io.open(file, how, encoding=encoding)

    def read_metadata(self, file_path):  # type: (str) ->str
        """
        Get version out of a .ini file (or .cfg)
        :return:
        """
        config = configparser.ConfigParser()
        config.read(file_path)
        try:
            return unicode(config["metadata"]["version"])
        except KeyError:
            return ""
