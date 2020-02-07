"""
Detect encoding, read file, remember encoding
"""
import configparser
import logging
from typing import Dict, IO, Any, cast

import chardet

logger = logging.getLogger(__name__)


class FileOpener:
    """
    Container for list of files that might have bumpable versions
    """

    def __init__(self) -> None:
        """
        Init object
        """
        self.found_encoding: Dict[str, str] = {}

    def is_python_inside(self, file_path: str) -> bool:
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
        if "." not in file_path:
            # noinspection PyBroadException
            try:
                firstline = self.open_this(file_path, "r").readline()
                if firstline.startswith("#") and "python" in firstline:
                    return True
            except:
                pass
        return False

    def read_this(self, file: str) -> str:
        """
        Return file text.
        :param file:
        :return:
        """
        with self.open_this(file, "r") as file_handler:
            return cast(str, file_handler.read())

    def open_this(self, file: str, how: str) -> IO[Any]:
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
            file_bytes = open(file, "rb").read()
            if not file_bytes:
                encoding = "utf-8"
            else:
                encoding_info = chardet.detect(file_bytes)
                encoding = encoding_info["encoding"]
            logger.debug(str(encoding))
            try:
                open(file, how, encoding=encoding).read()
            except UnicodeDecodeError:
                print(file)
                print(file_bytes)

            self.found_encoding[file] = encoding

        return open(file, how, encoding=encoding)

    def read_metadata(self, file_path: str) -> str:
        """
        Get version out of a .ini file (or .cfg)
        :return:
        """
        config = configparser.ConfigParser()
        config.read(file_path)
        try:
            return str(config["metadata"]["version"])
        except KeyError:
            return ""
