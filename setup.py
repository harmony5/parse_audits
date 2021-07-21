#!/usr/bin/env python

from setuptools import setup

setup(
    name='parse_audits',
    version='1.0',
    packages=[
        'parse_audits',
        'parse_audits.test',
    ],
    scripts=['bin/parser_cli.py'],
    license='LICENSE.txt',
    description='A tool to parse ClearQuest AuditTrail files to an easier to use format.',
    long_description=open('README.md').read(),
    install_requires=[
        'regex >= 2020.5.14',
        'typer >= 0.3.2',
    ],
)