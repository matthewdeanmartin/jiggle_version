"""
Tests
"""
# from docopt import DocoptExit

import jiggle_version.__init__ as init
import jiggle_version._version as v2
import jiggle_version.main as main
from jiggle_version.utils import JiggleVersionException

# _ = jiggle_version.package_info_finder

import os

initial_pwd = os.getcwd()
here = os.path.abspath(os.path.dirname(__file__))
PROJECT = "sample_lib"
SRC = here + "/../sample_projects/sample_src/"


def test_print_versions():
    print(init.__version__)
    print(v2)


#
# def test_process_docopts():
#     try:
#         main.process_docopts()
#     except DocoptExit:
#         pass


def test_process_docopts_fake_it():
    try:
        os.chdir(SRC)
        args = {
            "--debug": "False",
            "--help": "False",
            "--module": None,
            "--project": "sample_lib",
            "--source": None,
            "--version": "False",
            "--init": "False",
            "find": "True",
            "here": "False",
            "--signature": "False",
        }
        main.process_docopts(args)
    except JiggleVersionException as jve:
        print(os.getcwd())
        raise
    finally:
        os.chdir(initial_pwd)


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
