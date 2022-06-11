"""
Just discover version and if possible, the schema.


TODO: __version_info__ = (3, 0, 0, 'a0')  -- sometime this is canonical. Shouldn't be first choice.
But not sys.version_info!

TODO: use_scm_version=True,  -- If this is in the file, then the user is signalling that no file will have a
version string!

"""
import ast
import configparser
import logging
import os.path
import sys
from typing import Dict, List, Optional, Tuple, Union, cast

import parver
from semantic_version import Version

from jiggle_version.file_inventory import FileInventory
from jiggle_version.file_opener import FileOpener
from jiggle_version.parse_version import parse_dunder_version as dunder_version
from jiggle_version.parse_version import parse_kwarg_version as kwarg_version
from jiggle_version.parse_version.schema_guesser import version_object_and_next
from jiggle_version.utils import (
    JiggleVersionException,
    die,
    first_value_in_dict,
    ifnull,
    merge_two_dicts,
)
from versio import version as versio_version

logger = logging.getLogger(__name__)


class FindVersion:
    """
    Because OOP.
    """

    def __init__(
        self, project: str, source: str, file_opener: FileOpener, force_init: bool
    ) -> None:
        """
        Entry point
        """
        self.force_init = force_init
        # fuzzy concept of being secure, minimal package, "linted'
        self.strict = True

        # logger.debug("Will expect {0} at path {1}{0} ".format(self.PROJECT, self.SRC))

        self.version: Optional[Version] = None
        self.create_configs = False

        # for example, do we create __init__.py which changes behavior
        self.create_all = False
        self.setup_py_source = None
        self.schema: Optional[str] = None

        # if not project:
        #     raise JiggleVersionException("Can't continue, no project name")
        self.file_opener = file_opener

        if source is None:
            raise JiggleVersionException(
                'Can\'t continue, source directory is None, should be "" for current dir'
            )
        self.current_version: Optional[
            Union[Version, parver.Version, versio_version.Version]
        ] = None
        self.PROJECT = project
        self.SRC = source

        if self.PROJECT is None:
            self.is_folder_project: bool = False
        else:
            candidate_folder = os.path.join(self.SRC, self.PROJECT)
            self.is_folder_project = os.path.isdir(candidate_folder)

        if self.PROJECT is None:
            self.is_file_project: bool = False
        else:
            self.is_file_project = os.path.isfile(
                os.path.join(self.SRC, self.PROJECT) + ".py"
            )

        if not self.is_folder_project and not self.is_file_project:
            self.is_setup_only_project = os.path.isfile(
                os.path.join(self.SRC, "setup.py")
            )
        else:
            self.is_setup_only_project = False

        if not any(
            [self.is_setup_only_project, self.is_file_project, self.is_folder_project]
        ):
            print(
                "Can't find module nor setup.py, typically a packages has a .py file or folder with module name : "
                + str(self.SRC + self.PROJECT)
                + " - what should be done? Update the version.txt?"
            )
            # exits really mess with unit test runners
            sys.exit(-1)

        self.file_inventory = FileInventory(self.PROJECT, self.SRC)

    def find_any_valid_version(self) -> str:
        """
        Find version candidates, return first (or any, since they aren't ordered)

        Blow up if versions are not homogeneous
        :return:
        """
        versions = self.all_current_versions()

        if not versions and not self.force_init:
            raise JiggleVersionException(
                "Have no versions to work with, failed to find any. Include --init to start out at 0.1.0"
            )

        if not versions and self.force_init:
            versions = {"force_init": "0.1.0"}

        if len(versions) > 1:
            if not self.all_versions_equal(versions):
                if not self.all_versions_equal(versions):
                    almost_same = self.almost_the_same_version(
                        cast(List[str], versions.values())
                    )
                    if almost_same:
                        # TODO: disable with strict option
                        logger.warning(
                            "Version very by a patch level, will use greater."
                        )
                        return str(almost_same)

        if not versions.keys():
            raise JiggleVersionException("Noooo! Must find a value" + str(versions))
        return str(first_value_in_dict(versions))

    def almost_the_same_version(self, version_list: List[str]) -> Optional[str]:
        """
        Are these versions different by a .1 patch level? This is crazy common in the wild.
        :param version_list:
        :return:
        """

        version_list = list(set(version_list))
        try:
            sem_ver_list: List[Version] = list({str(Version(x)) for x in version_list})
        except ValueError:
            # I hope htat was a bad semver
            return None

        # should be good sem vers from here
        if len(sem_ver_list) == 2:
            if (
                sem_ver_list[0] == str(Version(sem_ver_list[1]).next_patch())
                or str(Version(sem_ver_list[0]).next_patch()) == sem_ver_list[1]
            ):
                if sem_ver_list[0] > sem_ver_list[1]:
                    return str(sem_ver_list[0])
                return str(sem_ver_list[1])
        return None

    def validate_current_versions(self) -> bool:
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
            if self.almost_the_same_version(cast(List[str], versions.values())):
                # TODO: disable with strict option
                logger.warning("Version very by a patch level, will use greater.")
                return True
            logger.error("Found various versions, how can we rationally pick?")
            logger.error(str(versions))
            return False

        for _ in versions:
            return True
        return False

    def version_by_eval(self, file_path: str) -> Dict[str, str]:
        """
        Version by ast evaluation. Didn't find more versions that existing methods
        :param file_path:
        :return:
        """
        source = self.file_opener.read_this(file_path)
        sb = "{"
        for line in source.split("\n"):
            if "=" in line:
                parts = line.split("=")
                sb += "'" + parts[0] + "':" + parts[1]
        sb += "}"
        if sb == "{}":
            return {}
        # noinspection PyBroadException
        try:
            thing = ast.literal_eval(sb)
        except:
            return {}
        for version_token in dunder_version.version_tokens:
            if version_token in thing:
                return {"literal_eval": thing[version_token]}
        return {}

    def version_by_import(self, module_name: str) -> Dict[str, str]:
        """
        This is slow & if running against random code, dangerous

        Sometimes apps call exit() in import if conditions not met.
        :param module_name:
        :return:
        """
        if not module_name:
            return {}
        try:
            module = __import__(module_name)
        except ModuleNotFoundError:
            # hypothetical module would have to be on python path or execution folder, I think.
            return {}
        except FileNotFoundError:
            return {}

        if hasattr(module, "__version__"):
            version = module.__version__
            return {"module import": version}
        return {}

    def all_current_versions(self) -> Dict[str, str]:
        """
        Track down all the versions & compile into one dictionary
        :return:
        """
        if self.PROJECT is None:
            raise TypeError("self.PROJECT missing, can't continue")

        versions: Dict[str, str] = {}
        files_to_check = self.file_inventory.source_files
        files_to_check.append(self.PROJECT + ".py")  # is this the 'central' module?
        for file in self.file_inventory.source_files:

            if not os.path.isfile(file):
                continue
            vers: Optional[Dict[str, str]] = self.find_dunder_version_in_file(file)
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

                        _, good_versions = self.kick_out_bad_versions(maybe_good)

        if not good_versions:
            vers = ""  # self.execute_setup()
            if vers:
                # noinspection PyBroadException
                try:
                    for value in vers.values():
                        _ = version_object_and_next(value)
                except:
                    print(vers)

                maybe_good = merge_two_dicts(good_versions, vers)
                _, good_versions = self.kick_out_bad_versions(maybe_good)

        # more_bad_versions, good_versions = self.kick_out_bad_versions(versions)
        if not good_versions:
            vers = self.version_by_import(self.PROJECT)
            maybe_good = merge_two_dicts(good_versions, vers)
            _, good_versions = self.kick_out_bad_versions(maybe_good)

        # no new versions found!
        # for file in self.file_inventory.source_files:
        #
        #     if not os.path.isfile(file):
        #         continue
        #     vers = self.version_by_eval(file)
        #     maybe_good = merge_two_dicts(good_versions, vers)
        #     more_bad_versions, good_versions = self.kick_out_bad_versions(
        #         maybe_good
        #     )

        # BUG: this ignores a bunch of bad versions because I would have had to merged dict
        if bad_versions:
            print(str(bad_versions))
            logger.warning(str(bad_versions))
        return good_versions

    def kick_out_bad_versions(
        self, versions: Dict[str, str]
    ) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Remove invalid versions from list of possible
        """
        copy: Dict[str, str] = {}
        bad_versions = {}
        for key, version in versions.items():
            # noinspection PyBroadException
            try:
                _ = version_object_and_next(version)
                copy[key] = version
            except:
                bad_versions[key] = version
        return bad_versions, copy

    def all_versions_equal(self, versions: Dict[str, str]) -> bool:
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
                    logger.error("Invalid version at:" + str((key, version)))
                    return False
                continue
            # noinspection PyBroadException
            try:
                version_as_version, _, __ = version_object_and_next(version)
            except:
                return False
            if version_as_version != semver:
                return False
        return True

    def read_setup_py(self) -> Dict[str, str]:
        """
        Extract from setup.py's setup() arg list.
        :return:
        """
        found: Dict[str, str] = {}
        setup_py = os.path.join("setup.py")

        if not os.path.isfile(setup_py):
            if self.strict:
                logger.debug(str(os.getcwd()))
                logger.debug(str(os.listdir(os.getcwd())))
                # return ""
                # raise JiggleVersionException(
                #     "Can't find setup.py : {0}, path :{1}".format(setup_py, self.SRC)
                # )
                return found
            return found

        with self.file_opener.open_this(setup_py, "r") as file_handle:
            self.setup_py_source = file_handle.read()

        if "use_scm_version=True" in ifnull(self.setup_py_source, ""):
            die(
                -1,
                "setup.py has use_scm_version=True in it- this means we expect no file to have a version string. "
                "Nothing to change",
            )
            return {}

        with self.file_opener.open_this(setup_py, "r") as infile:
            for line in infile:
                version = kwarg_version.find_in_line(line)
                if version:
                    found[setup_py] = version
                    continue
                version, _ = dunder_version.find_in_line(line)
                if version:
                    found[setup_py] = version
                    continue

        # stress testing
        # if "version" in self.setup_py_source and not found:
        #     raise TypeError(self.setup_py_source)

        return found

    def read_text(self) -> Dict[str, str]:
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

    def read_metadata(self) -> Dict[str, str]:
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

    def find_dunder_version_in_file(self, full_path: str) -> Dict[str, str]:
        """
        Find __version__ in a source file
        """
        versions = {}

        with self.file_opener.open_this(full_path, "r") as infile:
            for line in infile:
                version, _ = dunder_version.find_in_line(line)
                if version:
                    versions[full_path] = version
                version, _ = dunder_version.find_in_line(line)
        return versions

    def version_to_write(self, found: str) -> Version:
        """
        Take 1st version string found.
        :param found: possible version string
        :return:
        """
        first = False
        if self.version is None:
            first = True
            try:
                (
                    self.current_version,
                    self.version,
                    self.schema,
                ) = version_object_and_next(found.strip(" "))
            except:
                raise JiggleVersionException("Shouldn't throw here.")

        if first:
            logger.info(
                f"Updating from version {str(self.version)} to {str(self.version)}"
            )
        return self.version

    # def execute_setup(self) -> Optional[Dict[str, str]]:
    #     """
    #     for really surprising things like a dict foo in setup(**foo)
    #     consider python3 setup.py --version
    #     """
    #
    #     ver = execute_get_text("python setup.py --version")
    #     if not ver:
    #         return None
    #
    #     if "UserWarning" in ver:
    #         logger.warning("python setup.py --version won't parse, got :" + str(ver))
    #         # UserWarning- Ther version specified ... is an invalid...
    #         return {}
    #
    #     if ver:
    #         string = str(ver).strip(" \n")
    #         if "\n" in string:
    #             string = string.split("\n")[0]
    #
    #         return {"setup.py --version": string.strip(" \n")}
    #     return {}
