#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'molssi_workflow>=0.1',
    'molssi_util>=0.1'
    # TODO: put any other package requirements here
]

setup_requirements = [
    'pytest-runner',
    # TODO(paulsaxe): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name='molssi_widgets',
    version='0.1.0',
    description="Tk widgets to support the MolSSI Framework",
    long_description=readme + '\n\n' + history,
    author="Paul Saxe",
    author_email='psaxe@vt.edu',
    url='https://github.com/paulsaxe/molssi_widgets',
    packages=find_packages(include=['molssi_widgets']),
    include_package_data=True,
    install_requires=requirements,
    license="BSD license",
    zip_safe=False,
    keywords='molssi_widgets',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Materials Science',
        'Topic :: Scientific/Engineering :: Computational Materials Science',
        'Topic :: Scientific/Engineering :: Computational Molecular Science',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3  :: Only',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    entry_points={
    }
)
