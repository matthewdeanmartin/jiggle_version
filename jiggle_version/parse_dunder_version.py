# coding=utf-8
"""
A whole file dedicated to parsing __version__ in all it's weird possible ways

1) Only acts on source, no file handling.

2) some functions for *by line*

3) some functions for *by file*

4) Handle quotes

5) Handle whitespace

6) Handle version as tuple
"""
import ast
import re

from jiggle_version.utils import JiggleVersionException
from typing import List, Optional, Any

_ = List, Optional, Any

def version_by_ast(line):  # type: (str) -> Optional[str]
    """
    Safer way to 'execute' python code to get a simple value
    :param line:
    :return:
    """
    # clean up line.

    if line.startswith("__version__"):
        return ast.parse(line).body[0].value.s

    return None

def find_version_by_regex(file_source):  # type: (str)->str

    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", file_source, re.M)
    if version_match:
        return version_match.group(1)
    raise JiggleVersionException("Unable to find version string.")


def find_version_by_string_lib(line):
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