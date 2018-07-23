# coding=utf-8
"""
Deals with package level concepts, not module level concepts.
"""


from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import ast
import logging
import os
import sys
from typing import List, Optional

# so formatter doesn't remove.
from setuptools import find_packages

from jiggle_version.file_inventory import FileInventory
from jiggle_version.file_opener import FileOpener
from jiggle_version.utils import die, first_value_in_dict, JiggleVersionException

logger = logging.getLogger(__name__)

_ = List, Optional, FileInventory
if sys.version_info.major == 3:
    unicode = str


class ModuleFinder(object):
    """
    Finds modules in a folder.
    """

    def __init__(self, file_opener):  # type: (FileOpener) -> None
        self.file_opener = file_opener
        self.setup_source = ""

    def _read_file(self, file):  # type: (str) -> Optional[str]
        """
        Read any file, deal with encoding.
        :param file:
        :return:
        """
        source = None
        if os.path.isfile(file):
            with self.file_opener.open_this(file, "r") as setup_py:
                source = setup_py.read()
        return source

    def setup_py_source(self):  # type: () -> Optional[str]
        """
        Read setup.py to string
        :return:
        """
        if not self.setup_source:
            source = self._read_file("setup")  # rare case
        return self.setup_source

    def name_from_setup_py(self):  # type: () -> str
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

    def extract_package_dir(self):  # type: () -> Optional[str]
        """
        Get the package_dir dictionary from source
        :return:
        """
        # package_dir={'': 'lib'},
        source = self.setup_py_source()
        if not source:
            # this happens when the setup.py file is missing
            return None

        # sometime
        # 'package_dir'      : {'': 'src'},
        # sometimes
        # package_dir={...}
        if "package_dir=" in source:
            line = source.replace("\n", "")
            line = source.split("package_dir")[1]
            fixed = ""
            for char in line:
                fixed += char
                if char == "}":
                    break
            line = fixed

            simplified_line = line.strip(" ,").replace("'", '"')

            parts = simplified_line.split("=")

            dict_src = parts[1].strip(" \t")
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
                    return unicode(candidate)
            if len(paths_dict) == 1:
                candidate = first_value_in_dict(paths_dict)
                if os.path.isdir(candidate):
                    return unicode(candidate)
            else:
                raise JiggleVersionException(
                    "Have path_dict, but has more than one path."
                )
        return None

    def via_find_packages(self):  # type: () -> List[str]
        """
        Use find_packages code to find modules. Can find LOTS of modules.
        :return:
        """
        packages = []  # type: List[str]
        source = self.setup_py_source()
        if not source:
            return packages
        for row in source.split("\n"):
            if "find_packages" in row:
                logger.debug(row)
                if "find_packages()" in row:
                    packages = find_packages()
                else:
                    try:
                        value = row.split("(")[1].split(")")[0]
                        packages = find_packages(ast.literal_eval(value))
                        logger.debug(unicode(packages))
                    except:
                        logger.debug(source)
                        # raise

        return packages

    def find_project(self):  # type: () -> List[str]
        """
        Get all candidate projects
        :return:
        """
        folders = [f for f in os.listdir(".") if os.path.isdir(f)]

        candidates = []
        setup = self.setup_py_source()
        for folder in folders:
            if os.path.isfile(folder + "/__init__.py"):
                dunder_source = self._read_file(folder + "/__init__.py")
                project = folder
                if setup:
                    # prevents test folders & other junk
                    in_setup = (
                        "'{0}".format(project) not in setup
                        and '"{0}"'.format(project) not in setup
                    )
                    in_dunder = (
                        "'{0}".format(dunder_source) not in setup
                        and '"{0}"'.format(dunder_source) not in setup
                    )

                    if not in_setup and not in_dunder:
                        continue

                candidates.append(folder)

        # TODO: parse setup.cfg
        if not candidates:
            candidates = candidates + self.find_single_file_project()
        if not candidates:
            candidates = candidates + self.find_malformed_single_file_project()

        candidates = list(set([x for x in candidates if x]))

        # too many
        if not candidates:
            candidates.extend(self.via_find_packages())
            candidates = list(set([x for x in candidates if x]))

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
                    logger.warning("Assuming {0} is not the project".format(unlikely))
                    candidates.remove(unlikely)
                if len(candidates) == 1:
                    break

        # too few or too many
        if len(candidates) != 1:
            likely_name = self.name_from_setup_py()
            if likely_name in candidates:
                return [likely_name]
        return list(set([x for x in candidates if x]))

    # TODO: use setup.py line to find package
    # packages=find_packages('src'),
    # packages=['ajax_select'],

    def find_malformed_single_file_project(self):  # type: () -> List[str]
        """
        Take first non-setup.py python file. What a mess.
        :return:
        """
        files = [f for f in os.listdir(".") if os.path.isfile(f)]

        candidates = []
        # project misnamed & not in setup.py

        for file in files:
            if file.endswith("setup.py") or not file.endswith(".py"):
                continue  # duh

            candidate = file.replace(".py", "")
            if candidate != "setup":
                candidates.append(candidate)
                # return first
                return candidates

        # files with shebang
        for file in files:
            if file.endswith("setup.py"):
                continue  # duh

            if not "." in file:
                candidate = files
                try:
                    firstline = self.file_opener.open_this(file, "r").readline()
                    if (
                        firstline.startswith("#")
                        and "python" in firstline
                        and candidate in self.setup_py_source()
                    ):
                        candidates.append(candidate)
                        return candidates
                except:
                    pass
        # default.
        return candidates

    def find_single_file_project(self):  # type: () -> List[str]
        """
        Find well formed singler file project
        :return:
        """
        files = [f for f in os.listdir(".") if os.path.isfile(f)]

        candidates = []
        setup_source = self.setup_py_source()

        for file in files:
            if file.endswith("setup.py") or not file.endswith(".py"):
                continue  # duh

            if setup_source:
                if file.replace(".py", "") in setup_source:
                    candidate = file.replace(".py", "")
                    if candidate != "setup":
                        candidates.append(candidate)

        return candidates

    def validate_found_project(self, candidates):  # type: (List[str]) -> None
        """
        Should be only 1 project
        :param candidates:
        :return:
        """
        if len(candidates) > 1:
            message = "Found multiple possible projects : " + unicode(candidates)
            logger.error(message)
            die(-1, message)
            return
        if not candidates:
            # we can still update setup.py
            logger.warning(
                "Found no project. Expected a folder in current directory to contain a __init__.py "
                "file. Use --source, --project for other scenarios"
            )
            # die(-1)
            # return
