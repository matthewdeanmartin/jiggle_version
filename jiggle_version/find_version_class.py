# coding=utf-8
"""
Just discover version and if possible, the schema.

TODO: __version_info__ = (3, 0, 0, 'a0')
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import ast
import codecs
import io
import logging
import os.path
import re
from typing import List, Optional, Dict, Any

import chardet
from semantic_version import Version

from jiggle_version.file_inventory import FileInventory
from jiggle_version.schema_guesser import version_object_and_next
from jiggle_version.utils import (
    merge_two_dicts,
    first_value_in_dict,
    JiggleVersionException,
)

try:
    import configparser
except ImportError:
    # Python 2.x fallback
    import ConfigParser as configparser


if sys.version_info.major == 3:
    unicode = str

logger = logging.getLogger(__name__)

# contrive usage so black doesn't remove the import
_ = List, Optional, Dict, Any

# don't do this.
# execfile('...sample/version.py')
def version_by_ast(file):  # type: (str) -> str
    """
    Safer way to 'execute' python code to get a simple value
    :param file:
    :return:
    """
    with open(file) as input_file:
        for line in input_file:
            if line.startswith("__version__"):
                return ast.parse(line).body[0].value.s


# ----
# https://packaging.python.org/guides/single-sourcing-package-version/
here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):  # type: (Any)->str
    with codecs.open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


def find_version_by_regex(*file_paths):  # type: (Any)->str
    """
    find_version("package", "__init__.py")
    :param file_paths:
    :return:
    """
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# ----


class FindVersion(object):
    """
    Because OOP.
    """

    def __init__(self, project, source, debug=False):  # type: (str, str, bool) ->None
        """
        Entry point
        """
        # if not project:
        #     raise JiggleVersionException("Can't continue, no project name")

        if source is None:
            raise JiggleVersionException(
                'Can\'t continue, source directory is None, should be ""\ for current dir'
            )

        self.PROJECT = project
        self.SRC = source
        self.is_folder_project = os.path.isdir(os.path.join(self.SRC, self.PROJECT))
        self.is_file_project = os.path.isfile(
            os.path.join(self.SRC, self.PROJECT) + ".py"
        )
        if not self.is_folder_project and not self.is_file_project:
            logger.warning(
                "Can't find module, typically a packages has a .py file or folder with module name : "
                + unicode(self.SRC + self.PROJECT)
                + " - can only update setup.py and text files."
            )

        self.strict = True
        self.DEBUG = False
        # logger.debug("Will expect {0} at path {1}{0} ".format(self.PROJECT, self.SRC))

        self.version = None  # type: Optional[Version]
        self.create_configs = False

        # for example, do we create __init__.py which changes behavior
        self.create_all = False

        self.file_inventory = FileInventory(self.PROJECT, self.SRC)

    def find_any_valid_version(self):  # type: () -> str
        """
        Find version candidates, return first (or any, since they aren't ordered)

        Blow up if versions are not homogeneous
        :return:
        """
        versions = self.all_current_versions()
        if len(versions) > 1:
            if not self.all_versions_equal(versions):
                if not self.all_versions_equal(versions):
                    almost_same = self.almost_the_same_version(
                        [x for x in versions.values()]
                    )
                    if almost_same:
                        # TODO: disable with strict option
                        logger.warning(
                            "Version very by a patch level, will use greater."
                        )
                        return unicode(almost_same)

        if not versions.keys():
            raise JiggleVersionException("Noooo! Must find a value")
            return "0.1.0"
        return unicode(first_value_in_dict(versions))

    def almost_the_same_version(
        self, version_list
    ):  # type: (List[str]) -> Optional[str]
        version_list = list(set(version_list))

        sem_ver_list = list(
            set([unicode(Version(x)) for x in version_list])
        )  # type: List[Version]
        if len(sem_ver_list) == 2:
            if (
                sem_ver_list[0] == unicode(Version(sem_ver_list[1]).next_patch())
                or unicode(Version(sem_ver_list[0]).next_patch()) == sem_ver_list[1]
            ):
                if sem_ver_list[0] > sem_ver_list[1]:
                    return unicode(sem_ver_list[0])
                return unicode(sem_ver_list[1])
        return None

    def validate_current_versions(self):  # type: () -> bool
        """
        Can a version be found? Are all versions currently the same? Are they valid sem ver?
        :return:
        """
        versions = self.all_current_versions()
        for ver, version in versions.items():
            if "Invalid Semantic Version" in version:
                logger.error(
                    "Invalid versions, can't compare them, can't determine if in sync"
                )
                return False

        if not versions:
            logger.warning("Found no versions, will use default 0.1.0")
            return True

        if not self.all_versions_equal(versions):
            if self.almost_the_same_version([x for x in versions.values()]):
                # TODO: disable with strict option
                logger.warning("Version very by a patch level, will use greater.")
                return True
            logger.error("Found various versions, how can we rationally pick?")
            logger.error(unicode(versions))
            return False

        for key, version in versions.items():
            return True
        return False

    def all_current_versions(self):  # type: () ->Dict[str,str]
        """
        Track down all the versions & compile into one dictionary
        :return:
        """
        versions = {}  # type: Dict[str,str]
        for file in self.file_inventory.source_files:

            if not os.path.isfile(file):
                continue
            vers = self.find_dunder_version_in_file(file)
            versions = merge_two_dicts(versions, vers)

        for finder in [self.read_metadata, self.read_text, self.read_setup_py]:
            more_vers = finder()
            versions = merge_two_dicts(versions, more_vers)

        copy = {}  # type: Dict[str,str]
        for key, version in versions.items():
            try:
                _ = version_object_and_next(version)
                copy[key] = version
            except:
                logger.error(
                    "Invalid Version Schema - not Semantic Version, not Pep 440 -  "
                    + version
                )
                copy[key] = (
                    "Invalid Version Schema - not Semantic Version, not Pep 440 : "
                    + unicode(version)
                )
        return copy

    def all_versions_equal(self, versions):  # type: (Dict[str,str]) -> bool
        """
        Verify that all the versions are the same.
        :param versions:
        :return:
        """
        if len(versions) <= 1:
            return True

        semver = None
        for key, version in versions.items():
            if semver is None:
                try:
                    _ = version_object_and_next(version)
                except ValueError:
                    logger.error("Invalid version at:" + unicode((key, version)))
                    return False
                continue
            try:
                version_as_version, _, __ = version_object_and_next(version)
            except:
                return False
            if version_as_version != semver:
                return False
        return True

    def read_setup_py(self):  # type: ()-> Dict[str,str]
        """
        Extract from setup.py's setup() arg list.
        :return:
        """
        found = {}
        setup_py = os.path.join("setup.py")

        if not os.path.isfile(setup_py):
            if self.strict:
                logger.debug(os.getcwd())
                logger.debug(os.listdir(os.getcwd()))
                raise JiggleVersionException(
                    "Can't find setup.py : {0}, path :{1}".format(setup_py, self.SRC)
                )
            else:
                return found

        encoding = chardet.detect(io.open("setup.py", "rb").read())
        logger.debug(unicode(encoding))
        with io.open(setup_py, "r", encoding=encoding["encoding"]) as infile:
            for line in infile:
                simplified_line = line.replace(" ", "").replace("'", '"')
                if sum([1 for x in simplified_line if x == ","]) > 1:
                    comma_parts = simplified_line.split(",")
                    for part in comma_parts:

                        if "version" in part:
                            simplified_line = part

                # could be more than 1!
                if 'version="' in simplified_line:
                    version = simplified_line.split('"')[1]
                    if not version:
                        logging.warn("Can't find all of version string " + line)
                        continue
                    found[setup_py] = version
                    continue
                if '__version__="' in simplified_line:
                    version = simplified_line.split('"')[1]
                    if not version:
                        logging.warn("Can't find all of version string " + line)
                        continue
                    found[setup_py] = version
        return found

    def read_text(self):  # type: () ->Dict[str,str]
        """
        Get version out of ad-hoc version.txt
        :return:
        """
        found = {}
        for file in self.file_inventory.text_files:
            if not os.path.isfile(file):
                continue
            with open(file, "r") as infile:
                text = infile.readline()
            found[file] = text.strip(" \n")
        return found

    def read_metadata(self):  # type: () ->Dict[str,str]
        """
        Get version out of a .ini file (or .cfg)
        :return:
        """
        config = configparser.ConfigParser()
        config.read(self.file_inventory.config_files[0])
        try:
            return {"setup.cfg": config["metadata"]["version"]}
        except KeyError:
            return {}

    def find_dunder_version_in_file(self, full_path):  # type: (str)-> Dict[str,str]
        """
        Find __version__ in a source file
        :param full_path:
        :return:
        """
        versions = {}
        encoding = chardet.detect(io.open(full_path, "rb").read())
        # logger.warning("guessing encoding " + str(encoding))
        with io.open(full_path, "r", encoding=encoding["encoding"]) as infile:
            for line in infile:
                simplified_line = line.replace("'", '"')
                if simplified_line.strip().startswith("__version__"):
                    if '"' not in simplified_line:
                        pass
                        # logger.debug("Weird version string, no double quote : " + unicode((full_path, line, simplified_line)))
                    else:
                        if '"' in simplified_line:
                            parts = simplified_line.split('"')
                        else:
                            parts = simplified_line.split("'")
                        if len(parts) != 3:
                            # logger.debug("Weird string, more than 3 parts : " + unicode((full_path, line, simplified_line)))
                            continue
                        versions[full_path] = parts[1]
        return versions

    def validate_setup(self):  # type: () ->None
        """
        Don't put version constants into setup.py
        """
        setuppy = self.SRC + "setup.py"
        if not os.path.isfile(setuppy):
            return
        with io.open(setuppy, "r", encoding="utf8") as infile:
            for line in infile:
                # BUG: this doesn't stick to [metadata] & will touch other sections
                if line.strip().replace(" ", "").startswith("version="):
                    if not ("__version__" in line or "__init__" in line):
                        logger.error(line)
                        raise JiggleVersionException(
                            "Read the __version__.py or __init__.py don't add version in setup.py as constant"
                        )

    def version_to_write(self, found):  # type: (str) -> Version
        """
        Take 1st version string found.
        :param found: possible version string
        :return:
        """
        first = False
        if self.version is None:
            first = True
            try:
                self.current_version, self.version, self.schema = version_object_and_next(
                    found.strip(" ")
                )
            except:
                raise JiggleVersionException("Shouldn't throw here.")

        if first:
            logger.info(
                "Updating from version {0} to {1}".format(
                    unicode(self.version), unicode(self.version)
                )
            )
        return self.version
