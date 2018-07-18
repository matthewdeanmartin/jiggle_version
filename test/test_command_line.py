# coding=utf-8
"""
Tests
"""
import subprocess

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

    result = execute_get_text("python -m jiggle_version find")
    print(result)
    assert result