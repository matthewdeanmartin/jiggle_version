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

import chardet
from semantic_version import Version

from jiggle_version.file_inventory import FileInventory
from jiggle_version.file_makers import FileMaker
from jiggle_version.find_version_class import FindVersion
from jiggle_version.is_this_okay import check
from jiggle_version.schema_guesser import version_object_and_next
from jiggle_version.utils import die, JiggleVersionException

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


class JiggleVersion(object):
    """
    Coordinates code, writes versions
    """

    def __init__(self, project, source, debug=False):  # type: (str, str, bool) ->None
        """
        Entry point
        """
        if not project:
            logger.warning("No module name, can only update certain files.")
            # raise JiggleVersionException("Can't continue, no project name")

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

        self.DEBUG = False
        # logger.debug("Will expect {0} at path {1}{0} ".format(self.PROJECT, self.SRC))

        self.version_finder = FindVersion(self.PROJECT, self.SRC)
        try:
            self.current_version, self.version, self.schema = version_object_and_next(
                self.version_finder.find_any_valid_version()
            )
        except Exception as ex:
            # Can't find a version
            candidates = self.version_finder.all_current_versions()
            message = (
                unicode(ex)
                + " Can't find a recognizable version, won't be able to bump anything. "
                + str(candidates)
            )
            logger.error(message)
            die(-1, message)
            return
            # self.current_version , self.version = None, None

        self.create_configs = False

        # for example, do we create __init__.py which changes behavior
        self.create_all = False
        self.file_maker = FileMaker(self.PROJECT)
        self.version_finder = FindVersion(project, source, debug)
        self.file_inventory = FileInventory(project, source)

    def leading_whitespace(self, line):
        string = ""
        for char in line:
            if char in " \t":
                string += char
                continue
            else:
                return string
        return string

    def jiggle_source_code(self):  # type: () ->int
        """
        Update python source files
        """
        changed = 0
        for file_name in self.file_inventory.source_files:
            to_write = []
            self.create_missing(file_name, file_name)
            if not os.path.isfile(file_name):
                continue

            with io.open(file_name, "r", encoding="utf-8") as infile:
                for line in infile:
                    leading_white = self.leading_whitespace(line)
                    ends_with_comma = line.strip(" \t\n").endswith(",")
                    simplified_line = (
                        line.strip()
                        .replace(" ", "")
                        .replace("'", '"')
                        .replace("\n", "")
                    )
                    found = False
                    for version_token in ["__version__", "VERSION", "version"]:
                        if simplified_line.startswith(version_token + '="'):
                            if '"' not in simplified_line:
                                pass
                                # logger.warn("weird source,no double quote " + unicode((file_name, line, simplified_line)))
                                # raise JiggleVersionException(
                                #     "Couldn't find double quote (\") Please format your code, maybe with Black."
                                # )
                                # to_write.append(line)
                            else:
                                parts = simplified_line.split('"')
                                if len(parts) != 3:
                                    # logger.warn(
                                    #     "weird source, not 3 parts " + unicode((file_name, line, simplified_line)))
                                    continue
                                if parts[2].strip(" \t") not in [",", ""]:
                                    raise JiggleVersionException(
                                        "Can't parse this yet (stuff after version) "
                                        + line
                                    )
                                found = True
                                # preserve leading whitespace
                                comma = ""
                                if ends_with_comma:
                                    comma = ","
                                to_write.append(
                                    '{0}{1} = "{2}"{3}\n'.format(
                                        leading_white,
                                        version_token,
                                        unicode(self.version_to_write()),
                                        comma,
                                    )
                                )
                    if not found:
                        to_write.append(line)

            check(io.open(file_name, "r", encoding="utf-8").read(), "".join(to_write))
            with open(file_name, "w") as outfile:
                outfile.writelines(to_write)
                changed += 1
        return changed

    def create_missing(self, file_name, filepath):  # type: (str,str)->None
        """
        Check for file, decide if needed, call to create
        :param file_name:
        :param filepath:
        :return:
        """
        if not os.path.isfile(filepath):
            if self.create_all and "__init__" in file_name and not self.is_file_project:
                logger.info("Creating " + unicode(filepath))
                self.file_maker.create_init(filepath)
                if not os.path.isfile(filepath):
                    raise JiggleVersionException("Missing file " + filepath)
            if "__version__" in filepath and not self.is_file_project and self.PROJECT:
                logger.info("Creating " + unicode(filepath))
                self.file_maker.create_version(filepath)
                if not os.path.isfile(filepath):
                    raise JiggleVersionException("Missing file " + filepath)

    def validate_setup(self):  # type: () ->None
        """
        Okay, lots of people only have their version in setup.py as a constant.
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

    def jiggle_setup_py(self):  # type: () -> int
        """
        Edit a version = "1.2.3" or version="1.2.3",
        :return:
        """
        changed = 0
        setup_py = os.path.join(self.SRC, "setup.py")
        if not os.path.isfile(setup_py):
            return changed
        lines_to_write = []
        need_rewrite = False

        encoding = chardet.detect(io.open(setup_py, "rb").read())
        # logger.warning("guessing encoding " + str(encoding))
        with io.open(setup_py, "r", encoding=encoding["encoding"]) as infile:
            for line in infile:
                leading_white = self.leading_whitespace(line)
                simplified_line = (
                    line.replace(" ", "").replace("'", '"').replace("\t", "")
                )
                if 'version="' in simplified_line:
                    if len([x for x in simplified_line if x == "="]) > 1:
                        raise JiggleVersionException(
                            "Don't have a way of parsing this yet. " + line
                        )
                    source = leading_white + 'version = "{0}"'.format(
                        unicode(self.version_to_write())
                    )
                    if "," in simplified_line:
                        source += ","

                    need_rewrite = True
                    lines_to_write.append(source + "\n")
                elif simplified_line.startswith('__version__="'):
                    if '"' not in simplified_line:
                        # logger.warn("weird source,no double quote " + unicode((setup_py, line, simplified_line)))
                        # raise JiggleVersionException(
                        #     "Couldn't find double quote (\") Please format your code, maybe with Black."
                        # )
                        lines_to_write.append(line)
                    else:
                        parts = simplified_line.split('"')
                        if len(parts) != 3:
                            # logger.warn(
                            #     "weird source, not 3 parts " + unicode((setup_py, line, simplified_line)))
                            continue
                        lines_to_write.append(
                            '__version__ = "{0}"\n'.format(
                                unicode(self.version_to_write())
                            )
                        )
                        need_rewrite = True
                else:
                    lines_to_write.append(line)

        if need_rewrite:
            check(
                io.open(setup_py, "r", encoding=encoding["encoding"]).read(),
                "".join(lines_to_write),
            )
            with io.open(setup_py, "w", encoding=encoding["encoding"]) as outfile:

                outfile.writelines(lines_to_write)
                outfile.close()
                changed += 1
        return changed

    def version_to_write(self):  # type: () -> Version
        """
        :return:
        """
        return self.version

    def jiggle_all(self):  # type: () -> int
        """
        All possible files
        :return:
        """
        changed = 0
        changed += self.jiggle_text_file()
        changed += self.jiggle_source_code()
        changed += self.jiggle_config_file()
        changed += self.jiggle_setup_py()
        # assert changed > 0, "Failed to change anything."
        return changed

    def jiggle_config_file(self):  # type: () ->int
        """
        Update ini, cfg, conf
        """
        changed = 0
        # setup.py related. setup.py itself should read __init__.py or __version__.py
        to_write = []
        other_files = ["setup.cfg"]

        # Okay, lets just update if found
        # self.validate_setup()

        for file_name in other_files:
            filepath = os.path.join(self.SRC, file_name)

            # only create setup.cfg if we have setup.py
            if (
                self.create_configs
                and not os.path.isfile(filepath)
                and os.path.isfile("setup.py")
            ):
                logger.info("Creating " + unicode(filepath))
                self.file_maker.create_setup_cfg(filepath)

            if os.path.isfile(filepath):
                need_rewrite = False
                with io.open(filepath, "r", encoding="utf-8") as infile:
                    for line in infile:
                        if "version =" in line or "version=" in line:
                            parts = line.split("=")
                            if len(parts) != 2:
                                logger.error(line)
                                logger.error(parts)
                                logger.error("Must be of form version = 1.1.1")
                                print("Must be of form version = 1.1.1")
                                die(-1, "Can't parse " + str(line))
                                return changed

                            to_write.append(
                                "version={0}\n".format(unicode(self.version_to_write()))
                            )
                            need_rewrite = True
                        else:
                            to_write.append(line)
                if need_rewrite:
                    with io.open(
                        self.SRC + file_name, "w", encoding="utf-8"
                    ) as outfile:
                        outfile.writelines(to_write)
                    changed += 1
        return changed

    def jiggle_text_file(self):  # type: () -> int
        changed = 0

        for version_txt in self.file_inventory.text_files:
            if os.path.isfile(version_txt) or self.create_configs:
                with io.open(version_txt, "w", encoding="utf-8") as outfile:
                    if self.version is None or self.version == "":
                        raise JiggleVersionException("Can't write version")
                    outfile.writelines([unicode(self.version_to_write())])
                    outfile.close()
                    changed += 1
        return changed
