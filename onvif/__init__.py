from onvif.client import ONVIFService, ONVIFCamera
from onvif.exceptions import ONVIFError, ERR_ONVIF_UNKNOWN, ERR_ONVIF_PROTOCOL, \
        ERR_ONVIF_WSDL, ERR_ONVIF_BUILD

__version__ = '0.1.0'
VERSION = tuple(map(int, __version__.split('.')))

__all__ = ( 'ONVIFService', 'ONVIFCamera', 'ONVIFError', 'ERR_ONVIF_UNKNOWN',
             'ERR_ONVIF_PROTOCOL', 'ERR_ONVIF_WSDL', 'ERR_ONVIF_BUILD' )
