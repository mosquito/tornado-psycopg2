#!/usr/bin/env python
# encoding: utf-8
from pip.req import parse_requirements
from setuptools import setup
from tornado_psycopg2 import __author__, __version__


setup(
    name='tornado-psycopg2',
    version=__version__,
    author=__author__,
    author_email='admin@daloo.ru',
    license="MIT",
    platforms="all",
    classifiers=(
        'Environment :: Console',
        'Programming Language :: Python',
    ),
    long_description=open('README.rst').read(),
    include_package_data=False,
    packages=('tornado_psycopg2',),
    requires=(
        'Python (>2.6)',
    ),
    install_requires=(str(i.req) for i in parse_requirements('requirements.txt', session=False)),
)
