# coding=utf-8
"""
Tests
"""
import os
import sys
import subprocess
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
        assert result == "jiggle_version"
    finally:
        os.chdir("test")

def test_self_version():
    try:
        os.chdir(SRC)
        print(os.getcwd())
        result = execute_get_text("python -m jiggle_version --version")
        print(result)
        assert result
    finally:
        os.chdir("test")

def test_find_version():
    try:
        os.chdir(SRC)
        result = execute_get_text("python -m jiggle_version find")
        print(result)
        assert result
    finally:
        os.chdir("test")

def test_find_modify():
    try:
        SRC = here + "/../sample_projects/sample_src/"
        os.chdir(SRC)
        result = execute_get_text("python -m jiggle_version here")
        print(result)
        assert result
    finally:
        os.chdir("../../")
