# coding=utf-8
"""
Non-domain specific methods I don't want cluttering up other files.
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from typing import List, Optional, Dict, Any
import subprocess


# contrive usage so black doesn't remove the import
_ = List, Optional, Dict, Any


class JiggleVersionException(Exception):
    """
    Jiggle version can't continue. Different from a bug in jiggle version
    """


def die(code, why):  # type: (int,str)->None
    """
    In release, exit process. In development, throw with useful message.
    :param code:
    :param why:
    :return:
    """
    if code != 0:
        # Development
        if "Have no versions to work with" not in why:
            raise JiggleVersionException("Can't continue: " + why)
        else:
            # prod
            exit(code)


def first_value_in_dict(x):  # type: (Dict[Any, Any]) -> Any
    """
    foo[n] but for dictionaries
    :param x:
    :return:
    """
    for key, _ in x.items():
        return x[key]
    raise KeyError()


def merge_two_dicts(x, y):  # type: (Dict[Any, Any], Dict[Any, Any]) -> Dict[Any, Any]
    """
    Merge dictionaries. This is for python 2 compat.
    :param x:
    :param y:
    :return:
    """
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


def execute_get_text(command, raise_errors=False):  # type: (str) -> str
    """
    Execute a shell commmand
    :param command:
    :return:
    """
    try:
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        # print(result.decode())
    except subprocess.CalledProcessError as err:
        if raise_errors:
            raise
        return ""
    if result:
        return result.decode("utf-8")
    else:
        return ""
