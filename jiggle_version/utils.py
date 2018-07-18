# coding=utf-8
"""
Non-domain specific methods I don't want cluttering up other files.
"""
from typing import List, Optional, Dict, Any

# contrive usage so black doesn't remove the import
_ = List, Optional, Dict, Any

class JiggleVersionException(Exception):
    pass

def die(code, why):
    if code != 0:
        # Development
        raise JiggleVersionException("Can't continue: " + why)
        # prod
        # exit(code)

def first_value_in_dict(x):  # type: (Dict[Any, Any]) -> Any
    """
    foo[n] but for dictionaries
    :param x:
    :return:
    """
    for key, value in x.items():
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
