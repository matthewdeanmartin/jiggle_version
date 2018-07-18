# coding=utf-8
"""
Finds project by folder & source inspection.  Enables zero config by not
asking the user something we can probably infer.

# TODO: package_dir={'': 'src'},
"""
import ast
import os
import io
import logging
from typing import List, Optional

# so formatter doesn't remove.
from setuptools import find_packages

logger = logging.getLogger(__name__)

_ = List, Optional


class ModuleFinder(object):
    def __init__(self): # type: () -> None
        pass

    def read_file(self, file):  # type: (str) -> Optional[str]
        setup_source = None
        if os.path.isfile("setup.py"):
            try:
                with io.open("setup.py", "r", encoding="utf-8") as setup_py:
                    setup_source = setup_py.read()
            except UnicodeDecodeError:
                with io.open("setup.py", "r", encoding="ascii") as setup_py:
                    setup_source = setup_py.read()
        return setup_source

    def setup_py_source(self):  # type: () -> Optional[str]
        return self.read_file("setup.py")

    def name_from_setup_py(self): # type: () -> str
        source = self.setup_py_source()
        if not source:
            return ""
        for row in source.split("\n"):
            if "name" in row:
                simplified_row = row.replace(" ", "").replace("'", '"').strip(" \t\n")
                if '"' in simplified_row:
                    return simplified_row.split('"')[1]
        return ""

    def via_find_packages(self):# type: () -> List[str]
        packages = []
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
                        logger.debug(packages)
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
                dunder_source = self.read_file(folder + "/__init__.py")
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
        # TODO: parse setup.py
        # TODO: parse setup.cfg
        if not candidates:
            candidates = candidates + self.find_single_file_project()
            # if not candidates:
            #     print(setup)
        if not candidates:
            candidates = candidates + self.find_malformed_single_file_project()
            # if not candidates:
            #     print(setup)

        candidates = list(set([x for x in candidates if x]))

        # too many
        if len(candidates) == 0:
            candidates.extend(self.via_find_packages())
            candidates = list(set([x for x in candidates if x]))

        if len(candidates) > 1:
            for unlikely in ["test", "tests", "example", "demo", "test_files"]:
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

    def find_malformed_single_file_project(self):# type: () -> List[str]
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
                    firstline = open(file, "r").readline()
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

    def find_single_file_project(self):# type: () -> List[str]
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
            logger.error("Found multiple possible projects : " + str(candidates))
            exit(-1)
            return
        if not candidates:
            # we can still update setup.py
            logger.warning(
                "Found no project. Expected a folder in current directory to contain a __init__.py "
                "file. Use --source, --project for other scenarios"
            )
            # exit(-1)
            # return
