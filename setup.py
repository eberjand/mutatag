#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name='mutatag',
    version='0.1',
    description='Audio metadata tagger for FLAC/OGG/OPUS/MP3/M4A',
    url='https://github.com/eberjand/mutatag',
    license='MIT',
    entry_points={
        'console_scripts': [
            'mutatag = mutatag.mutatag:main',
            #'mutacopytags = mutatag.copytags:copytags'
        ]
    },
    install_requires=['mutagen>=1.31.0'],
    packages=find_packages()
)
