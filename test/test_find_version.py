# coding=utf-8
"""
Tests
"""
from jiggle_version.find_version_by_package import pkg_resources_version

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

import os

from jiggle_version.commands import find_version
initial_pwd= os.getcwd()
here = os.path.abspath(os.path.dirname(__file__))
PROJECT = "sample_lib"
SRC = here + "/../sample_projects/"


def test_find_version():
    try:
        os.chdir(SRC)
        # what ev, who knows if these file even exist
        _ = find_version(PROJECT, "sample_src", force_init=True)
    finally:
        os.chdir(initial_pwd)



def test_find_version_by_package():
    _ = pkg_resources_version(PROJECT)