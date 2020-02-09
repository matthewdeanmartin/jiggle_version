"""
Module finder
"""
import os
from jiggle_version.file_opener import FileOpener
from jiggle_version.central_module_finder import CentralModuleFinder


initial_pwd = os.getcwd()


# def test_go():
#     try:
#         if not os.getcwd().endswith("test"):
#             os.chdir(initial_pwd)
#         fo = FileOpener()
#         cmf = CentralModuleFinder(file_opener=fo)
#         central = cmf.find_central_module()
#         assert central == "sample_lib", central
#     finally:
#         os.chdir(initial_pwd)


def test_setup_name():
    try:
        if os.getcwd().endswith("test"):
            os.chdir("..")
        fo = FileOpener()
        cmf = CentralModuleFinder(file_opener=fo)
        cmf.find_setup_file_name()
        assert cmf.setup_file_name == "setup.py"
    finally:

        os.chdir(initial_pwd)
