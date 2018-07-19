# coding=utf-8
"""
Is that a version string, a tuple or a int or float? 'Cause in the wild people use all of those.
"""
from jiggle_version.parse_dunder_version import find_in_line

def test_regression_scenarios():

    result, _ = find_in_line("VERSION = (1, 1, 0, 'rc1')")
    assert result == "1.1.0.rc1", result

    # passing
    result, _ = find_in_line("VERSION = (1, 0, 1)")
    assert result == "1.0.1", result
    result, _ = find_in_line("    version = re.search(r'^__version__\s*=\s*[\'\"]([^\'\"]*)[\'\"]',")
    assert result is None, result
    result, _ = find_in_line("version = re.search(r'^__version__\s*=\s*[")
    assert result is None, result



def test_common_scenarios():
    # single quotes
    result, _ = find_in_line("__version__ = '1.2.3'")
    assert result == "1.2.3", result

    # double quotes
    result, _ = find_in_line("__version__ = \"1.2.3\"")
    assert result == "1.2.3", result

    # whitespace
    result, _ = find_in_line(" __version__    =    \"1.2.3\"    ")
    assert result == "1.2.3", result

    # tabs
    result, _ = find_in_line(" \t __version__ \t   =    \"1.2.3\"  \t  ")
    assert result == "1.2.3", result

    # no whitespace
    result, _ = find_in_line("__version__=\"1.2.3\"")
    assert result == "1.2.3", result

    # comments
    result, _ = find_in_line("__version__=\"1.2.3\" # this is my version")
    assert result == "1.2.3", result

def test_that_is_a_tuple():
    # single quotes
    result, _ = find_in_line("__version__ = (1, 2, 3)")
    assert result == "1.2.3", result

    result, _ = find_in_line("__version__ = (1, 2,)")
    assert result == "1.2", result

    result, _ = find_in_line("__version__=(1, 2,)")
    assert result == "1.2", result

    result, _ = find_in_line("__version__=(1, 2,) # comments" )
    assert result == "1.2", result


def test_that_is_a_int_or_float():
    # single quotes
    result, _ = find_in_line("__version__ = 1.2")
    assert result == "1.2", result

    result, _ = find_in_line("__version__ = 1")
    assert result == "1", result

    result, _ = find_in_line("__version__=2")
    assert result == "2", result

    result, _ = find_in_line("__version__=2 # comments")
    assert result == "2", result

    result, _ = find_in_line("__version__=2 # __version__ = 3")
    assert result == "2", result