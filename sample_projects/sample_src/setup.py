# coding=utf-8
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from distutils.core import setup

PROJECT_NAME = "sample_lib"

here = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(here, PROJECT_NAME, "__version__.py")) as f:
    exec(f.read(), about)

setup(
    name=PROJECT_NAME,
    version=about['__version__'],
)
