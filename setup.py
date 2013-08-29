#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


APP_NAME = 'tarbell'
APP_SCRIPT = './tarbell_runner'
VERSION = '0.8'

settings = dict()

# Grab requirments.
with open('requirements.txt') as f:
    required = f.readlines()

# Publish Helper.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


# Build Helper.
if sys.argv[-1] == 'build':
    try:
        import py2exe
    except ImportError:
        print 'py2exe is required to continue.'
        sys.exit(1)

    sys.argv.append('py2exe')

    settings.update(
        console=[{'script': APP_SCRIPT}],
        zipfile = None,
        options = {
            'py2exe': {
                'compressed': 1,
                'optimize': 0,
                'bundle_files': 1}})

settings.update(
    name=APP_NAME,
    version=VERSION,
    author=u'Chicago Tribune News Applications Team',
    author_email='newsapps@tribune.com',
    packages=['tarbell',],
    url='http://github.com/newsapps/tarbell',
    license='MIT',
    description= 'A very simple content management system',
    long_description=open('README.md').read(),
    zip_safe=False,
    include_package_data=True,
    install_requires=required,
)


setup(**settings)


