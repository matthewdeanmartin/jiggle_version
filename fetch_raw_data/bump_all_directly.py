# coding=utf-8
"""
Go!
"""

import logging
import os
import random
import sys

from jiggle_version.commands import bump_version
from jiggle_version.file_opener import FileOpener
from jiggle_version.main import console_trace
from jiggle_version.project_finder import ModuleFinder
from jiggle_version.utils import JiggleVersionException

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

things = [x for x in os.listdir("packages")]
random.shuffle(things)
console_trace(logging.DEBUG)

bumped = 0
failed = 0
failed_dirs_module =[]
failed_dirs_bumping =[]
failed_dirs_nothing_changed =[]
messages = {}
no_ver_found = []
for dir in things:
    if "bjad" in dir:
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
            f = FileOpener() # don't re-used encodings until it is absolute paths
            module_finder = ModuleFinder(f)
            candidates = module_finder.find_project()
            print(candidates)
        except JiggleVersionException as jve:
            failed += 1
            failed_dirs_module.append(dir)
            print("Failure looking for a module")
            print(os.getcwd())
            print(jve)
            continue

        try:
            if not candidates:
                raise TypeError("No project found")
        except TypeError as te:
            failed += 1
            failed_dirs_module.append(dir)
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
            v = bump_version(candidates[0], guess_src_dir, True)
            if v:
                bumped+=1
            else:
                failed+=1
                failed_dirs_nothing_changed.append(dir)
        except JiggleVersionException as jve:
            if str(jve) in messages:
                messages[str(jve)] +=1
            else:
                messages[str(jve)] = 1
            if "Have no versions to work with, failed to find any" in str(jve):
                no_ver_found.append(dir)

            failed += 1
            failed_dirs_bumping.append(dir)
            print("Failure editing modules")
            print(os.getcwd())
            print(jve)
            continue

    finally:
        os.chdir("../..")

print("bumped", "failed")
print(bumped, failed)

print("'main' module not found" + str(len(failed_dirs_module)))
print(failed_dirs_module)

print("nothing changed" + str(len(failed_dirs_nothing_changed)))
print(failed_dirs_nothing_changed)

print("error while bumping" + str(len(failed_dirs_bumping)))
print(failed_dirs_bumping)

print(messages)

print("No ver found projects" + str(len(no_ver_found)))
print(no_ver_found)

x ={'Have no versions to work with, failed to find any.': 80,
    'Have path_dict, but has more than one path.': 3, # multiple projects to bump? Might as well I guess.
    "Can't continue: Versions not in sync, won't continue": 22, # NOT MY FAULT.
    'Either this is hard to parse or we have 2+ src foldrs': 12, # multiple projects to bump? Might as well I guess.
    "Can't find setup.py : setup.py, path :": 3}
z = {'Have path_dict, but has more than one path.': 6,
     "Can't continue: Versions not in sync, won't continue": 22,
     'Have no versions to work with, failed to find any.': 65,
     "Can't continue: setup.py has use_scm_version=True in it- this means we expect no file to have a version string. Nothing to change": 18,
     "Can't find setup.py : setup.py, path :": 3,
     'Either this is hard to parse or we have 2+ src foldrs': 1}
y = {'Have path_dict, but has more than one path.': 6,
     'Have no versions to work with, failed to find any.': 34,
     "Can't continue: setup.py has use_scm_version=True in it- this means we expect no file to have a version string. Nothing to change": 18,
     "Can't find setup.py : setup.py, path :": 3,
     "Can't continue: Versions not in sync, won't continue": 22,
     'Either this is hard to parse or we have 2+ src foldrs': 1}
p = {"Can't find setup.py : setup.py, path :": 3,
     'Have no versions to work with, failed to find any.': 23,
     "Can't continue: setup.py has use_scm_version=True in it- this means we expect no file to have a version string. Nothing to change": 18,
     "Can't continue: Versions not in sync, won't continue": 22,
     'Either this is hard to parse or we have 2+ src foldrs': 1,
     'Have path_dict, but has more than one path.': 6}

