# coding=utf-8
"""
Tests
"""
import os
import sys
import subprocess
initial_pwd= os.getcwd()
here = os.path.abspath(os.path.dirname(__file__))
PROJECT = "jiggle_version"
SRC = here + "/.."

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

def execute_get_text(command):
    try:
        result = subprocess.check_output(
            command,
            stderr=subprocess.STDOUT,
            shell=True)
        print(result.decode())
    except subprocess.CalledProcessError as err:
        print(err)
        # try:
        #     print(err.stdout)
        # except:
        #     pass
        # try:
        #     print(err.stderr)
        # except:
        #     pass
        raise

    return result.decode('utf-8')

def test_where_am_i():
    try:
        os.chdir(SRC)
        print(os.getcwd())
        result = execute_get_text("pwd")
        print(result)
        assert str(result).strip().endswith("jiggle_version"), str(result)
    finally:
        os.chdir("test")

def test_self_version():
    try:
        os.chdir(SRC)
        print(os.getcwd())
        result = execute_get_text("python -m jiggle_version --version --debug=True")
        print(result)
        assert result
    finally:
        os.chdir(initial_pwd)

# broken - either everywhere or on 2.7. No clues.
# def test_find_version():
#     try:
#         os.chdir(SRC)
#         result = execute_get_text("python -m jiggle_version find --debug=True")
#         print(result)
#         assert result
#     finally:
#         os.chdir("test")
#
# def test_find_modify():
#     try:
#         SRC = here + "/../sample_projects/sample_src/"
#         os.chdir(SRC)
#         print(os.getcwd())
#         result = execute_get_text("python -m jiggle_version here --debug=True")
#         print(result)
#         assert result
#     finally:
#         os.chdir("../../")
