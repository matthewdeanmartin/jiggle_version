"""
Zero config alternative to bump version.

see README.md for philosophy & design decisions


TODO: detection problem- can detect, but can't update!
__version__ = '.'.join(__version_info__)

TODO: backwards version info
__version_info__ = (2, 21)
__version__ = '.'.join(str(x) for x in __version_info__)

# what system is this?
__version__ = (
    '.'.join(str(x) for x in __version_info__[:3]) +
    ''.join(__version_info__[3:] or [])
)

TODO: Ok, this would require executing
VersionInfo = collections.namedtuple('version_info', ('major', 'minor', 'micro'))
__version_info__ = VersionInfo(
    major=0,
    minor=1,
    micro=3,
)

__version_info__ = {
    'major': 0,
    'minor': 9,
    'micro': 5,
    'releaselevel': 'beta',
    'serial': 1
}

TODO: BUG
__version_info__ = (0, 1, 4)
__version__ = "0.1.8" # Jiggle Version Was Here



"""

import configparser
import logging
import os.path

import chardet
from semantic_version import Version

from jiggle_version.file_inventory import FileInventory
from jiggle_version.file_makers import FileMaker
from jiggle_version.file_opener import FileOpener
from jiggle_version.find_version_class import FindVersion
from jiggle_version.parse_python.is_this_okay import check
from jiggle_version.parse_version import parse_dunder_version as dunder_version
from jiggle_version.parse_version import parse_kwarg_version as kwarg_version
from jiggle_version.parse_version.schema_guesser import version_object_and_next
from jiggle_version.utils import JiggleVersionException, die

logger = logging.getLogger(__name__)


