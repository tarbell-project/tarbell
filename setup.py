#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


APP_NAME = 'tarbell'
VERSION = '0.9-iter1'

settings = dict()

# Grab requirments.
with open('requirements.txt') as f:
    required = f.readlines()

# Publish Helper.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

settings.update(
    name=APP_NAME,
    version=VERSION,
    author=u'Chicago Tribune News Applications Team',
    author_email='newsapps@tribune.com',
    url='http://github.com/newsapps/tarbell',
    license='MIT',
    description='A very simple content management system',
    long_description=open('README.md').read(),
    zip_safe=False,
    packages=find_packages(),
    data_files=[
        ('tarbell/tests/example/base',
            ['tarbell/tests/example/base/config.py']),
        ('tarbell/tests/example/base/static',
            ['tarbell/tests/example/base/static/style.css']),
        ('tarbell/tests/example/base/templates',
            ['tarbell/tests/example/base/templates/_base.html']),
        ('tarbell/tests/example/project',
            ['tarbell/tests/example/project/config.py']),
        ('tarbell/tests/example/project/static',
            ['tarbell/tests/example/project/static/style.css']),
        ('tarbell/tests/example/project/templates',
            ['tarbell/tests/example/project/templates/index.html']),
    ],
    install_requires=required,
    entry_points={
        'console_scripts': [
            'tarbell = tarbell.cli:main',
        ],
    },
    keywords=['Development Status :: 3 - alpha',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Internet',
          ],
)


setup(**settings)
