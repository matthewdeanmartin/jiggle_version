"""
Stupider version of jiggle version that jiggle_version depends on.

I didn't want a weird circular dependency.
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
import os.path

from semantic_version import Version

PROJECT = "jiggle_version"
SRC = ""
files = ["/__init__.py", "/_version.py"]
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
                        raise TypeError(
                            'Version must be of form __version__ = "1.1.1"  with no comments'
                        )
                    if version is None:
                        version = Version(parts[1])
                        next_version = version.next_patch()
                to_write.append('__version__ = "{0}"'.format(str(next_version)))
            else:
                to_write.append(line)

    if DEBUG:
        for line in to_write:
            print(line, end="")
    else:
        with open(SRC + PROJECT + file_name, "w") as outfile:
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
                    parts = line.split("=")
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
            with open(SRC + file_name, "w") as outfile:
                outfile.writelines(to_write)
