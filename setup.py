# -*- coding: utf-8 -*-

import lshash

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

with open('CHANGES.rst') as f:
    changes = f.read()

required = ['numpy']

setup(
    name='lshash',
    version=lshash.__version__,
    packages=['lshash'],
    author='Kay Zhu',
    author_email='me@kayzhu.com',
    maintainer='Kay Zhu',
    maintainer_email='me@kayzhu.com',
    description='A fast Python implementation of locality sensitive hashing with persistance support.',
    long_description=readme + '\n\n' + changes,
    license=license,
    requires=required,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries',
        ],
)
