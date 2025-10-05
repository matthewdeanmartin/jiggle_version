"""
Non-domain specific methods I don't want cluttering up other files.
"""

from __future__ import annotations

import sys
from typing import Any, Dict, Optional


class JiggleVersionException(Exception):
    """
    Jiggle version can't continue. Different from a bug in jiggle version
    """


def first_value_in_dict(x: Dict[Any, Any]) -> Any:
    """
    foo[n] but for dictionaries
    :param x:
    :return:
    """
    for key, _ in x.items():
        return x[key]
    raise KeyError()


def merge_two_dicts(x: Dict[Any, Any], y: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Merge dictionaries. This is for python 2 compat.
    :param x:
    :param y:
    :return:
    """
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


def parse_source_to_dict(source: str) -> str:
    """
    Extract dict from source file
    :param source:
    :return:
    """
    line = source.replace("\n", "")
    line = line.split("package_dir")[1]
    fixed = ""
    for char in line:
        fixed += char
        if char == "}":
            break
    line = fixed
    simplified_line = line.strip(" ,").replace("'", '"')
    parts = simplified_line.split("=")
    dict_src = parts[1].strip(" \t")
    return dict_src
