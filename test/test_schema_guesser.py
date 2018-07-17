# # coding=utf-8
# """
# Tests
# """
#
# from jiggle_version.schema_guesser import guess_schema
#
# try:
#     FileNotFoundError
# except NameError:
#     FileNotFoundError = IOError
#
# import os
#
# here = os.path.abspath(os.path.dirname(__file__))
# PROJECT = "sample_lib"
# SRC = here + "/../sample_projects/sample_src/"
#
#
# def test_guess_version():
#     # what ev, who knows if these file even exist
#     _ = guess_schema("PROJECT, SRC, True", "whatev")
