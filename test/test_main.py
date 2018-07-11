# coding=utf-8

import jiggle_version.main as main

import jiggle_version.__init__ as init
import jiggle_version.__version__ as v2

def test_print_versions():
    print(init.__version__)
    print(v2)

def test_dunder_main():
    import jiggle_version.__main__

def test_go():
    jiggler = main.JiggleVersion()
    jiggler.jiggle_source_code()
    jiggler.jiggle_config_file()

