"""
Setup for pypi support
"""
import codecs
import os
import sys

from setuptools import find_packages, setup  # , setup, Command

PROJECT_NAME = "jiggle_version"

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = "\n" + f.read()
about = {}
with open(os.path.join(here, PROJECT_NAME, "_version.py")) as f:
    exec(f.read(), about)
if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel upload")
    sys.exit()
required = [
    "docopt",  # command line parser
    "semantic_version",  # sem ver parser
    "cmp-version",
    "parver",  # pep440 parser
    "versio",  # pep440 parser
    "chardet",  # for reading source code files
]

setup(
    name=PROJECT_NAME,
    version=about["__version__"],
    description="Opinionated, no config build version incrementer. No regex. Drop in and go.",
    long_description=long_description,
    # markdown is not supported. Easier to just convert md to rst with pandoc
    # long_description_content_type='text/markdown',
    author="Matthew Martin",
    author_email="matthewdeanmartin@gmail.com",
    url="https://github.com/matthewdeanmartin/" + PROJECT_NAME,
    packages=find_packages(exclude=["test"]),
    entry_points={
        "console_scripts": ["jiggle_version=jiggle_version.main:process_docopts"]
    },
    install_requires=required,
    extras_require={},
    include_package_data=True,
    license="MIT",
    keywords="version, build tools",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    # setup_cfg=True,
    setup_requires=[],
)
