#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from setuptools import setup, find_packages


APP_NAME = 'tarbell'
VERSION = '0.9b3'

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
        "Jinja2==2.7.1",
        "MarkupSafe==0.18",
        "PyYAML==3.10",
        "Werkzeug==0.9.4",
        "boto==2.19.0",
        "clint==0.3.1",
        "requests==2.1.0",
        "wsgiref==0.1.2",
        "google-api-python-client==1.2",
        "keyring>=3.2.1",
        "xlrd==0.9.2",
        "python-dateutil>=2.2",
        "docutils==0.11",
        "sh==1.09",
        "sphinx_rtd_theme==0.1.5",
        "Markdown==2.3.1"],
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
