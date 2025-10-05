"""
Finds project by folder & source inspection.  Enables zero config by not
asking the user something we can probably infer.

Naming:
    package = named by setup(), recapped in setup.cfg & PKG_INFO
        - developer writes version in setup(), setup.cfg,
        - setup.py sdist will output to zip file name, PKG_INFO
    central module = module whose name matches package & version matches package
        - Doesn't have to match package ver, often does
        - Has version in file if single file module
        - Has version in __init__ (per PEP advice) as __version__
    module = .py file next to setup.py or folder with __init__ next to setup.py
        - has __version__ somewhere in "header"
    submodule = files in folder with __init__
        - can have version in "header", rarely does

    Confusing naming: find_packages returns modules and submodules.
    AFAIK, no PEP has concept of central module, but the fact people version them together implies
    people think there is.

Weird States:
    setup.py only
    missing __init__.py
    module in /SRC/ folder and uses package_dir
    only 1 module (i.e. a central module), but name of package != module name



TODO: confounds two concepts:
    package - 1, has 1 version from setup.py/setup.cfg (might be same as central module)
    modules -
        0 - setup.py only, degenerate case or it is just not really a python dist (maybe jquery!)
        1 - easy scenario
        2+ - could each have own version
        2+ - but 1 is the central module and the rest are unversionsed test/demo/examples/etc

"""

from __future__ import annotations

import ast
import logging
from pathlib import Path
from typing import List, Optional

# Assuming these modules are part of the same package and are structured correctly.
from jiggle_version.file_opener import FileOpener
from jiggle_version.find_modules_function import find_packages_recursively
from jiggle_version.utils import (
    JiggleVersionException,
    first_value_in_dict,
    parse_source_to_dict,
)

logger = logging.getLogger(__name__)


class ModuleFinder:
    """
    Finds modules in a folder.
    """

    def __init__(self, file_opener: FileOpener) -> None:
        """Initializes the finder with a FileOpener instance."""
        self.file_opener = file_opener
        self.setup_source: Optional[str] = None

    def _read_file(self, file_path: Path) -> Optional[str]:
        """
        Reads a file if it exists, using the FileOpener to handle encoding.
        """
        if file_path.is_file():
            return self.file_opener.read_this(file_path)
        return None

    def setup_py_source(self) -> Optional[str]:
        """
        Reads setup.py (or extensionless 'setup') to a string and caches it.
        """
        if self.setup_source is None:
            self.setup_source = self._read_file(Path("setup.py"))
            if not self.setup_source:
                self.setup_source = self._read_file(Path("setup"))  # rare case
        return self.setup_source

    def extract_package_dir(self) -> Optional[str]:
        """
        Get the package_dir dictionary from the setup.py source.
        """
        # package_dir={'': 'lib'},
        source = self.setup_py_source()
        if not source:
            # this happens when the setup.py file is missing
            return None

        # sometimes: 'package_dir'     : {'': 'src'},
        # sometimes: package_dir={...}
        if "package_dir=" in source:
            dict_src = parse_source_to_dict(source)
            if not dict_src.endswith("}"):
                raise JiggleVersionException(
                    "Either this is hard to parse or we have 2+ src folders"
                )
            try:
                paths_dict = ast.literal_eval(dict_src)
            except ValueError:
                logger.error(f"Could not parse package_dir from source: {dict_src}")
                return ""

            if "" in paths_dict:
                candidate = Path(paths_dict[""])
                if candidate.is_dir():
                    return str(candidate)
            if len(paths_dict) == 1:
                candidate = Path(first_value_in_dict(paths_dict))
                if candidate.is_dir():
                    return str(candidate)
            else:
                raise JiggleVersionException(
                    "Have path_dict, but has more than one path."
                )
        return None

    def find_local_packages(self) -> List[Path]:
        """
        Finds all modules and submodules by walking the directory tree,
        looking for __init__.py files.
        """
        # Determine where to start the search. This mimics the behavior of
        # find_packages() which can take a 'where' argument, often defined
        # in setup.py via 'package_dir'.
        package_dir_str = self.extract_package_dir()

        search_paths: List[Path] = []
        if package_dir_str and Path(package_dir_str).is_dir():
            search_paths.append(Path(package_dir_str))
        else:
            # If package_dir is not specified or invalid, check common locations.
            for common_dir in ["src", "lib"]:
                if Path(common_dir).is_dir():
                    search_paths.append(Path(common_dir))
            if not search_paths:
                # Fallback to the current directory
                search_paths.append(Path("."))

        all_packages: set[Path] = set()
        for path in search_paths:
            # Pass the string representation of the path to maintain compatibility
            # with the external find_packages_recursively function.
            found = find_packages_recursively(path)
            for pkg in found:
                all_packages.add(pkg)

        return list(all_packages)

    def find_by_any_method(self) -> List[Path]:
        """Tries multiple strategies to find packages/modules."""
        packages = self.find_local_packages()
        logger.info(f"found by custom package discovery: {packages}")

        if not packages:
            packages = self.find_top_level_modules_by_dunder_init()
            logger.info(f"found by dunder_init folders: {packages}")

        if not packages:
            packages = self.find_single_file_project()
            logger.info(f"found by single file: {packages}")

        return packages

    def find_top_level_modules_by_dunder_init(self) -> List[Path]:
        """
        Finds modules that are directories with an __init__.py file.
        This recreates the basic behavior of setuptools.find_packages().
        """
        # TODO: use package_dirs more robustly
        packaged_dirs_str: Optional[str] = ""
        try:
            packaged_dirs_str = self.extract_package_dir()
        except JiggleVersionException:
            pass

        likely_src_folders = {Path("."), Path("src"), Path("lib")}
        if packaged_dirs_str:
            likely_src_folders.add(Path(packaged_dirs_str))

        candidates: list[Path] = []
        for likely_src in likely_src_folders:
            if not likely_src.is_dir():
                continue

            for item in likely_src.iterdir():
                # Check if the item is a directory and contains an __init__.py
                if item.is_dir() and (item / "__init__.py").is_file():
                    candidates.append(Path(item.name))

        return list(set(candidates))

    def find_single_file_project(self) -> List[Path]:
        """
        Finds projects that consist of a single Python file.
        """
        # TODO: use package_dirs more robustly
        packaged_dirs_str: Optional[str] = ""
        try:
            packaged_dirs_str = self.extract_package_dir()
        except JiggleVersionException:
            pass

        likely_src_folders = {Path("."), Path("src")}
        if packaged_dirs_str:
            likely_src_folders.add(Path(packaged_dirs_str))

        candidates: list[Path] = []
        for likely_src in likely_src_folders:
            if not likely_src.is_dir():
                continue

            # BUG: doesn't deal with src/foo/bar.py (original bug noted)
            for item in likely_src.iterdir():
                if not item.is_file():
                    continue

                if item.name == "setup.py" or item.name == "setup":
                    continue

                # Check for .py extension
                if item.suffix == ".py":
                    # Use stem to get the filename without the extension
                    candidates.append(Path(item.stem))
                else:
                    # Check for python shebang in extensionless files
                    if self.file_opener.is_python_inside(item):
                        candidates.append(Path(item.name))
        return candidates
