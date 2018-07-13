# coding=utf-8
"""
Zero config alternative to bump version.

# NO REGEX. Sometimes I wan't a tool, not a superflous brain teaser.
# NO CONFIG. The tool shouldn't be more complex than writing a replacement.
# You want to support something other than semantic version? Write your own.
# NO FLOODING git with commits and tags.
# WORKS OUT OF BOX FOR MOST COMMON SCENARIO: automated build bumping. Edit the damn strings by
# hand if you need a major or minor. It is only 3 or so files.

----
Minor things:
Homogenize version based on 1st found.
Super strict parsing.

"""
import logging
import os.path
from typing import List, Optional

from semantic_version import Version

logger = logging.getLogger(__name__)

# contrive usage so black doesn't remove the import
_ = List, Optional


class JiggleVersion:
    """
    Because OOP.
    """

    def __init__(self, project, source, debug=False):  # type: (str, str, bool) ->None
        """
        Entry point
        """
        self.PROJECT = project
        self.SRC = source
        if not os.path.isdir(self.SRC + self.PROJECT):
            raise TypeError("Can't find proj dir, consider using absolute")
        self.DEBUG = False
        print("Will expect {0} at path {1}{0} ".format(self.PROJECT, self.SRC))

        self.version = None  # type: Optional[Version]
        self.create_configs = False

        # for example, do we create __init__.py which changes behavior
        self.create_all = False

    def jiggle_source_code(self):  # type: () ->None
        """
        Update python source files
        """
        files = ["/__init__.py", "/__version__.py"]

        for file_name in files:
            to_write = []
            filepath = self.SRC + self.PROJECT + file_name
            self.create_missing(file_name, filepath)

            if not os.path.isfile(filepath):
                raise TypeError("Missing file " + filepath)
            with open(filepath, "r") as infile:
                for line in infile:
                    if line.strip().startswith("__version__"):
                        if '"' not in line:
                            print(file_name, line)
                            raise TypeError("Please format your code with Black.")
                        else:
                            parts = line.split('"')
                            if len(parts) != 3:
                                raise TypeError(
                                    'Version must be of form __version__ = "1.1.1"  with no comments'
                                )
                            next_version = self.version_to_write(parts[1])
                        to_write.append('__version__ = "{0}"'.format(str(next_version)))
                    else:
                        to_write.append(line)

            if self.DEBUG:
                for line in to_write:
                    print(line, end="")

            with open(self.SRC + self.PROJECT + file_name, "w") as outfile:
                outfile.writelines(to_write)

    def create_missing(self, file_name, filepath):  # type: (str,str)->None
        if not os.path.isfile(filepath):
            if self.create_all and "__init__" in file_name:
                print("Creating " + str(filepath))
                self.create_init(filepath)
            if "__version__" in filepath:
                print("Creating " + str(filepath))
                self.create_version(filepath)

    def validate_setup(self):  # type: () ->None
        """
        Don't put version constants into setup.py
        """
        setuppy = self.SRC + "setup.py"
        if not os.path.isfile(setuppy):
            return
        with open(setuppy, "r") as infile:
            for line in infile:
                if line.strip().replace(" ", "").startswith("version="):
                    if not ("__version__" in line or "__init__" in line):
                        print(line)
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
            print(
                "Updating from version {0} to {1}".format(
                    str(self.version), str(next_version)
                )
            )
        return next_version

    def create_init(self, path):  # type: (str) -> None
        source = """# coding=utf-8
\"\"\"
Version
\"\"\"
__version__ = \"0.0.0\"
"""
        with open(path, "w") as outfile:
            outfile.write(source)

    def create_version(self, path):  # type: (str) -> None
        source = """# coding=utf-8
\"\"\"
Init
\"\"\"
__version__ = \"0.0.0\"
"""
        with open(path, "w") as outfile:
            outfile.write(source)

    def create_setup_cfg(self, path):  # type: (str) -> None
        source = """[metadata]
name = {0}
version=0.0.1 
""".format(
            self.PROJECT
        )
        with open(path, "w") as outfile:
            outfile.write(source)

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
                print("Creating " + str(filepath))
                self.create_setup_cfg(filepath)

            if os.path.isfile(filepath):
                with open(filepath, "r") as infile:
                    for line in infile:
                        if "version =" in line or "version=" in line:
                            parts = line.split("=")
                            if len(parts) != 2:
                                print(line)
                                print(parts)
                                raise TypeError("Must be of form version = 1.1.1")
                            next_version = self.version_to_write(parts[1])
                            to_write.append("version={0}\n".format(str(next_version)))
                        else:
                            to_write.append(line)

                if self.DEBUG:
                    for line in to_write:
                        print(line, end="")
                else:
                    with open(self.SRC + file_name, "w") as outfile:
                        outfile.writelines(to_write)


def go():  # type: () ->None
    """
    Entry point
    :return:
    """
    jiggler = JiggleVersion("", "")
    jiggler.jiggle_source_code()
    jiggler.jiggle_config_file()
