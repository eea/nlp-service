#!/usr/bin/env python

from distutils.core import setup

setup(
    name='NLP Service',
    version='1.0',
    description='NLP Service',
    author='Tiberiu Ichim',
    author_email='tiberiu.ichim@eaudeweb.ro',
    packages=['app'],
    install_requires=[
        'venusian',
        'uvicorn',
    ]
)
