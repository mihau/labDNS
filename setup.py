# -*- coding: utf-8 -*-
from setuptools import setup
import os

VERSION = '0.1'

INSTALL_REQUIRES = []

README = os.path.join(os.path.dirname(__file__), 'README.md')

setup(
    name='labDNS',
    version=VERSION,
    author='Michał Szymański',
    author_email='michalszymanski91@gmail.com',
    description='Simple DNS server for testing purposes.',  # noqa

    packages=['labDNS'],

    include_package_data=True,
    install_requires=[],
    zip_safe=False,

    license="BSD",

    entry_points={
        'console_scripts': [
            'labDNS= labDNS.resolver:main'
        ]
    }
)
