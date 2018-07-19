# coding=utf-8
"""
The kwarg version is found  in setup() of setup.py.

Depending on formatting, it may or may not look like:

version=...

Hardest case is positional, not that I've seen it in the wild yet.
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import ast
import re
from typing import List, Optional, Any, Tuple

from jiggle_version.parse_dunder_version import simplify_line, validate_string

_ = List, Optional, Any, Tuple


def find_by_ast(line):  # type: (str) -> Optional[str]
    """
    Safer way to 'execute' python code to get a simple value
    :param line:
    :return:
    """
    if not line:
        return ""
    # clean up line.
    simplified_line = simplify_line(line)

    if simplified_line.startswith("version="):
        try:
            tree = ast.parse(simplified_line)
            if hasattr(tree.body[0].value, "s"):
                return tree.body[0].value.s
            if hasattr(tree.body[0].value, "elts"):
                version_parts = []
                for elt in tree.body[0].value.elts:
                    version_parts.append(str(elt.n))
                return ".".join(version_parts)
            if hasattr(tree.body[0].value, "n"):
                return str(tree.body[0].value.n)
            # print(tree)
        except Exception as ex:
            # raise
            return None

    return None


def find_version_by_regex(file_source):  # type: (str)->Optional[str]
    """
    Regex for dunder version
    """
    if not file_source:
        return None
    version_match = re.search(r"^version=['\"]([^'\"]*)['\"]", file_source, re.M)
    if version_match:
        return version_match.group(1)
    return None


def find_version_by_string_lib(line):  # type: (str,str)->Optional[str]
    """
    No regex parsing. Or at least, mostly, not regex.
    """
    if not line:
        return None
    simplified_line = simplify_line(line)
    version = None
    if simplified_line.startswith("version="):
        if '"' not in simplified_line:
            pass
            # logger.debug("Weird version string, no double quote : " + unicode((full_path, line, simplified_line)))
        else:
            if "=" in simplified_line:
                post_equals= simplified_line.split("=")[0]
                if '"' in post_equals:
                    parts = post_equals.split('"')

                    if len(parts) != 3:
                        # logger.debug("Weird string, more than 3 parts : " + unicode((full_path, line, simplified_line)))
                        version = parts[0]
    return version


def find_in_line(line):  #
    if not line:
        return None

    by_ast = find_by_ast(line)
    validate_string(by_ast)
    if by_ast:
        return by_ast

    by_string_lib = find_version_by_string_lib(line)
    validate_string(by_string_lib)
    if by_string_lib:
        return by_string_lib

    by_regex = find_version_by_regex(line)
    validate_string(by_regex)
    if by_regex:
        return by_regex

    return None
