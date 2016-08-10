#!/usr/bin/env python

import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='imgc',
    version='0.1.0',
    packages=find_packages(exclude=['tests*']),
    install_requires=['Pillow'],
    include_package_data=True,
    license='BSD License',  
    description='python parallel image compressor/converter',
    long_description=README,
    url='https://github.com/paramono/imgc',
    author='Alexander Paramonov',
    author_email='alex@paramono.com',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers'
        'Intended Audience :: End Users/Desktop'
        'Intended Audience :: Information Technology'
        'Intended Audience :: System Administrators'
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
    ],
    entry_points={
        'console_scripts': [
            'imgc = imgc:main',
        ]
    }
)
