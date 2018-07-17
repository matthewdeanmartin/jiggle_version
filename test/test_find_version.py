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

here = os.path.abspath(os.path.dirname(__file__))
PROJECT = "sample_lib"
SRC = here + "/../sample_projects/sample_src/"


def test_find_version():
    # what ev, who knows if these file even exist
    _ = find_version(PROJECT, SRC, True)

def test_find_version_by_package():
    _ = pkg_resources_version(PROJECT)