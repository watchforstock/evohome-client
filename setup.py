from setuptools import setup

setup(
	name = 'evohomeclient',
	version = '0.1.0',
	description = 'Python client for connecting to the Evohome webservice',
	url = 'https://github.com/watchforstock/evohome-client/',
	author = 'Andrew Stock',
	author_email = 'evohome@andrew-stock.com',
	license = 'Apache 2',
	classifiers = [
		'Development Status :: 3 - Alpha',
	],
	packages = ['evohomeclient'],
	install_requires = ['requests']
)