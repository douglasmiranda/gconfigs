#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

setup(
    name='gconfigs',
    version='0.1.1',
    description="gConfigs - Config and Secret parser for your Python projects.",
    long_description=readme + '\n\n' + history,
    author="Douglas Miranda",
    author_email='douglasmirandasilva@gmail.com',
    url='https://github.com/douglasmiranda/gconfigs',
    packages=find_packages(include=['gconfigs']),
    include_package_data=True,
    license="MIT license",
    zip_safe=False,
    keywords='gconfigs configs environment secrets dotenv',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
)
