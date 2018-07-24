# coding=utf-8
"""
Tests
"""
from jiggle_version.file_opener import FileOpener

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

import os

from jiggle_version.jiggle_class import JiggleVersion
initial_pwd= os.getcwd()
here = os.path.abspath(os.path.dirname(__file__))
PROJECT = "sample_lib"
SRC = here + "/../sample_projects/sample_src/"

various_old = {
    # PROJECT: SRC,
    ("setup_only", ""): here + "/../sample_projects/setup_only/",
    ("file_module_src", ""): here + "/../sample_projects/file_module_src/",
    # ("file_module_ver_in_file",""): here + "/../sample_projects/file_module_ver_in_file/",
    ("double_module", ""): here + "/../sample_projects/double_module/",
    ("ver_in_weird_file", ""): here + "/../sample_projects/ver_in_weird_file/",
    ("with_unlikely_modules", ""): here + "/../sample_projects/with_unlikely_modules/",
}

various = {
    ("dupes", ""): here + "/../sample_projects/dupes_in_dunders/",
}

def test_new_probs():
    # what ev, who knows if these file even exist

    f = FileOpener()
    for key, value in various.items():
        try:
            os.chdir(value)
            jiggler = JiggleVersion(key[1], key[0], f)
            jiggler.create_configs = True
            changed = jiggler.jiggle_all()
            assert changed>0
        finally:
            os.chdir(initial_pwd)
        assert changed > 0

def test_old_probs():
    # what ev, who knows if these file even exist

    f = FileOpener()
    for key, value in various.items():
        try:
            os.chdir(value)
            jiggler = JiggleVersion(key[0], key[1], f)
            jiggler.create_configs = True
            changed = jiggler.jiggle_all()
            assert changed>0
        finally:
            os.chdir(initial_pwd)


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
    f = FileOpener()
    # put app in dir with setup.py. Easier!
    try:
        os.chdir(SRC)
        # doesn't exist
        jiggler = JiggleVersion(PROJECT, "",f)
        jiggler.create_configs = True
        jiggler.create_all = True
        jiggler.jiggle_all()

        # and already exist
        jiggler = JiggleVersion(PROJECT, "",f)
        jiggler.create_configs = True
        jiggler.create_all = True
        jiggler.jiggle_all()

    finally:
        os.chdir(initial_pwd)

