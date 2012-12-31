from distutils.core import setup
from setuptools import find_packages

setup(
    name='tarbell',
    version='0.2',
    author=u'David Eads',
    author_email='davideads@gmail.com',
    packages=find_packages(),
    url='http://github.com/newsapps/tarbell',
    license='MIT, see LICENSE',
    description= 'A very simple web authoring tool.',
    long_description=open('README').read(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'Flask>=0.9',
        'boto>=2.3.0',
        'requests>=0.11.2',
        'gdata>=2.0.17',
        'ordereddict>=1.1',
    ]
)
