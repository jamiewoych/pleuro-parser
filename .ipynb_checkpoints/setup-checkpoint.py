#!/usr/bin/env python

"""
Call `pip install -e .` to install package locally for testing.
"""

from setuptools import setup, find_packages

# build command
setup(
    name="pleuro_parser",
    version="0.0.2",
    author="Jamie Woych",
    author_email="jw3943@columbia.edu",
    license="GPLv3",
    description="A package for salamander inventory",
    classifiers=["Programming Language :: Python :: 3"],
    packages=find_packages(),
    entry_points={
        "console_scripts": ["pleuro_parser = pleuro_parser.__main__:main"]
    },

    install_requires=[  # 
        "seaborn",      # For heatmap plotting
        "streamlit",    # For the webapp interface
        "pandas",       # For handling dataframes and CSV manipulation
        "matplotlib",   # For general plotting and visualization
        "pathlib",      # For handling file paths
        "datetime",     # For date and time manipulation
        "io",           # Part of the standard library, no need to install
        #"os",           # chaning directory if not in right one
        "sys",          # Part of the standard library, no need to install
        "contextlib",   # Part of the standard library, no need to install
    ],
)

