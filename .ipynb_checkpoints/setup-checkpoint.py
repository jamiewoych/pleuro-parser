#!/usr/bin/env python

"""
Call `pip install -e .` to install package locally for testing.
"""

from setuptools import setup, find_packages

# build command
setup(
    name="mini_project",
    version="0.0.1",
    author="Jamie Woych",
    author_email="jw3943@columbia.edu",
    license="GPLv3",
    description="A package for salamander inventory",
    classifiers=["Programming Language :: Python :: 3"],
    packages=find_packages(),
    entry_points={
        "console_scripts": ["mini_project = mini_project.__main__:main"]
    },
)


