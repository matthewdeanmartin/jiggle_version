# coding=utf-8
"""
Finds project by folder & source inspection.  Enables zero config by not
asking the user something we can probably infer.
"""
import os

from typing import List

# so formatter doesn't remove.
_ = List


def find_project():  # type: () -> List[str]
    folders = files = [f for f in os.listdir(".") if os.path.isdir(f)]
    found = 0
    candidates = []
    for folder in folders:
        if os.path.isfile(folder + "/__init__.py"):
            project = folder
            candidates.append(folder)
    # TODO: parse setup.py
    # TODO: parse setup.cfg

    return candidates
