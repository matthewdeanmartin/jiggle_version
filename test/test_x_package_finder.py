"""
package info finder
"""
import os
from jiggle_version.file_opener import FileOpener
from jiggle_version.parse_package.package_info_finder import PackageInfoFinder

initial_pwd = os.getcwd()


# def test_find_setup_py():
#     try:
#         if os.getcwd().endswith("test"):
#             os.chdir("..")
#         print(os.getcwd())
#         fo = FileOpener()
#         pif = PackageInfoFinder(file_opener=fo)
#
#         from_setup_py = pif.setup_py_source()
#         assert from_setup_py
#
#     finally:
#
#         os.chdir(initial_pwd)


def test_find_package_dir():
    try:
        if os.getcwd().endswith("test"):
            os.chdir("..")
        print(os.getcwd())
        fo = FileOpener()
        pif = PackageInfoFinder(file_opener=fo)

        package_dir = pif.extract_package_dir()
        assert package_dir is None
    finally:

        os.chdir(initial_pwd)
