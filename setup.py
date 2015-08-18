#!/usr/bin/env python
# encoding: utf-8
import re
from setuptools import setup
from tornado_psycopg2 import __author__, __version__

author = re.compile(r"(?P<name>[^\<]+)\s{1,}\<(?P<email>.*)\>").match(__author__).groupdict()

setup(
    name='tornado-psycopg2',
    version=__version__,
    author=author['name'],
    author_email=author['email'],
    license="MIT",
    platforms="all",
    classifiers=(
        'Environment :: Console',
        'Programming Language :: Python',
    ),
    long_description=open('README.rst').read(),
    description='Tornado driver for support asynchronous mode for psycopg2.',
    include_package_data=False,
    packages=['tornado_psycopg2'],
    requires=['Python (>2.6)'],
    install_requires=[i.strip() for i in open('requirements.txt').read().split('\n') if i],
)
