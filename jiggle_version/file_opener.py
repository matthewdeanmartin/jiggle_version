"""
Detect encoding, read file, remember encoding
"""

from __future__ import annotations

import configparser
import logging
from typing import IO, Any, Dict, cast

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

            try:
                with self.open_this(file_path, "r") as file_handle:
                    firstline = file_handle.readline()
                if firstline.startswith("#") and "python" in firstline:
                    return True
            except Exception:
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
            with open(file, "rb") as file_handle_rb:
                file_bytes = file_handle_rb.read()
            if not file_bytes:
                encoding = "utf-8"
            else:
                encoding_info = chardet.detect(file_bytes)
                encoding = encoding_info["encoding"] or ""
            logger.debug(str(encoding))
            try:
                with open(file, how, encoding=encoding) as file_handle:
                    file_handle.read()
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
