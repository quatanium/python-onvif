import os
#from distutils.core import setup
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
version_path = os.path.join(here, 'onvif/version.txt')
version = open(version_path).read().strip()

requires = [ 'suds >= 0.4' ]

setup(name='onvif',
      version=version,
      description='Python client for ONVIF Camera',
      packages=['onvif'],
      url='https://github.com/quatanium/python-onvif',
      author='quatanium',
      author_email='sinchb128@gmail.com',
      maintainer='sinchb',
      maintainer_email='sinchb128@gmail.com',
      keywords=['ONVIF', 'Camera'],
      install_requires=requires,
      include_package_data=True,
      entry_points={
          'console_scripts': ['onvif-cli = onvif.cli:main']
          }
     )


