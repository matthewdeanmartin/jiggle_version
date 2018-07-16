# coding=utf-8
"""
Tests
"""
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError
import os

from docopt import DocoptExit

import jiggle_version.__init__ as init
import jiggle_version.__version__ as v2
import jiggle_version.main as main
from jiggle_version.jiggle_class import JiggleVersion

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


def test_entry_point():
    main.bump_version(PROJECT, SRC, True)
