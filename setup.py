#!/usr/bin/env python

from setuptools import setup, find_packages

requires = [
    'Flask',
    'Flask-RESTful',
    'grpcio == 1.11.0',
    'grpcio-tools == 1.11.0',
    'protobuf>=3.2.0',
    'secp256k1',
    'jsonrpcserver',
    'pyopenssl',
    'plyvel'
]

setup_options = {
    'name': 'iconservice', 
    'version': '0.0.1',
    'description': 'iconservice for python',
    'long_description': open('docs/class.md').read(),
    'author': 'ICON foundation',
    'author_email': 'foo@icon.foundation',
    'packages': find_packages(exclude=['tests*','docs']),
    'license': "Apache License 2.0",
    'install_requires': requires,
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers', 
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6'
    ]
}

setup(**setup_options)