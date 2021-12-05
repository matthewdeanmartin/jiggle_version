"""
Given a known package, find the 'central' module, the one whose version should sync with the package
"""


import logging
import os
from typing import List, Optional

from jiggle_version.file_opener import FileOpener

# so formatter doesn't remove.
from jiggle_version.module_finder import ModuleFinder

logger = logging.getLogger(__name__)


class CentralModuleFinder:
    """
    Finds modules in a folder. No assumptions about existance of PKG_INFO
    """

    def __init__(self, file_opener: FileOpener) -> None:
        """
        Initialize object
        :param file_opener:
        """
        self.file_opener = file_opener
        self.setup_source: Optional[str] = ""

        self.setup_file_name = ""
        self.find_setup_file_name()
        self.read_setup_py_source()
        self.package_name = self.parse_package_name()

    def find_setup_file_name(self) -> None:
        """
        Usually setup.py or setup
        """
        for file_path in [
            x
            for x in os.listdir(".")
            if os.path.isfile(x) and x in ["setup.py", "setup"]
        ]:
            if self.file_opener.is_python_inside(file_path):
                self.setup_file_name = file_path
                break

    def _read_file(self, file: str) -> Optional[str]:
        """
        Read any file, deal with encoding.
        :param file:
        :return:
        """
        if not self.setup_file_name:
            return None
        source = None
        if os.path.isfile(file):
            with self.file_opener.open_this(file, "r") as setup_py:
                source = setup_py.read()
        return source

    def read_setup_py_source(self) -> None:
        """
        Read setup.py to string
        :return:
        """
        if not self.setup_file_name:
            self.setup_source = ""
        if not self.setup_source:
            self.setup_source = self._read_file(self.setup_file_name)

    def parse_package_name(self) -> Optional[str]:
        """
        Extract likley module name from setup.py args
        :return:
        """
        if not self.setup_source:
            return None
        for row in self.setup_source.split("\n"):
            simplified_row = row.replace(" ", "").replace("'", '"').strip(" \t\n")
            if "name=" in simplified_row:
                if '"' in simplified_row:
                    return simplified_row.split('"')[1]

        name = ""  # self.execute_setup_name()
        if name:
            return name

        return ""

    # def execute_setup_name(self) -> Optional[str]:
    #     """
    #     Runs code, so this is a bit dangerous, especially if it isn't your own
    #     :return:
    #     """
    #     try:
    #         name = execute_get_text("python setup.py --name")
    #     except subprocess.CalledProcessError:
    #         # setup.py is not always in an executable state
    #         return None
    #     if not name:
    #         return None
    #     name = name.strip(" \n\t")
    #     if " " in name or "\n" in name:
    #         # likely includes print() that ruin results
    #         return None
    #     return name

    def find_central_module(self) -> Optional[str]:
        """
        Get the module that is the sole module, or the module
        that matches the package name/version
        :return:
        """
        # find modules.
        mf = ModuleFinder(self.file_opener)

        candidates = mf.find_by_any_method()

        sub_modules = []
        root_modules = []

        for candidate in candidates:
            if "." in candidate:
                sub_modules.append(candidate)
            else:
                root_modules.append(candidate)

        candidates = root_modules

        # remove junk. Junk only has meaning in the sense of finding the central module.
        candidates = self.remove_likely_non_central(candidates)
        if len(candidates) == 1:
            return candidates[0]

        # see if there is 1 out of the many with same name pkg_foo, module_foo
        if self.package_name:
            if self.package_name in candidates:
                return self.package_name

        # I don't understand the _ to - transformations.
        if self.package_name:
            if self.package_name.replace("-", "_") in candidates:
                return self.package_name.replace("-", "_")

        if self.package_name:
            if self.package_name.replace("-", "") in candidates:
                return self.package_name.replace("-", "")

        if self.package_name:
            if self.package_name.replace("_", "") in candidates:
                return self.package_name.replace("_", "")
        # see if there is 1 out of the many with version in sync- pkg_foo v1.2.3, module_bar v1.2.3
        # TODO:

        return None

    def remove_likely_non_central(self, candidates: List[str]) -> List[str]:
        """
        Stuff that is likely to be in find_packages(exclude...)
        :param candidates:
        :return:
        """
        if len(candidates) > 1:
            for unlikely in [
                "test",
                "tests",
                "example",
                "examples",
                "demo",
                "demos",
                "test_files",
                "doc",
                "docs",
            ]:
                if unlikely in candidates:
                    logger.warning(f"Assuming {unlikely} is not the project")
                    candidates.remove(unlikely)
                for candidate in candidates:
                    if candidate.startswith(unlikely):
                        logger.warning(f"Assuming {candidate} is not the project")
                        candidates.remove(candidate)
        return candidates
