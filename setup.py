# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in pibicontrol/__init__.py
from pibicontrol import __version__ as version

setup(
	name='pibicontrol',
	version=version,
	description='IoT Control on Frappe',
	author='PibiCo',
	author_email='pibico.sl@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
