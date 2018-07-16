# coding=utf-8
"""
Zero config alternative to bump version.

see README.md for philosophy & design decisions

"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import logging
import os.path
from typing import List, Optional, Dict, Any

from semantic_version import Version

from jiggle_version.file_makers import FileMaker
from jiggle_version.utils import merge_two_dicts, first_value_in_dict

try:
    import configparser
except ImportError:
    # Python 2.x fallback
    import ConfigParser as configparser

import sys

if sys.version_info.major == 3:
    unicode = str

logger = logging.getLogger(__name__)

# contrive usage so black doesn't remove the import
_ = List, Optional, Dict, Any


class JiggleVersion:
    """
    Because OOP.
    """

    def __init__(self, project, source, debug=False):  # type: (str, str, bool) ->None
        """
        Entry point
        """
        if not project:
            raise TypeError("Can't continue, no project name")

        if source is None:
            raise TypeError(
                'Can\'t continue, source directory is None, should be ""\ for current dir'
            )

        self.PROJECT = project
        self.SRC = source
        if not os.path.isdir(self.SRC + self.PROJECT):
            raise TypeError("Can't find proj dir, consider using absolute")
        self.DEBUG = False
        logger.info("Will expect {0} at path {1}{0} ".format(self.PROJECT, self.SRC))

        self.version = None  # type: Optional[Version]
        self.create_configs = False

        # for example, do we create __init__.py which changes behavior
        self.create_all = False
        self.file_maker = FileMaker(self.PROJECT)

        # the files we will attempt to manage
        self.project_root = os.path.join(self.SRC, self.PROJECT)

        self.source_files = [
            "__init__.py",  # required.
            "__version__.py",  # required.
            "_version.py",  # optional
        ]
        replacement = []
        for file in self.source_files:
            replacement.append(os.path.join(self.project_root, file))
        self.source_files = replacement

        self.config_files = [os.path.join(self.SRC, "setup.cfg")]

        self.text_files = [os.path.join(self.SRC, "version.txt")]

    def find_any_valid_verision(self):  # type: () -> str
        """
        Find version candidates, return first (or any, since they aren't ordered)

        Blow up if versions are not homogeneous
        :return:
        """
        versions = self.all_current_versions()
        return unicode(first_value_in_dict(versions))

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

        if not self.all_versions_equal_sem_ver(versions):
            logger.error("Found various versions, how can we rationally pick?")
            logger.error(unicode(versions))
            return False

        for key, version in versions.items():
            logger.debug("Found version : {0}".format(version))
            return True
        return False

    def all_current_versions(self):  # type: () ->Dict[str,str]
        """
        Track down all the versions & compile into one dictionary
        :return:
        """
        versions = {}  # type: Dict[str,str]
        for file in self.source_files:

            if not os.path.isfile(file):
                continue
            vers = self.find_dunder_version_in_file(file)

            versions = merge_two_dicts(versions, vers)
            more_vers = self.read_metadata()

            versions = merge_two_dicts(versions, more_vers)
            even_more_vers = self.read_text()

            versions = merge_two_dicts(versions, even_more_vers)
        copy = {}  # type: Dict[str,str]
        for key, version in versions.items():
            try:
                _ = Version(version)
                copy[key] = version
            except ValueError:
                logger.error("Invalid Semantic Version " + version)
                copy[key] = "Invalid Semantic Version : " + unicode(version)
        return copy

    def all_versions_equal_sem_ver(self, versions):  # type: (Dict[str,str]) -> bool
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
                    semver = Version(version)
                except ValueError:
                    logger.error("Invalid version at:")
                    logger.error(unicode((key, version)))
                    return False
                continue
            try:
                version_as_version = Version(version)
            except ValueError:
                return False
            if version_as_version != semver:
                return False
        return True

    def read_text(self):  # type: () ->Dict[str,str]
        """
        Get version out of ad-hoc version.txt
        :return:
        """
        if not os.path.isfile(self.text_files[0]):
            return {}
        with open(self.text_files[0], "r") as infile:
            text = infile.readline()
        return {self.text_files[0]: text.strip(" \n")}

    def read_metadata(self):  # type: () ->Dict[str,str]
        """
        Get version out of a .ini file (or .cfg)
        :return:
        """
        config = configparser.ConfigParser()
        config.read(self.config_files[0])
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
        with open(full_path, "r") as infile:
            for line in infile:
                if line.strip().startswith("__version__"):
                    if '"' not in line:
                        logger.error(unicode((full_path, line)))
                        raise TypeError(
                            "Couldn't find double quote (\") Please format your code, maybe with Black."
                        )
                    else:
                        parts = line.split('"')
                        if len(parts) != 3:
                            raise TypeError(
                                'Version must be of form __version__ = "1.1.1"  with no comments'
                            )
                        versions[full_path] = parts[1]
        return versions

    def jiggle_source_code(self):  # type: () ->None
        """
        Update python source files
        """

        for file_name in self.source_files:
            to_write = []
            self.create_missing(file_name, file_name)
            if not os.path.isfile(file_name):
                continue

            with open(file_name, "r") as infile:
                for line in infile:
                    if line.strip().startswith("__version__"):
                        if '"' not in line:
                            logger.error(unicode((file_name, line)))
                            raise TypeError(
                                "Couldn't find double quote (\") Please format your code, maybe with Black."
                            )
                        else:
                            parts = line.split('"')
                            if len(parts) != 3:
                                raise TypeError(
                                    'Version must be of form __version__ = "1.1.1"  with no comments'
                                )
                            next_version = self.version_to_write(parts[1])
                        to_write.append(
                            '__version__ = "{0}"'.format(unicode(next_version))
                        )
                    else:
                        to_write.append(line)

            with open(file_name, "w") as outfile:
                outfile.writelines(to_write)

    def create_missing(self, file_name, filepath):  # type: (str,str)->None
        """
        Check for file, decide if needed, call to create
        :param file_name:
        :param filepath:
        :return:
        """
        if not os.path.isfile(filepath):
            if self.create_all and "__init__" in file_name:
                logger.info("Creating " + unicode(filepath))
                self.file_maker.create_init(filepath)
                if not os.path.isfile(filepath):
                    raise TypeError("Missing file " + filepath)
            if "__version__" in filepath:
                logger.info("Creating " + unicode(filepath))
                self.file_maker.create_version(filepath)
                if not os.path.isfile(filepath):
                    raise TypeError("Missing file " + filepath)

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
                        raise TypeError(
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
            self.version = Version(found.strip(" "))
        next_version = self.version.next_patch()
        if first:
            logger.info(
                "Updating from version {0} to {1}".format(
                    unicode(self.version), unicode(next_version)
                )
            )
        return next_version

    def jiggle_config_file(self):  # type: () ->None
        """
        Update ini, cfg, conf
        """
        # setup.py related. setup.py itself should read __init__.py or __version__.py
        to_write = []
        other_files = ["/setup.cfg"]

        self.validate_setup()

        for file_name in other_files:
            filepath = self.SRC + file_name

            # only create setup.cfg if we have setup.py
            if (
                self.create_configs
                and not os.path.isfile(filepath)
                and os.path.isfile(self.SRC + "setup.py")
            ):
                logger.info("Creating " + unicode(filepath))
                self.file_maker.create_setup_cfg(filepath)

            if os.path.isfile(filepath):
                with io.open(filepath, "r", encoding="utf-8") as infile:
                    for line in infile:
                        if "version =" in line or "version=" in line:
                            parts = line.split("=")
                            if len(parts) != 2:
                                logger.error(line)
                                logger.error(parts)
                                logger.error("Must be of form version = 1.1.1")
                                print("Must be of form version = 1.1.1")
                                exit(-1)
                                return
                            next_version = self.version_to_write(parts[1])
                            to_write.append(
                                "version={0}\n".format(unicode(next_version))
                            )
                        else:
                            to_write.append(line)

                with io.open(self.SRC + file_name, "w", encoding="utf-8") as outfile:
                    outfile.writelines(to_write)

        version_txt = self.SRC + "/version.txt"
        if os.path.isfile(version_txt) or self.create_configs:
            with io.open(version_txt, "w", encoding="utf-8") as outfile:
                # BUG will blow up if not already set
                if self.version is None or self.version == "":
                    raise TypeError("Can't write version")
                # BUG: wrong version!
                next_version = self.version_to_write("0.0.0")
                outfile.writelines([unicode(next_version)])
                outfile.close()
