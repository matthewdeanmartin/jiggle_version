# coding=utf-8
"""
Tests
"""
import subprocess

def execute_get_text(command):
    try:
        completed = subprocess.run(
            command,
            check=True,
            shell=True,
            stdout=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as err:
        raise
    else:
        return completed.stdout.decode('utf-8')

def test_find_version():

    result = execute_get_text("python -m jiggle_version find")
    assert result