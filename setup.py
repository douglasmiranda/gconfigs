#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
import sys

assert sys.version_info >= (3, 6, 0), "black requires Python 3.6+"

from pathlib import Path

readme = Path("README.rst").read_text()
history = Path("HISTORY.rst").read_text()

setup(
    name="gconfigs",
    version="0.1.4",
    description="gConfigs - Config and Secret parser for your Python projects.",
    long_description=f"{readme}\n\n{history}",
    author="Douglas Miranda",
    author_email="douglascoding@gmail.com",
    url="https://github.com/douglasmiranda/gconfigs",
    packages=find_packages(include=["gconfigs"]),
    include_package_data=True,
    license="MIT license",
    zip_safe=False,
    keywords="gconfigs configs environment secrets dotenv 12-factor",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
