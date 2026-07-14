# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from setuptools import setup, find_packages
from kirana_ledger import __version__ as version

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="kirana_ledger",
    version=version,
    description="Hyper-Local Inventory + Udhaar (Credit) Ledger for Kirana Stores",
    author="Pasha1234565",
    author_email="",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
