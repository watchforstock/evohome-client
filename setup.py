import os
import sys

from setuptools import setup
from setuptools.command.install import install

VERSION = "0.3.6"

class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, VERSION
            )
            sys.exit(info)

setup(
    name='evohomeclient',
    version=VERSION,
    description='Python client for connecting to the Evohome webservice',
    url='https://github.com/watchforstock/evohome-client/',
    download_url='https://github.com/watchforstock/evohome-client/tarball/' + VERSION,
    author='Andrew Stock',
    author_email='evohome@andrew-stock.com',
    license='Apache 2',
    classifiers=[
        'Development Status :: 3 - Alpha',
    ],
    keywords=['evohome'],
    packages=['evohomeclient', 'evohomeclient2'],
    install_requires=['requests'],
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)
