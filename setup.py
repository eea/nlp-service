#!/usr/bin/env python
# from distutils.core import setup
#
# setup(
#     name='NLP Service',
#     version='1.0',
#     description='NLP Service',
#     author='Tiberiu Ichim',
#     author_email='tiberiu.ichim@eaudeweb.ro',
#     package_dir={'': 'app'},
#     packages=['app'],
#     install_requires=[
#         'venusian',
#         'uvicorn',
#     ]
# )
#
#
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="NLPService",
    version="1.0",
    description='NLP Service',
    author='Tiberiu Ichim',
    author_email='tiberiu.ichim@eaudeweb.ro',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # packages=['app'],
    # package_dir={"app": "."},
    packages=setuptools.find_packages(),
    # python_requires=">=3.6",
    install_requires=[
        'venusian',
        'uvicorn',
        'fastapi_chameleon',
        'pygraphviz',
        'jq',
    ]
)
