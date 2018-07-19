import io
import logging
import sys
from typing import List, Optional, Any

import chardet

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
        if not file.startswith("/"):
            # raise TypeError("this isn't absolute! We're siths, ya' know.")
            pass
        if file in self.found_encoding:

            encoding = self.found_encoding[file]
        else:
            encoding_info = chardet.detect(io.open("setup.py", "rb").read())
            encoding = encoding_info["encoding"]
            logger.debug(unicode(encoding))
            self.found_encoding[file] = encoding

        return io.open(file, how, encoding=encoding)
