"""
Deals with package level concepts, not module level concepts.
"""

from __future__ import annotations

import ast
import logging
import os
from pathlib import Path
from typing import List, Optional

from jiggle_version.file_opener import FileOpener
from jiggle_version.find_modules_function import find_packages_recursively
from jiggle_version.utils import (
    JiggleVersionException,
    first_value_in_dict,
    parse_source_to_dict,
)

logger = logging.getLogger(__name__)


class PackageInfoFinder:
    """
    Finds modules in a folder.
    """

    def __init__(self, file_opener: FileOpener) -> None:
        self.file_opener = file_opener
        self.setup_source: Optional[str] = ""

    def _read_file(self, file: Path) -> Optional[str]:
        """
        Read any file, deal with encoding.
        :param file:
        :return:
        """
        source = None
        if file.is_file():
            with self.file_opener.open_this(file, "r") as setup_py:
                source = setup_py.read()
        return source

    def setup_py_source(self) -> Optional[str]:
        """
        Read setup.py to string
        """
        if not self.setup_source:
            self.setup_source = self._read_file(Path("setup.py"))  # rare case

        if not self.setup_source:
            self.setup_source = self._read_file(Path("setup"))  # rare case
        return self.setup_source

    def name_from_setup_py(self) -> str:
        """
        Extract likley module name from setup.py args
        :return:
        """
        source = self.setup_py_source()
        if not source:
            return ""
        for row in source.split("\n"):
            #
            if "packages=" in row:
                simplified_row = row.replace(" ", "").replace("'", '"').strip(" \t\n")
                if '"' in simplified_row:
                    return simplified_row.split('"')[1]

            if "name=" in row:
                simplified_row = row.replace(" ", "").replace("'", '"').strip(" \t\n")
                if '"' in simplified_row:
                    return simplified_row.split('"')[1]
        return ""

    def extract_package_dir(self) -> Optional[str]:
        """
        Get the package_dir dictionary from source
        :return:
        """
        # package_dir={'': 'lib'},
        source = self.setup_py_source()
        if not source:
            logger.warning("No setup.py")
            # this happens when the setup.py file is missing
            return None

        # sometime
        # 'package_dir'      : {'': 'src'},
        # sometimes
        # package_dir={...}
        if "package_dir=" in source:
            dict_src = parse_source_to_dict(source)
            if not dict_src.endswith("}"):
                raise JiggleVersionException(
                    "Either this is hard to parse or we have 2+ src foldrs"
                )
            try:
                paths_dict = ast.literal_eval(dict_src)
            except ValueError:
                logger.error(source + ": " + dict_src)
                return ""

            if "" in paths_dict:
                candidate = paths_dict[""]
                if os.path.isdir(candidate):
                    return str(candidate)
            if len(paths_dict) == 1:
                candidate = first_value_in_dict(paths_dict)
                if os.path.isdir(candidate):
                    return str(candidate)
            else:
                raise JiggleVersionException(
                    "Have path_dict, but has more than one path."
                )
        else:
            logger.warning("package_dir not in setup.py")
        return None

    def via_find_packages(self) -> List[Path]:
        """
        Use find_packages code to find modules. Can find LOTS of modules.
        """
        packages: List[Path] = []
        source = self.setup_py_source()
        if not source:
            return packages
        for row in source.split("\n"):
            if "find_packages" in row:
                logger.debug(row)
                if "find_packages()" in row:
                    packages = find_packages_recursively(Path("."))
                else:

                    try:
                        value = row.split("(")[1].split(")")[0]
                        packages = find_packages_recursively(ast.literal_eval(value))
                        logger.debug(str(packages))
                    except Exception:
                        logger.debug(source)
                        # raise

        return packages

    def find_project(self) -> List[Path]:
        """
        Get all candidate projects
        :return:
        """
        folders = [Path(f) for f in os.listdir(".") if Path(f).is_dir()]

        candidates = []
        setup = self.setup_py_source()
        for folder in folders:
            if os.path.isfile(folder / "/__init__.py"):
                dunder_source = self._read_file(folder / "/__init__.py")
                project = folder
                if setup:
                    # prevents test folders & other junk
                    in_setup = (
                        f"'{project}" not in setup and f'"{project}"' not in setup
                    )
                    in_dunder = (
                        f"'{dunder_source}" not in setup
                        and f'"{dunder_source}"' not in setup
                    )

                    if not in_setup and not in_dunder:
                        continue

                candidates.append(folder)

        # TODO: parse setup.cfg
        if not candidates:
            candidates = candidates + self.find_single_file_project()
        if not candidates:
            candidates = candidates + self.find_malformed_single_file_project()

        candidates = list({x for x in candidates if x})

        # too many
        if not candidates:
            candidates.extend(self.via_find_packages())
            candidates = list({x for x in candidates if x})

        if len(candidates) > 1:
            for unlikely in [
                "test",
                "tests",
                "example",
                "examples",
                "demo",
                "demos",
                "test_files",
            ]:
                if unlikely in candidates:
                    logger.warning(f"Assuming {unlikely} is not the project")
                    candidates.remove(Path(unlikely))
                if len(candidates) == 1:
                    break

        # too few or too many
        if len(candidates) != 1:
            likely_name = self.name_from_setup_py()
            if likely_name in candidates:
                return [Path(likely_name)]
        return list({x for x in candidates if x})

    # TODO: use setup.py line to find package
    # packages=find_packages('src'),
    # packages=['ajax_select'],

    def find_malformed_single_file_project(self) -> List[Path]:
        """
        Take first non-setup.py python file. What a mess.
        :return:
        """
        files = [Path(f) for f in os.listdir(".") if Path(f).is_file()]

        candidates: list[Path] = []
        # project misnamed & not in setup.py

        for file in files:
            if file.name.endswith("setup.py") or not file.name.endswith(".py"):
                continue  # duh

            # candidate = file.replace(".py", "")
            # if candidate != "setup":
            #     candidates.append(candidate)
            #     # return first
            #     return candidates

        # files with shebang
        for file in files:
            if file.name.endswith("setup.py"):
                continue  # duh

            if "." not in str(file):
                candidate = file

                try:
                    with self.file_opener.open_this(file, "r") as file_handle:
                        firstline = file_handle.readline()
                    if (
                        firstline.startswith("#")
                        and "python" in firstline
                        and str(candidate) in (self.setup_py_source() or "")
                    ):
                        candidates.append(candidate)
                        return candidates
                except Exception:
                    pass
        # default.
        return candidates

    def find_single_file_project(self) -> List[Path]:
        """
        Find well-formed singler file project
        """
        files = [Path(f) for f in os.listdir(".") if Path(f).is_file()]

        candidates: list[Path] = []
        setup_source = self.setup_py_source()

        for file in files:
            if file.name.endswith("setup.py") or not file.name.endswith(".py"):
                continue  # duh

            if setup_source:
                if file.name.replace(".py", "") in setup_source:
                    candidate = file.name.replace(".py", "")
                    if candidate != "setup":
                        candidates.append(Path(candidate))

        return candidates

    def validate_found_project(self, candidates: List[str]) -> None:
        """
        Should be only 1 project
        """
        if len(candidates) > 1:
            message = "Found multiple possible projects : " + str(candidates)
            logger.error(message)
            raise JiggleVersionException(message)
        if not candidates:
            # we can still update setup.py
            logger.warning(
                "Found no project. Expected a folder in current directory to contain a __init__.py "
                "file. Use --source, --project for other scenarios"
            )
            # die(-1)
            # return
