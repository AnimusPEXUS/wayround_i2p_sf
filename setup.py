#!/usr/bin/python3

from distutils.core import setup

setup(
    name='org_wayround_sf',
    version='0.1',
    description='walk() function for sf.net files',
    author='Alexey Gorshkov',
    author_email='animus@wayround.org',
    url='http://wiki.wayround.org/soft/org_wayround_sf',
    packages=[
        'org.wayround.sf',
        ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX',
        'Development Status :: 1 - Planning'
        ]
    )
