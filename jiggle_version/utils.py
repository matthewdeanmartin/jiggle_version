# coding=utf-8
"""
Non-domain specific methods I don't want cluttering up other files.
"""
from typing import List, Optional, Dict, Any

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
        if False:
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
