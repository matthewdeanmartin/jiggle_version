#!/usr/bin/env python3

from setuptools import setup

setup(
    name="foo",
    version = "1.1.12",
    description="foo",
    long_description="foo\n",
    long_description_content_type="text/markdown",
    modules=["foo.py"],
    url="http://google.com",
    license="MIT",
    author="foo bar",
    author_email="foo@example.com",
    classifiers=(
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Development Status :: 3 - Alpha",
    ),
    python_requires=">=3.6",
    test_suite="tests",
)
