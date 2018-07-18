# coding=utf-8
"""
Go!
"""

import logging
import os
import random
import sys

from jiggle_version.commands import bump_version
from jiggle_version.main import console_trace
from jiggle_version.project_finder import ModuleFinder
from jiggle_version.utils import JiggleVersionException

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

things = [x for x in os.listdir("packages")]
random.shuffle(things)
console_trace(logging.DEBUG)
for dir in things:
    if "abjad" in dir:
        # weird encoding
        continue
    if dir.endswith(".gz") or dir.endswith(".zip"):
        continue
    if ".DS_Store" in dir:
        continue

    print("---{0}---".format(dir))
    candidates = None
    try:
        os.chdir("packages/{0}".format(dir))
        try:
            module_finder = ModuleFinder()
            candidates = module_finder.find_project()
            print(candidates)
        except JiggleVersionException as jve:
            print("Failure looking for a module")
            print(os.getcwd())
            print(jve)
            continue

        try:
            if not candidates:
                raise TypeError("No project found")
        except TypeError as te:
            print(os.getcwd())
            print(te)
            continue

        try:
            guess_src_dir = module_finder.extract_package_dir()
            if not guess_src_dir:
                guess_src_dir = ""
            if candidates[0] == guess_src_dir:
                if not os.path.isdir(os.path.join(guess_src_dir,candidates[0])):
                    # HACK: not sure if this is a good idea.
                    guess_src_dir = ""
            bump_version(candidates[0], guess_src_dir, True)
        except JiggleVersionException as jve:
            print("Failure editing modules")
            print(os.getcwd())
            print(jve)
            continue

    finally:
        os.chdir("../..")
