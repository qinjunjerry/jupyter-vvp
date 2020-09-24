from distutils.core import setup

DESCRIPTION = "vvpMagics: Magics to connect to VVP"
NAME = "vvpmagics"
VERSION = '0.0.1'
PACKAGES = ['jupytervvp']
AUTHOR = "Ververica"
AUTHOR_EMAIL = "platform@ververica.com"
URL = 'https://github.com/dataArtisans/vvp-jupyter'
DOWNLOAD_URL = 'https://github.com/dataArtisans/vvp-jupyter'
LICENSE = 'Apache License 2.0'


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      download_url=DOWNLOAD_URL,
      license=LICENSE,
      packages=PACKAGES,
      install_requires=[
          'ipython>=4.0.2',
          'ipykernel',
          'requests'
      ])