#!/usr/bin/python3

from distutils.core import setup

setup(
    name='wayround_i2p_sf',
    version='0.3.2',
    description='walk() function for sf.net files',
    author='Alexey Gorshkov',
    author_email='animus@wayround.org',
    url='http://wiki.wayround.org/soft/wayround_i2p_sf',
    packages=[
        'wayround_i2p.sf',
        ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX',
        'Development Status :: 1 - Planning'
        ]
    )
