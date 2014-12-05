from distutils.core import setup
from onvif import __version__

setup(name='onvif',
      version=__version__,
      packages=['onvif'],
      description='Python client for ONVIF Camera',
      author='quatanium',
      author_email='sinchb128@gmail.com',
      maintainer='sinchb',
      maintainer_email='sinchb128@gmail.com',
      keywords=['ONVIF', 'Camera']
     )


