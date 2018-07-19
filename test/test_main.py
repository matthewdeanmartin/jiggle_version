# coding=utf-8
"""
Tests
"""
from docopt import DocoptExit

import jiggle_version.__init__ as init
import jiggle_version.__version__ as v2
import jiggle_version.main as main
from jiggle_version.utils import JiggleVersionException

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError
import os
initial_pwd= os.getcwd()
here = os.path.abspath(os.path.dirname(__file__))
PROJECT = "sample_lib"
SRC = here + "/../sample_projects/sample_src/"

def test_print_versions():
    print(init.__version__)
    print(v2)

def test_process_docopts():
    try:
        main.process_docopts()
    except DocoptExit:
        pass


def test_process_docopts_fake_it():
    try:
        os.chdir(SRC)
        args = {'--debug': 'False',
            '--help': False,
            '--project': None,
            '--source': None,
            '--version': False,
            'find': True,
            'here': False}
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
        main.bump_version(PROJECT, "", True)
    except JiggleVersionException as jve:
        print(os.getcwd())
        raise
    finally:
        os.chdir(initial_pwd)


