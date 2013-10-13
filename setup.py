#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from setuptools import setup, find_packages


APP_NAME = 'tarbell'
VERSION = '0.9-iter1'

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
    install_requires=[
        "BeautifulSoup==3.2.1",
        "Flask==0.10.1",
        "GitPython==0.3.2.RC1",
        "Jinja2==2.7.1",
        "MarkupSafe==0.18",
        "PyYAML==3.10",
        "Werkzeug==0.9.4",
        "async==0.6.1",
        "clint==0.3.1",
        "gdata==2.0.18",
        "gitdb==0.5.4",
        "itsdangerous==0.23",
        "legit==0.1.1",
        "ordereddict==1.1",
        "requests==1.2.3",
        "scrubber==1.6.1",
        "smmap==0.8.2",
        "unicodecsv==0.9.4",
        "wsgiref==0.1.2",
        "google-api-python-client==1.2",
        "keyring==3.0.2",
        "xlrd==0.9.2",
        "python-dateutil==2.1",
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
