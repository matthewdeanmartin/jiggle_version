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

PROJECT = "jiggle_version"
SRC = ""
files = ["/__init__.py", "/__version__.py"]
DEBUG = False

version = None
for file_name in files:
    to_write = []
    with open(SRC + PROJECT + file_name, "r") as infile:
        for line in infile:
            if line.strip().startswith("__version__"):
                if '"' not in line:
                    print(file_name)
                    print(line)
                    raise TypeError("Please format your code with Black.")
                else:
                    parts = line.split('"')
                    if len(parts) != 3:
                        raise TypeError("Version must be of form __version__ = \"1.1.1\"  with no comments")
                    if version is None:
                        version = Version(parts[1])
                        next_version = version.next_patch()
                to_write.append("__version__ = \"{0}\"".format(str(next_version)))
            else:
                to_write.append(line)

    if DEBUG:
        for line in to_write:
            print(line, end="")
    else:
        with open(SRC + PROJECT + file_name, 'w') as outfile:
            outfile.writelines(to_write)

# setup.py related. setup.py itself should read __init__.py or __version__.py
to_write = []
other_files = ["setup.cfg"]

for file_name in other_files:
    filepath = SRC + file_name
    if os.path.isfile(filepath):
        with open(filepath, "r") as infile:
            for line in infile:
                if "version =" in line or "version=" in line:
                    parts = line.split('=')
                    if len(parts) != 2:
                        print(line)
                        print(parts)
                        raise TypeError("Must be of form version = 1.1.1")
                    if version is None:
                        version = Version(parts[1].strip(" "))
                        next_version = version.next_patch()
                    to_write.append("version={0}\n".format(str(next_version)))
                else:
                    to_write.append(line)

        if DEBUG:
            for line in to_write:
                print(line, end="")
        else:
            with open(SRC + file_name, 'w') as outfile:
                outfile.writelines(to_write)
