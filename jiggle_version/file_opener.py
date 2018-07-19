# coding=utf-8
"""
Detect encoding, read file, remember encoding
"""
import io
import logging
import sys
from typing import List, Optional, Any

import chardet

try:
    import configparser
except ImportError:
    # Python 2.x fallback
    import ConfigParser as configparser

_ = List, Optional, Any
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
        self.found_encoding = {}

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
            return config["metadata"]["version"]
        except KeyError:
            return ""
