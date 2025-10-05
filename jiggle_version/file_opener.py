"""
A refactored script using pathlib to detect encoding, read files,
and remember the encoding for subsequent operations.
"""

from __future__ import annotations

import configparser
import logging
from pathlib import Path
from typing import IO, Any, Dict

import chardet

logger = logging.getLogger(__name__)


class FileOpener:
    """
    A container for file operations that automatically handles file encoding.
    It uses pathlib.Path for all file system interactions.
    """

    def __init__(self) -> None:
        """
        Initializes the FileOpener, creating a cache for file encodings.
        """
        # The cache uses resolved Path objects as keys to ensure that
        # different relative paths to the same file are treated as one.
        self.found_encoding: Dict[Path, str] = {}

    def _get_encoding(self, file_path: Path) -> str:
        """
        Detects, caches, and returns the encoding for a given file.
        If the encoding is already cached, it returns the cached value.

        :param file_path: A Path object for the file.
        :return: The detected encoding as a string.
        """
        resolved_path = file_path.resolve()
        if resolved_path in self.found_encoding:
            return self.found_encoding[resolved_path]

        try:
            file_bytes = file_path.read_bytes()
            if not file_bytes:
                # Default to UTF-8 for empty files.
                encoding = "utf-8"
            else:
                detection = chardet.detect(file_bytes)
                encoding = detection["encoding"] or "utf-8"  # Fallback to utf-8
                logger.debug(
                    f"Detected encoding for {file_path}: {encoding} with {detection['confidence']:.2f} confidence."
                )

            # A quick verification that the encoding works to avoid errors later.
            try:
                file_bytes.decode(encoding)
            except (UnicodeDecodeError, TypeError):
                logger.warning(
                    f"Detected encoding '{encoding}' failed to decode {file_path}. "
                    f"Falling back to 'utf-8'."
                )
                encoding = "utf-8"

            self.found_encoding[resolved_path] = encoding
            return encoding

        except IOError as e:
            logger.error(f"Could not read file {file_path}: {e}")
            # Re-raise or return a default? Re-raising is cleaner.
            raise

    def is_python_inside(self, file_path: Path) -> bool:
        """
        Checks if a file is a Python script.
        Returns True for .py files or extensionless files with a python shebang.

        :param file_path: A Path object for the file.
        :return: True if the file appears to be a Python script.
        """
        if not file_path.is_file():
            return False

        # Check by file extension first.
        if file_path.suffix == ".py":
            return True

        # For extensionless files, check for a shebang in the first line.
        if not file_path.suffix:
            try:
                # Read only the first line for efficiency.
                with self.open_this(file_path, "r") as file_handle:
                    first_line = file_handle.readline()
                if first_line.startswith("#") and "python" in first_line:
                    return True
            except (IOError, IndexError) as e:
                # Handles cases where the file can't be read or is empty.
                logger.debug(f"Could not check shebang for {file_path}: {e}")

        return False

    def read_this(self, file_path: Path) -> str:
        """
        Reads and returns the entire content of a file as a string.
        This method automatically handles the file's encoding.

        :param file_path: A Path object for the file.
        :return: The decoded text content of the file.
        """
        encoding = self._get_encoding(file_path)
        return file_path.read_text(encoding=encoding)

    def open_this(self, file_path: Path, mode: str = "r") -> IO[Any]:
        """
        Opens a file with the correct encoding.

        :param file_path: A Path object for the file.
        :param mode: The mode to open the file in (e.g., 'r', 'w', 'rb').
        :return: A file handle.
        """
        # Binary modes do not take an encoding argument.
        if "b" in mode:
            return file_path.open(mode)

        # For text modes, get the detected encoding.
        encoding = self._get_encoding(file_path)
        return file_path.open(mode, encoding=encoding)

    def read_metadata(self, file_path: Path) -> str:
        """
        Reads the 'version' from the [metadata] section of a .ini or .cfg file.

        :param file_path: A Path object for the configuration file.
        :return: The version string, or an empty string if not found.
        """
        config = configparser.ConfigParser()
        try:
            # Read the file content using our method that handles encoding.
            file_content = self.read_this(file_path)
            config.read_string(file_content)
            return config.get("metadata", "version", fallback="")
        except (IOError, configparser.Error) as e:
            logger.error(f"Failed to read or parse metadata from {file_path}: {e}")
            return ""
