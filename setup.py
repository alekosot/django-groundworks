#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

from groundworks import __author__, __email__, __version__

with open('README.rst') as readme_file:
    readme = readme_file.read()


requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='django_groundworks',
    version=__version__,
    description="Utilities for django projects",
    long_description=readme,
    author=__author__,
    author_email=__email__,
    url='https://github.com/alxs/django_groundworks',
    packages=[
        'django-groundworks',
    ],
    package_dir={
        'django-groundworks': 'groundworks'
    },
    include_package_data=True,
    install_requires=requirements,
    license="BSD license",
    zip_safe=False,
    keywords='django_groundworks',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
