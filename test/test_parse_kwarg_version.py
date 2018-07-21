# coding=utf-8
"""
Is that a version string, a tuple or a int or float? 'Cause in the wild people use all of those.
"""
from jiggle_version.parse_kwarg_version import find_in_line
# TODO: enable test
# def test_oneliner():
#
#     result = find_in_line("setup(version = \"1.2.4\")")
#     assert result == "1.2.4", result
#
def test_regression_scenarios():
    result = find_in_line(", version='1.2.0'")
    assert result == "1.2.0", result

    result = find_in_line("version = \"0.0.1a1.dev0\", # Jiggle Version Was Here")
    assert result == "0.0.1a1.dev0", result
    # result = find_in_line("VERSION = (1, 0, 1),")
    # assert result == "1.0.1", result
    result = find_in_line("    version = re.search(r'^__version__\s*=\s*[\'\"]([^\'\"]*)[\'\"]',")
    assert result is None, result
    result = find_in_line("version = re.search(r'^__version__\s*=\s*[")
    assert result is None, result


def test_common_scenarios():
    # single quotes
    result = find_in_line("version = '1.2.3'")
    assert result == "1.2.3", result

    # double quotes
    result= find_in_line("version = \"1.2.3\"")
    assert result == "1.2.3", result

    # whitespace
    result= find_in_line(" version    =    \"1.2.3\"    ")
    assert result == "1.2.3", result

    # tabs
    result= find_in_line(" \t version \t   =    \"1.2.3\"  \t  ")
    assert result == "1.2.3", result

    # no whitespace
    result = find_in_line("version=\"1.2.3\"")
    assert result == "1.2.3", result

    # comments
    result= find_in_line("version=\"1.2.3\" # this is my version")
    assert result == "1.2.3", result

def test_that_is_a_tuple():
    # single quotes
    result= find_in_line("version = (1, 2, 3)")
    assert result == "1.2.3", result

    result = find_in_line("version = (1, 2,)")
    assert result == "1.2", result

    result = find_in_line("version=(1, 2,)")
    assert result == "1.2", result

    result= find_in_line("version=(1, 2,) # comments" )
    assert result == "1.2", result


def test_that_is_a_int_or_float():
    # single quotes
    result = find_in_line("version = 1.2")
    assert result == "1.2", result

    result = find_in_line("version = 1")
    assert result == "1", result

    result= find_in_line("version=2")
    assert result == "2", result

    result = find_in_line("version=2 # comments")
    assert result == "2", result

    result= find_in_line("version=2 # version = 3")
    assert result == "2", result