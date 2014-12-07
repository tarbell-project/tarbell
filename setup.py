#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from setuptools import setup, find_packages


APP_NAME = 'tarbell'
VERSION = '0.9b7'

settings = dict()

# Publish Helper.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

settings.update(
    name=APP_NAME,
    version=VERSION,
    author=u'Chicago Tribune News Applications Team',
    author_email='newsapps@tribune.com',
    url='http://github.com/newsapps/flask-tarbell',
    license='MIT',
    description='A very simple content management system',
    long_description='',
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask==0.10.1",
        "Jinja2==2.7.3",
        "Markdown==2.4.1",
        "MarkupSafe==0.23",
        "PyYAML==3.11",
        "boto==2.34.0",
        "clint==0.4.1",
        "gnureadline==6.3.3",
        "google-api-python-client==1.3.1",
        "keyring==4.0",
        "python-dateutil>=2.2",
        "requests==2.3.0",
        "sh==1.09",
        "wsgiref==0.1.2",
        "xlrd==0.9.3",
    ],
    entry_points={
        'console_scripts': [
            'tarbell = tarbell.cli:main',
        ],
    },
    keywords=['Development Status :: 4 - beta',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Internet',
          ],
)


setup(**settings)