class JiggleVersion:
    """
    Coordinates code, writes versions
    """

    def __init__(
        self,
        project: str,
        source: str,
        file_opener: FileOpener,
        force_init: bool,
        signature: bool = False,
    ) -> None:
        """
        Entry point
        """
        self.force_init = force_init
        self.file_opener = file_opener
        if not project:
            logger.warning("No module name, can only update certain files.")
            # raise JiggleVersionException("Can't continue, no project name")

        if source is None:
            raise JiggleVersionException(
                "Can't continue, source directory is None, should be zero length string for current dir"
            )

        self.PROJECT = project
        self.SRC = source

        self.is_folder_project: bool = os.path.isdir(
            os.path.join(self.SRC, self.PROJECT)
        )
        self.is_file_project: bool = os.path.isfile(
            os.path.join(self.SRC, self.PROJECT) + ".py"
        )
        if not self.is_folder_project and not self.is_file_project:
            logger.warning(
                "Can't find module, typically a packages has a .py file or folder with module name : "
                + str(self.SRC + self.PROJECT)
                + " - can only update setup.py and text files."
            )

        self.DEBUG = False
        # logger.debug("Will expect {0} at path {1}{0} ".format(self.PROJECT, self.SRC))

        self.version_finder = FindVersion(
            self.PROJECT, self.SRC, self.file_opener, force_init=self.force_init
        )

        any_valid = self.version_finder.find_any_valid_version()

        try:
            self.current_version, self.version, self.schema = version_object_and_next(
                any_valid
            )
        except Exception as ex:
            # Can't find a version
            candidates = self.version_finder.all_current_versions()
            message = (
                str(ex)
                + " Can't parse this version, won't be able to bump anything. "
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
        self.version_finder = FindVersion(
            project, source, file_opener, force_init=self.force_init
        )
        self.file_inventory = FileInventory(project, source)

        # TODO: Make this off by default & option to turn on
        if signature:
            self.signature_txt = "  # Jiggle Version Was Here"
        else:
            self.signature_txt = ""

    def leading_whitespace(self, line: str) -> str:
        """
        For preserving indents
        :param line:
        :return:
        """
        string = ""
        for char in line:
            if char in " \t":
                string += char
                continue
            return string
        return string

    def jiggle_source_code(self) -> int:
        """
        Updates version of central package
        """
        changed = 0
        for file_name in self.file_inventory.source_files:
            to_write = []
            # self.create_missing(file_name, file_name)
            if not os.path.isfile(file_name):
                continue

            all_source = self.file_opener.read_this(file_name)
            if "__version_info__" in all_source:
                logger.warning("We have __version_info__ to sync up.")
                # raise TypeError()

            with self.file_opener.open_this(file_name, "r") as infile:
                for line in infile:
                    leading_white = self.leading_whitespace(line)
                    version, version_token = dunder_version.find_in_line(line)
                    if version:
                        simplified_line = dunder_version.simplify_line(
                            line, keep_comma=True
                        )
                        if simplified_line.strip(" \t\n").endswith(","):
                            comma = ","
                        else:
                            comma = ""

                        if simplified_line.strip(" \t\n").startswith(","):
                            start_comma = ","
                        else:
                            start_comma = ""

                        to_write.append(
                            f"{start_comma}{leading_white}{version_token} "
                            f'= "{str(self.version_to_write())}"{comma}{self.signature_txt}\n'
                        )
                    else:
                        to_write.append(line)

            with self.file_opener.open_this(file_name, "r") as file_handle:
                check(file_handle.read(), "".join(to_write))
            with open(file_name, "w", encoding="utf-8") as outfile:
                outfile.writelines(to_write)
                changed += 1
        return changed

    # This is just a bad idea. You can't do this without user input & __version__.py is a bad convention.
    # def create_missing(self, file_name, filepath):  # type: (str,str)->None
    #     """
    #     Check for file, decide if needed, call to create
    #     :param file_name:
    #     :param filepath:
    #     :return:
    #     """
    #     if not os.path.isfile(filepath):
    #         if self.create_all and "__init__" in file_name and not self.is_file_project:
    #             logger.info("Creating " + unicode(filepath))
    #             self.file_maker.create_init(filepath)
    #             if not os.path.isfile(filepath):
    #                 raise JiggleVersionException("Missing file " + filepath)
    #         if "__version__" in filepath and not self.is_file_project and self.PROJECT:
    #             logger.info("Creating " + unicode(filepath))
    #             self.file_maker.create_version(filepath)
    #             if not os.path.isfile(filepath):
    #                 raise JiggleVersionException("Missing file " + filepath)

    def jiggle_setup_py(self) -> int:
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

        with open(setup_py, "rb") as file_handle:
            encoding = chardet.detect(file_handle.read())
        # logger.warning("guessing encoding " + str(encoding))
        with self.file_opener.open_this(setup_py, "r") as infile:
            for line in infile:
                leading_white = self.leading_whitespace(line)

                simplified_line = dunder_version.simplify_line(line, keep_comma=True)

                # determine if we have a version=
                version = kwarg_version.find_in_line(line)
                # setup() function args
                if version:
                    if simplified_line.strip(" \t\n").startswith(","):
                        start_comma = ","
                    else:
                        start_comma = ""

                    comma = ""
                    if simplified_line.strip(" \t\n").endswith(","):
                        comma = ","
                    # could happen, say on last.
                    # if not comma and not start_comma:
                    #     print(simplified_line)
                    #     raise TypeError("$$$$$")
                    source = f'{leading_white}{start_comma}version = "{str(self.version_to_write())}"{comma}{self.signature_txt}\n'
                    need_rewrite = True
                    lines_to_write.append(source)
                    continue

                # code that isn't the setup() function args
                version, version_token = dunder_version.find_in_line(line)
                if version:
                    if simplified_line.strip(" \t\n").startswith(","):
                        start_comma = ","
                    else:
                        start_comma = ""

                    # the other simplify removes ","
                    if simplified_line.strip(" \t\n").endswith(","):
                        comma = ","
                    else:
                        comma = ""

                    lines_to_write.append(
                        f"{leading_white}{start_comma}{version_token} ="
                        f' "{str(self.version_to_write())}"{comma}{self.signature_txt}\n'
                    )
                    need_rewrite = True
                    continue

                lines_to_write.append(line)

        if need_rewrite:
            with self.file_opener.open_this(setup_py, "r") as file_handle_r:
                source_string = str(file_handle_r.read())
                check(source_string, "".join(lines_to_write))
            with open(setup_py, "w", encoding=encoding["encoding"]) as outfile:
                outfile.writelines(lines_to_write)
                outfile.close()
                changed += 1
        return changed

    def version_to_write(self) -> Version:
        """
        Should refactor to plain attribute
        """
        return self.version

    def jiggle_all(self) -> int:
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

    def jiggle_config_file(self) -> int:
        """
        Update ini, cfg, conf
        """
        changed = 0
        # setup.py related. setup.py itself should read __init__.py or __version__.py

        other_files = ["setup.cfg"]

        for file_name in other_files:
            filepath = os.path.join(self.SRC, file_name)

            # only create setup.cfg if we have setup.py
            if (
                self.create_configs
                and not os.path.isfile(filepath)
                and os.path.isfile("setup.py")
            ):
                logger.info("Creating " + str(filepath))
                self.file_maker.create_setup_cfg(filepath)

            if os.path.isfile(filepath):
                config = configparser.ConfigParser()
                config.read(filepath)
                try:
                    version = config["metadata"]["version"]
                except KeyError:
                    version = ""
                if version:
                    with open(filepath, "w", encoding="utf-8") as configfile:  # save
                        config["metadata"]["version"] = str(self.version_to_write())
                        config.write(configfile)
                        changed += 1
        return changed

    def jiggle_text_file(self) -> int:
        """
        Update ver strings in a non-python, ordinary text file in root of package (next to setup.py).
        """
        changed = 0

        files_to_update = []
        for version_txt in self.file_inventory.text_files:
            if os.path.isfile(version_txt):
                files_to_update.append(version_txt)

        if not files_to_update and self.create_configs:
            files_to_update = self.file_inventory.default_text_file

        for version_txt in files_to_update:
            if os.path.isfile(version_txt):
                with open(version_txt, "w", encoding="utf-8") as outfile:
                    if self.version is None or self.version == "":
                        raise JiggleVersionException("Can't write version")
                    outfile.writelines([str(self.version_to_write())])
                    outfile.close()
                    changed += 1
        return changed
