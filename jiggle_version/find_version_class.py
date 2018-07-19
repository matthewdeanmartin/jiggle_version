# coding=utf-8
"""
Just discover version and if possible, the schema.


TODO: __version_info__ = (3, 0, 0, 'a0')  -- sometime this is canonical. Shouldn't be first choice.
But not sys.version_info!

TODO: use_scm_version=True,  -- If this is in the file, then the user is signalling that no file will have a version string!

"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os.path
import sys
from typing import List, Optional, Dict, Any

from semantic_version import Version

import jiggle_version.parse_dunder_version as dunder_version
import jiggle_version.parse_kwarg_version as kwarg_version
from jiggle_version.file_inventory import FileInventory
from jiggle_version.file_opener import FileOpener
from jiggle_version.schema_guesser import version_object_and_next
from jiggle_version.utils import (
    merge_two_dicts,
    first_value_in_dict,
    JiggleVersionException,
    die, execute_get_text)

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


class FindVersion(object):
    """
    Because OOP.
    """

    def __init__(
        self, project, source, file_opener, debug=False
    ):  # type: (str, str, FileOpener, bool) ->None
        """
        Entry point
        """
        # if not project:
        #     raise JiggleVersionException("Can't continue, no project name")
        self.file_opener = file_opener

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

        self.setup_py_source = None

    def find_any_valid_version(self):  # type: () -> str
        """
        Find version candidates, return first (or any, since they aren't ordered)

        Blow up if versions are not homogeneous
        :return:
        """
        versions = self.all_current_versions()
        if not versions:
            raise JiggleVersionException("Have no versions to work with, failed to find any.")

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
            raise JiggleVersionException("Noooo! Must find a value" + unicode(versions))
        return unicode(first_value_in_dict(versions))

    def almost_the_same_version(
        self, version_list
    ):  # type: (List[str]) -> Optional[str]

        version_list = list(set(version_list))
        try:
            sem_ver_list = list(
                set([unicode(Version(x)) for x in version_list])
            )  # type: List[Version]
        except ValueError:
            # I hope htat was a bad semver
            return None

        # should be good sem vers from here
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
        for _, version in versions.items():
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

        for _ in versions:
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
            if vers:
                versions = merge_two_dicts(versions, vers)

        for finder in [self.read_metadata, self.read_text, self.read_setup_py]:
            more_vers = finder()
            if more_vers:
                versions = merge_two_dicts(versions, more_vers)

        bad_versions, good_versions = self.kick_out_bad_versions(versions)

        # get more versions here via risky routes
        if not good_versions:
            # desperate times, man...
            for folder in [self.file_inventory.project_root, self.file_inventory.src]:
                if not os.path.isdir(folder):
                    print(os.listdir("."))
                    continue

                if folder == "":
                    folder = "."
                for file in [x for x in os.listdir(folder) if x.endswith(".py")]:
                    # not going to do the extensionsless py files, too slow.
                    file_path = os.path.join(folder, file)
                    if not os.path.isfile(file_path):
                        continue
                    vers = self.find_dunder_version_in_file(file_path)
                    if vers:
                        maybe_good = merge_two_dicts(good_versions, vers)

                        more_bad_versions, good_versions = self.kick_out_bad_versions(maybe_good)

        if not good_versions:
            vers = self.execute_setup()
            if vers:
                try:
                    for key, value in vers.items():
                        v = version_object_and_next(value)
                except:
                    print(vers)

                maybe_good = merge_two_dicts(good_versions, vers)
                more_bad_versions, good_versions = self.kick_out_bad_versions(maybe_good)

        # more_bad_versions, good_versions = self.kick_out_bad_versions(versions)

        if bad_versions:
            print(unicode(bad_versions))
            logger.warning(unicode(bad_versions))
        return good_versions

    def kick_out_bad_versions(self, versions):
        copy = {}  # type: Dict[str,str]
        bad_versions = {}
        for key, version in versions.items():
            try:
                _ = version_object_and_next(version)
                copy[key] = version
            except:
                bad_versions[key] = version
        return bad_versions, copy

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
                    semver, _, __ = version_object_and_next(version)
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

        self.setup_py_source = self.file_opener.open_this(setup_py, "r").read()

        if "use_scm_version=True" in self.setup_py_source:
            die(-1, "setup.py has use_scm_version=True in it- this means we expect no file to have a version string. Nothing to change")
            return {}

        with self.file_opener.open_this(setup_py, "r") as infile:
            for line in infile:
                version = kwarg_version.find_in_line(line)
                if version:
                    found[setup_py] = version
                    continue
                version, version_token = dunder_version.find_in_line(line)
                if version:
                    found[setup_py] = version
                    continue

        # stress testing
        # if "version" in self.setup_py_source and not found:
        #     raise TypeError(self.setup_py_source)

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
            with self.file_opener.open_this(file, "r") as infile:
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

        with self.file_opener.open_this(full_path, "r") as infile:
            for line in infile:
                version, version_token = dunder_version.find_in_line(line)
                if version:
                    versions[full_path] = version
                version, version_token = dunder_version.find_in_line(line)
        return versions

    def validate_setup(self):  # type: () ->None
        """
        Don't put version constants into setup.py
        """
        setuppy = self.SRC + "setup.py"
        if not os.path.isfile(setuppy):
            return
        with self.file_opener.open_this(setuppy, "r") as infile:
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

    def execute_setup(self): # type: () -> Dict[str,str]
        """
        for really surprising things like a dict foo in setup(**foo)
        consider python3 setup.py --version
        :return:
        """

        ver = execute_get_text("python setup.py --version")
        if "UserWarning" in ver:
            # UserWarning- Ther version specified ... is an invalid...
            return {}

        if ver:
            string = unicode(ver).strip(" \n")
            if "\n" in string:
                string = string.split("\n")[0]

            return {"setup.py --version": string.strip(" \n")}
        else:
            return {}

