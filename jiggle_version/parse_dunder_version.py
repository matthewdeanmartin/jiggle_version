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
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import ast
import re
from typing import List, Optional, Any, Tuple

_ = List, Optional, Any, Tuple

version_tokens = [
    "__version__",  # canonical
    "__VERSION__",  # rare and wrong, but who am I to argue
    "VERSION",  # rare
    "version",
    "PACKAGE_VERSION",
]


def find_by_ast(line, version_token="__version__"):  # type: (str,str) -> Optional[str]
    """
    Safer way to 'execute' python code to get a simple value
    :param line:
    :return:
    """
    if not line:
        return ""
    # clean up line.
    simplified_line = simplify_line(line)

    if simplified_line.startswith(version_token):
        try:
            tree = ast.parse(simplified_line)
            if hasattr(tree.body[0].value, "s"):
                return tree.body[0].value.s
            if hasattr(tree.body[0].value, "elts"):
                version_parts = []
                for elt in tree.body[0].value.elts:
                    if hasattr(elt, "n"):
                        version_parts.append(str(elt.n))
                    else:
                        version_parts.append(str(elt.s))
                return ".".join(version_parts)
            if hasattr(tree.body[0].value, "n"):
                return str(tree.body[0].value.n)
            # print(tree)
        except Exception as ex:
            # raise
            return None

    return None


def simplify_line(line, keep_comma=False):  # type: (str, bool)->str
    """
    Change ' to "
    Remove tabs and spaces (assume no significant whitespace inside a version string!)
    """
    if not line:
        return ""
    if "#" in line:
        parts = line.split("#")
        simplified_line = parts[0]
    else:
        simplified_line = line

    simplified_line = (
        simplified_line.replace(" ", "")
        .replace("'", '"')
        .replace("\t", "")
        .replace("\n", "")
        .replace("'''", '"')  # version strings shouldn't be split across lines normally
        .replace('"""', '"')
    )
    if not keep_comma:
        simplified_line = simplified_line.strip(" ,")
    return simplified_line


def find_version_by_regex(
    file_source, version_token="__version__"
):  # type: (str,str)->Optional[str]
    """
    Regex for dunder version
    """
    if not file_source:
        return None
    version_match = re.search(
        r"^" + version_token + r" = ['\"]([^'\"]*)['\"]", file_source, re.M
    )
    if version_match:
        candidate = version_match.group(1)
        if candidate == "" or candidate == ".":  # yes, it will match to a .
            return None
        return candidate
    return None


def find_version_by_string_lib(
    line, version_token="__version__"
):  # type: (str,str)->Optional[str]
    """
    No regex parsing. Or at least, mostly, not regex.
    """
    if not line:
        return None
    simplified_line = simplify_line(line)
    version = None
    if simplified_line.strip().startswith(version_token):
        if '"' not in simplified_line:
            pass
            # logger.debug("Weird version string, no double quote : " + unicode((full_path, line, simplified_line)))
        else:
            if "=" in simplified_line:
                post_equals = simplified_line.split("=")[1]

                if post_equals.startswith('"'):
                    parts = post_equals.split('"')
                    version = parts[0]
                if not version:
                    version = None
    return version


def validate_string(version):  # type: (str) -> Optional[str]
    if not version:
        return None
    for char in version:
        if char in " \t()":
            return None
            # raise TypeError("Bad parse : " + version)
    return version


def find_in_line(line):  # type: (str)->Tuple[Optional[str],Optional[str]]
    """
    Use three strategies to parse version string
    :param line:
    :return:
    """
    if not line:
        return None, None
    for version_token in version_tokens:

        by_ast = find_by_ast(line, version_token)
        by_ast = validate_string(by_ast)
        if by_ast:
            return by_ast, version_token

        by_string_lib = find_version_by_string_lib(line, version_token)
        by_string_lib = validate_string(by_string_lib)
        if by_string_lib:
            return by_string_lib, version_token

        by_regex = find_version_by_regex(line, version_token)
        by_regex = validate_string(by_regex)
        if by_regex:
            return by_regex, version_token
    return None, None
