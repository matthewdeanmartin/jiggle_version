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
        print(result)
    except subprocess.CalledProcessError as err:
        print(err)
        print(err.stdout)
        print(err.stderr)
        raise

    return result.decode('utf-8')


def test_find_version():
    try:
        os.chdir(SRC)
        result = execute_get_text("python -m jiggle_version find")
        print(result)
        assert result
    finally:
        os.chdir("test")
