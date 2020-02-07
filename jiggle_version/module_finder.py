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
import ast
import logging
import os
from typing import List, Optional

# so formatter doesn't remove.
from setuptools import find_packages

from jiggle_version.file_opener import FileOpener
from jiggle_version.utils import (
    first_value_in_dict,
    JiggleVersionException,
    parse_source_to_dict,
)

logger = logging.getLogger(__name__)


class ModuleFinder:
    """
    Finds modules in a folder.
    """

    def __init__(self, file_opener: FileOpener) -> None:
        self.file_opener = file_opener
        self.setup_source: Optional[str] = ""

    def _read_file(self, file: str) -> Optional[str]:
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

    def setup_py_source(self) -> Optional[str]:
        """
        Read setup.py to string
        """
        if not self.setup_source:
            self.setup_source = self._read_file("setup.py")
        if not self.setup_source:
            self.setup_source = self._read_file("setup")  # rare case
        return self.setup_source

    def extract_package_dir(self) -> Optional[str]:
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
        return None

    def find_by_any_method(self) -> List[str]:
        """
        Ensemble algorithm for finding package/module
        """
        packages = self.via_find_packages()
        print("found by find_packages() " + str(packages))

        if not packages:
            packages = self.find_top_level_modules_by_dunder_init()
            print("found by dunder_init folders " + str(packages))

        if not packages:
            packages = self.find_single_file_project()
            print("found by single file " + str(packages))

        return packages

    def via_find_packages(self) -> List[str]:
        """
        Use find_packages code to find modules. Can find LOTS of modules.
        :return:
        """
        packages: List[str] = []
        source = self.setup_py_source()
        if not source:
            return packages
        find_package_args = ""
        for row in source.split("\n"):
            if "find_packages" in row:
                logger.debug(row)
                if "find_packages()" in row:
                    packages = find_packages()
                else:
                    # noinspection PyBroadException
                    try:

                        find_package_args_source = row.split("(")[1].split(")")[0]
                        find_package_args = ast.literal_eval(find_package_args_source)
                        logger.debug(packages)
                    except:
                        logger.debug(source)
                        # raise
        if not find_package_args:
            packages = find_packages()
        else:
            # noinspection PyBroadException
            try:
                # signature find(cls, where='.', exclude=(), include=('*',)):
                packages = find_packages(find_package_args)
            except:
                packages = find_packages()

        return packages

    def find_top_level_modules_by_dunder_init(self) -> List[str]:
        """
        Find modules along side setup.py (or in current folder)

        Recreates what find_packages does.
        :return:
        """
        # TODO: use package_dirs
        packaged_dirs: Optional[str] = ""
        # noinspection PyBroadException
        try:
            # Right now only returns 1st.
            packaged_dirs = self.extract_package_dir()
        except:
            pass
        likely_src_folders = [".", "src", "lib"]
        if packaged_dirs and packaged_dirs not in likely_src_folders:
            likely_src_folders.append(packaged_dirs)

        candidates = []
        for likely_src in likely_src_folders:
            if not os.path.isdir(likely_src):
                continue
            folders = [
                f
                for f in os.listdir(likely_src)
                if os.path.isdir(os.path.join(likely_src, f))
            ]

            for folder in folders:
                if os.path.isfile(os.path.join(likely_src, folder, "__init__.py")):
                    # dunder_source = self.file_opener.read_file(folder + "/__init__.py")
                    candidates.append(folder)

        return list({x for x in candidates if x})

    # TODO: use setup.py line to find package
    # packages=find_packages('src'),
    # packages=['ajax_select'],
    # python setup.py --provides

    def find_single_file_project(self) -> List[str]:
        """
        Take first non-setup.py python file. What a mess.
        :return:
        """
        # TODO: use package_dirs
        packaged_dirs: Optional[str] = ""
        # noinspection PyBroadException
        try:
            # Right now only returns 1st.
            packaged_dirs = self.extract_package_dir()
        except:
            pass
        likely_src_folders = [".", "src/"]
        if packaged_dirs:
            likely_src_folders.append(packaged_dirs)

        candidates = []
        for likely_src in likely_src_folders:
            if not os.path.isdir(likely_src):
                continue
            files = [f for f in os.listdir(likely_src) if os.path.isfile(f)]

            # BUG: doesn't deal with src/foo/bar.py
            for file in files:
                if file.endswith("setup.py") or file == "setup":
                    continue  # duh
                if file.endswith(".py"):
                    candidate = file.replace(".py", "")
                    if candidate != "setup":
                        candidates.append(candidate)
                else:
                    if self.file_opener.is_python_inside(file):
                        candidates.append(file)
        return candidates

    # def validate_found_project(self, candidates):  # type: (List[str]) -> None
    #     """
    #     Should be only 1 project
    #     :param candidates:
    #     :return:
    #     """
    #     if len(candidates) > 1:
    #         message = "Found multiple possible projects : " + str(candidates)
    #         logger.error(message)
    #         die(-1, message)
    #         return
    #     if not candidates:
    #         # we can still update setup.py
    #         logger.warning(
    #             "Found no project. Expected a folder in current directory to contain a __init__.py "
    #             "file. Use --source, --project for other scenarios"
    #         )
    #         # die(-1)
    #         # return
