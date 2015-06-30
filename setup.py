#!/usr/bin/python3

from distutils.core import setup

setup(
    name='wayround_org_sf',
    version='0.3.1',
    description='walk() function for sf.net files',
    author='Alexey Gorshkov',
    author_email='animus@wayround.org',
    url='http://wiki.wayround.org/soft/wayround_org_sf',
    packages=[
        'wayround_org.sf',
        ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX',
        'Development Status :: 1 - Planning'
        ]
    )
