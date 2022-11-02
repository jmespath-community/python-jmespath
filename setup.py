#!/usr/bin/env python

import io

from setuptools import setup, find_packages


setup(
    name='jmespath-community',
    version='1.1.0',
    description='JSON Matching Expressions',
    long_description=io.open('README.rst', encoding='utf-8').read(),
    author='James Saryerwinnie, Springcomp',
    author_email='js@jamesls.com, springcomp@users.noreply.github.com',
    url='https://github.com/jmespath-community/jmespath.py',
    scripts=['bin/jp.py'],
    packages=find_packages(exclude=['tests']),
    license='MIT',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
