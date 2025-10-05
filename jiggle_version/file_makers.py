from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FileMaker:
    """
    A utility class for creating common project files with default version information.
    """

    def __init__(self, project: Path) -> None:
        """
        Initializes the FileMaker.

        Args:
            project: The name of the project, used when creating config files.
        """
        self.project = project

    def create_version_file(
        self,
        path: Path,
        version: str = "0.0.0",
        docstring: str = "Auto-generated version file",
    ) -> None:
        """
        Creates a Python file containing a `__version__` dunder attribute.

        This method combines the logic of the original `create_init` and
        `create_version` methods. It ensures the parent directory exists
        before writing the file.

        Args:
            path: The full Path object where the file will be created.
            version: The initial version string to write into the file.
            docstring: A docstring to include in the generated file.
        """
        try:
            # Ensure the parent directory exists, creating it if necessary.
            path.parent.mkdir(parents=True, exist_ok=True)

            source = f"""# coding=utf-8
\"\"\"
{docstring}
\"\"\"
__version__ = "{version}"
"""
            # Use write_text for a simple and clean way to write the file.
            path.write_text(source, encoding="utf-8")
            logger.info(f"Successfully created version file at: {path}")

        except OSError as e:
            logger.error(f"Failed to create file at {path}: {e}")
            # Optionally, re-raise or handle the exception as needed.
            raise

    def create_setup_cfg(self, path: Path, version: str = "0.0.1") -> None:
        """
        Creates a basic setup.cfg file with metadata.

        This method ensures the parent directory exists before writing the file.

        Args:
            path: The full Path object where the file will be created.
            version: The initial version string to write into the file.
        """
        try:
            # Ensure the parent directory exists.
            path.parent.mkdir(parents=True, exist_ok=True)

            source = f"""[metadata]
name = {self.project}
version = {version}
"""
            path.write_text(source, encoding="utf-8")
            logger.info(f"Successfully created setup.cfg at: {path}")

        except OSError as e:
            logger.error(f"Failed to create file at {path}: {e}")
            raise
