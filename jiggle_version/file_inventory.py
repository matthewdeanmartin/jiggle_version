"""
Make dupe file lists go away.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class FileInventory:
    """
    Manages an inventory of files within a project that may contain version information.
    Uses pathlib for modern and robust path operations.
    """

    def __init__(
        self,
        project: Path,
        src: Path,
        custom_source_files: Optional[List[str]] = None,
        custom_config_files: Optional[List[str]] = None,
        custom_text_files: Optional[List[str]] = None,
    ) -> None:
        """
        Initializes the file inventory, defining potential locations for version strings.

        Args:
            project: The name of the project module/directory (e.g., 'my_package').
            src: The source directory path where the project resides.
            custom_source_files: An optional list of additional source file names to check
                                 within the project directory.
            custom_config_files: An optional list of additional config file names to check
                                 in the source directory.
            custom_text_files: An optional list of additional text file names to check
                               in the source directory for a raw version string.
        """
        self.project = project
        self.src_path = Path(src)
        self.project_root: Path = self.src_path / self.project

        # --- Source Files (typically inside the project folder) ---
        source_filenames = [
            "__init__.py",
            "__version__.py",
            "_version.py",
            "version.py",
            "__about__.py",
            "__meta__.py",
            "__pkg__.py",
        ]
        if custom_source_files:
            source_filenames.extend(custom_source_files)

        # Use a list comprehension to build the full paths.
        # This will only generate paths if the project root directory actually exists.
        self.source_files: List[Path] = [
            self.project_root / file
            for file in source_filenames
            if self.project_root.is_dir()
        ]

        # --- Config Files (typically in the root source directory) ---
        config_filenames = ["setup.cfg"]
        if custom_config_files:
            config_filenames.extend(custom_config_files)

        self.config_files: List[Path] = [
            self.src_path / file for file in config_filenames
        ]

        # --- Text Files (for raw version strings) ---
        text_filenames = [
            "version.txt",
            "VERSION.txt",
            "_version.txt",
            "_VERSION.txt",
            "VERSION",
            "version",
            "_VERSION",
            "_version",
            ".version",
            ".VERSION",
        ]
        if custom_text_files:
            text_filenames.extend(custom_text_files)

        self.text_files: List[Path] = [self.src_path / file for file in text_filenames]

        # --- Default text file to create if one doesn't exist ---
        self.default_text_file: Path = self.src_path / "VERSION.txt"
