# coding=utf-8
"""
Tests
"""
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

import os

from jiggle_version.jiggle_class import JiggleVersion

here = os.path.abspath(os.path.dirname(__file__))
PROJECT = "sample_lib"
SRC = here + "/../sample_projects/sample_src/"


def test_go():
    # what ev, who knows if these file even exist
    jiggler = JiggleVersion(PROJECT, SRC, True)
    jiggler.create_configs = True
    jiggler.jiggle_source_code()
    jiggler.jiggle_config_file()


def test_no_files():
    for file in [SRC + PROJECT + "/__init__.py",
                 SRC + PROJECT + "/__version__.py",
                 SRC + "setup.cfg"]:
        try:
            os.remove(file)
        except FileNotFoundError:
            pass
        except OSError:
            pass

    # doesn't exist
    jiggler = JiggleVersion(PROJECT, SRC, True)
    jiggler.create_configs = True
    jiggler.create_all = True
    jiggler.jiggle_source_code()
    jiggler.jiggle_config_file()

    # and already exist
    jiggler = JiggleVersion(PROJECT, SRC, True)
    jiggler.create_configs = True
    jiggler.create_all = True
    jiggler.jiggle_source_code()
    jiggler.jiggle_config_file()
