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

various = {
    PROJECT: SRC,
    "setup_only": here + "/../sample_projects/setup_only/",
    "file_module_src":  here + "/../sample_projects/file_module_src/",
    "double_module":  here + "/../sample_projects/double_module/",
}

def test_go():
    # what ev, who knows if these file even exist
    for key, value in various.items():
        try:
            os.chdir(value)
            jiggler = JiggleVersion(key, "", True)
            jiggler.create_configs = True
            changed = jiggler.jiggle_all()
            assert changed>0
        finally:
            os.chdir("../../test")
        assert changed > 0


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

    # put app in dir with setup.py. Easier!
    try:
        os.chdir(SRC)
        # doesn't exist
        jiggler = JiggleVersion(PROJECT, "", True)
        jiggler.create_configs = True
        jiggler.create_all = True
        jiggler.jiggle_all()

        # and already exist
        jiggler = JiggleVersion(PROJECT, "", True)
        jiggler.create_configs = True
        jiggler.create_all = True
        jiggler.jiggle_all()

    finally:
        os.chdir("../../test")

