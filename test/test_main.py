"""
Tests
"""

# from docopt import DocoptExit

import os

import jiggle_version.__init__ as init
import jiggle_version.__main__ as main
import jiggle_version._version as v2
from jiggle_version.utils import JiggleVersionException

# _ = jiggle_version.package_info_finder


initial_pwd = os.getcwd()
here = os.path.abspath(os.path.dirname(__file__))
PROJECT = "sample_lib"
SRC = here + "/../sample_projects/sample_src/"


def test_print_versions():
    print(init.__version__)
    print(v2)


def test_entry_point():
    # put app in dir with setup.py. Easier!
    try:
        os.chdir(SRC)
        main.bump_version(PROJECT, "", force_init=True, signature=True)
    except JiggleVersionException as jve:
        print(os.getcwd())
        raise
    finally:
        os.chdir(initial_pwd)
