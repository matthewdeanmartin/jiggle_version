from mypyc.build import mypycify
from setuptools import setup

setup(
    name='jiggle_version',
    packages=['jiggle_version'],
    ext_modules=mypycify([
        '--disallow-untyped-defs',  # Pass a mypy flag
        'jiggle_version',
    ]),
)