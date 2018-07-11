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
import os.path

from semantic_version import Version


class JiggleVersion:
    """
    Because OOP.
    """

    def __init__(self):
        # type: () ->None
        """
        Entry point
        """
        self.PROJECT = "sample_lib"
        self.SRC = "../"
        if not os.path.isdir(self.SRC + self.PROJECT):
            self.SRC = "../../"
            if not os.path.isdir(self.SRC + self.PROJECT):
                self.SRC = ""
                if not os.path.isdir(self.SRC + self.PROJECT):
                    raise TypeError("Can't find proj dir")
        print("expecting " + self.SRC + self.PROJECT)
        self.DEBUG = False
        self.version = None  # type: Optional[Version]

    def jiggle_source_code(self):
        # type: () ->None
        """
        Update python source files
        """
        files = ["/__init__.py", "/__version__.py"]

        for file_name in files:
            to_write = []
            with open(self.SRC + self.PROJECT + file_name, "r") as infile:
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
            else:
                with open(self.SRC + self.PROJECT + file_name, "w") as outfile:
                    outfile.writelines(to_write)

    def validate_setup(self):
        # type: () ->None
        """
        Don't put version constants into setup.py
        """
        with open(self.SRC + "setup.py", "r") as infile:
            for line in infile:
                if line.strip().replace(" ", "").startswith("version="):
                    if not ("__version__" in line or "__init__" in line):
                        print(line)
                        raise TypeError(
                            "Read the __version__.py or __init__.py don't add version in setup.py as constant"
                        )

    def version_to_write(self, found):
        # type: (str) -> Version
        """
        Take 1st version string found.
        :param found: possible version string
        :return:
        """
        if self.version is None:
            self.version = Version(found.strip(" "))
        next_version = self.version.next_patch()
        return next_version

    def jiggle_config_file(self):
        # type: () ->None
        """
        Update ini, cfg, conf
        """
        # setup.py related. setup.py itself should read __init__.py or __version__.py
        to_write = []
        other_files = ["/setup.cfg"]

        self.validate_setup()

        for file_name in other_files:
            filepath = self.SRC + file_name
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


def go():
    # type: () ->None
    """
    Entry point
    :return:
    """
    jiggler = JiggleVersion()
    jiggler.jiggle_source_code()
    jiggler.jiggle_config_file()


if __name__ == "__main__":
    pass
