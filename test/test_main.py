# coding=utf-8
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError
import os

from docopt import DocoptExit

import jiggle_version.__init__ as init
import jiggle_version.__version__ as v2
import jiggle_version.main as main

here = os.path.abspath(os.path.dirname(__file__))
PROJECT = "sample_lib"
SRC = here + "/../sample_src/"

def test_print_versions():
    print(init.__version__)
    print(v2)


def test_go():
    # what ev, who knows if these file even exist
    jiggler = main.JiggleVersion(PROJECT, SRC, True)
    jiggler.create_configs = True
    jiggler.jiggle_source_code()
    jiggler.jiggle_config_file()


def test_no_files():
    for file in [SRC + PROJECT + "__init__.py",
                 SRC + PROJECT + "__version__.py",
                 SRC + "setup.cfg"]:
        try:
            os.remove(file)
        except FileNotFoundError:
            pass

    # doesn't exist
    jiggler = main.JiggleVersion(PROJECT, SRC, True)
    jiggler.create_configs = True
    jiggler.create_all = True
    jiggler.jiggle_source_code()
    jiggler.jiggle_config_file()

    # and already exist
    jiggler = main.JiggleVersion(PROJECT, SRC, True)
    jiggler.create_configs = True
    jiggler.create_all = True
    jiggler.jiggle_source_code()
    jiggler.jiggle_config_file()


def test_process_docopts():
    try:
        main.process_docopts()
    except DocoptExit:
        pass


def test_entry_point():
    main.go(PROJECT, SRC, True)
