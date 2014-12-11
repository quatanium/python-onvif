__version__ = '0.0.1'

import os.path
from types import InstanceType
import urlparse
import urllib
from threading import Thread

import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.CRITICAL)

from suds.client import Client
from suds.wsse import Security, UsernameToken
from suds_passworddigest import UsernameDigestToken
from onvif.exceptions import ONVIFError

SUPPORTED_SERVICES = ('devicemgmt', 'ptz', 'media',
                      'events', 'imaging', 'analytics')

# Ensure methods to raise an ONVIFError Exception
# when some thing was wrong
def safe_func(func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            raise ONVIFError(err)
    return wrapped


class ONVIFService(object):
    '''
    Python Implemention for ONVIF Service.
    Services List:
        DeviceMgmt DeviceIO Event AnalyticsDevice Display Imaging Media
        PTZ Receiver RemoteDiscovery Recording Replay Search Extension

    >>> from onvif import ONVIFService
    >>> device_service = ONVIFService('http://192.168.0.112/onvif/device_service',
    ...                           'admin', 'foscam',
    ...                           '/home/linuxdev3/workspace/router/onvif/wsdl/devicemgmt.wsdl')
    >>> ret = device_service.GetHostname()
    >>> print ret.FromDHCP
    >>> print ret.Name
    >>> device_service.SetHostname(dict(Name='newhostname'))
    >>> ret = device_service.GetSystemDateAndTime()
    >>> print ret.DayLightSavings
    >>> print ret.TimeZone
    >>> dict_ret = device_service.to_dict(ret)
    >>> print dict_ret['TimeZone']

    There are two ways to pass parameter to services methods
    1. Dict
        params = {'Name': 'NewHostName'}
        device_service.SetHostname(params)
    2. Type Instance
        params = device_service.create_type('SetHostname')
        device_service.SetHostname(params)

        time_params = device_service.create_type('SetSystemDateAndTime')
        time_params.DateTimeType = 'Manual'
        time_params.DaylightSavings = True
        time_params.TimeZone = 'CST-8:00:00'
        time_params.UTCDateTime.Date.Year = 2014
        time_params.UTCDateTime.Date.Month = 12
        time_params.UTCDateTime.Date.Day = 3
        time_params.UTCDateTime.Time.Hour = 9
        time_params.UTCDateTime.Time.Minute = 36
        time_params.UTCDateTime.Time.Second = 11
        device_service.SetSystemDateAndTime(time_params)
    '''

    @safe_func
    def __init__(self, xaddr, user, passwd, url,
                 cache_location=None, cache_duration=None,
                 encrypt=False, daemon=False, ws_client=None):

        if not os.path.isfile(url):
            raise ONVIFError('%s doesn`t exist!' % url)

        # Convert pathname to url
        self.url = urlparse.urljoin('file:', urllib.pathname2url(url))
        self.xaddr = xaddr
        # Create soap client
        if not ws_client:
            self.ws_client = Client(url=self.url, location=self.xaddr)
        else:
            self.ws_client = ws_client
            self.ws_client.set_options(location=self.xaddr)

        # Set cache duration and location
        if cache_duration is not None:
            self.ws_client.options.cache.setduration(days=cache_duration)
        if cache_location is not None:
            self.ws_client.options.cache.setlocation(cache_location)

        # Set soap header for authentication
        self.user = user
        self.passwd = passwd
        # Indicate wether password digest is needed
        self.encrypt = encrypt

        self.daemon = daemon

        self.set_wsse()

        # Method to create type instance of service method defined in WSDL
        self.create_type = self.ws_client.factory.create

    @safe_func
    def set_wsse(self, user=None, passwd=None):
        ''' Basic ws-security auth '''
        if user:
            self.user = user
        if passwd:
            self.passwd = passwd

        security = Security()

        if self.encrypt:
            token = UsernameDigestToken(self.user, self.passwd)
        else:
            token = UsernameToken(self.user, self.passwd)
            token.setnonce()
            token.setcreated()

        security.tokens.append(token)
        self.ws_client.set_options(wsse=security)

    @classmethod
    @safe_func
    def clone(cls, service, *args, **kwargs):
        clone_service = service.ws_client.clone()
        kwargs['ws_client'] = clone_service
        return ONVIFService(*args, **kwargs)

    @staticmethod
    @safe_func
    def to_dict(sudsobject):
        # Convert a WSDL Type instance into a dictionary
        if sudsobject is None:
            return { }
        elif isinstance(sudsobject, list):
            ret = [ ]
            for item in sudsobject:
                ret.append(Client.dict(item))
            return ret
        return Client.dict(sudsobject)

    def service_wrapper(self, func):
        @safe_func
        def wrapped(params=None, callback=None):
            def call(params=None, callback=None):
                # No params
                if params is None:
                    params = {}
                elif isinstance(params, InstanceType):
                    params = ONVIFService.to_dict(params)
                ret = func(**params)
                if callable(callback):
                    callback(ret)
                return ret

            if self.daemon:
                th = Thread(target=call, args=(params, callback))
                th.daemon = True
                th.start()
            else:
                return call(params, callback)
        return wrapped


    def __getattr__(self, name):
        '''
        Call the real onvif Service operations,
        See the offical wsdl definition for the
        APIs detail(API name, request parameters,
        response parameters, parameter types, etc...)
        '''
        builtin =  name.startswith('__') and name.endswith('__')
        if builtin:
            return self.__dict__[name]
        else:
            return self.service_wrapper(getattr(self.ws_client.service, name))

class ONVIFCamera(object):
    '''
    Python Implemention ONVIF compliant device
    This class integrates onvif services

    >>> from onvif import ONVIFCamera
    >>> mycam = ONVIFCamera('192.168.0.112', 80, 'admin',
    ...                 'foscam', '/home/linuxdev3/workspace/router/onvif/wsdl/')
    >>> mycam.devicemgmt.GetServices(False)
    >>> media_service = mycam.create_media_service()
    >>> ptz_service = mycam.create_ptz_service()
    # Get PTZ Configuration:
    >>> mycam.ptz.GetConfiguration()
    # Another way:
    >>> ptz_service.GetConfiguration()
    '''

    # Class-level variables
    services_template = {'devicemgmt': None, 'ptz': None, 'media': None,
                         'imaging': None, 'events': None, 'analytics': None }
    def __init__(self, host, port ,user, passwd, wsdl_dir,
                 cache_location=None, cache_duration=None,
                 encrypt=False, daemon=False):
        self.host = host
        self.port = int(port)
        self.user = user
        self.passwd = passwd
        self.wsdl_dir = wsdl_dir
        self.cache_location = cache_location
        self.cache_duration = cache_duration
        self.encrypt = encrypt
        self.daemon = daemon

        # Active service client container
        self.services = { }

        # Establish devicemgmt service first
        self.devicemgmt  = self.create_devicemgmt_service()

        # Get Capabilities for service creatation
        self.capabilities = self.devicemgmt.GetCapabilities()

        self.to_dict = ONVIFService.to_dict


    def update_url(self, host=None, port=None):
        changed = False
        if host and self.host != host:
            changed = True
            self.host = host
        if port and self.port != port:
            changed = True
            self.port = port

        if not changed:
            return

        self.devicemgmt = self.create_devicemgmt_service()
        self.capabilities = self.devicemgmt.GetCapabilities()

        for sname in self.services.keys():
            xaddr = getattr(self.capabilities, sname.capitalize).XAddr
            self.services[sname].ws_client.set_options(location=xaddr)

    def update_auth(self, user=None, passwd=None):
        changed = False
        if user and user != self.user:
            changed = True
            self.user = user
        if passwd and passwd != self.passwd:
            changed = True
            self.passwd = passwd

        if not changed:
            return

        for service in self.services.keys():
            self.services[service].set_wsse(user, passwd)

    def create_onvif_service(self, wsdl, xaddr, name):
        '''Create ONVIF service client'''

        name = name.lower()
        wsdl_file = os.path.join(self.wsdl_dir, wsdl)
        svt = self.services_template.get(name)
        # Has a template, clone from it. Easy and fast.
        if svt:
            service = ONVIFService.clone(svt, xaddr, self.user, self.passwd,
                                         wsdl_file, self.cache_location,
                                         self.cache_duration, self.encrypt,
                                         self.daemon)
        # No template, create new service from wsdl document.
        # A little time-comsuming
        else:
            service = ONVIFService(xaddr, self.user, self.passwd, wsdl_file,
                                self.cache_location, self.cache_duration,
                                self.encrypt, self.daemon)

        self.services[name] = service
        setattr(self, name, service)
        if not self.services_template.get(name):
            self.services_template[name] = service

        return service

    def get_service(self, name):
        service = getattr(self, name.lower(), None)
        if not service:
            return getattr(self, 'create_%s_service' % name.lower())()
        return service

    def create_devicemgmt_service(self):
        # The entry point for devicemgmt service is fixed to:
        xaddr = 'http://%s:%d/onvif/device_service' % (self.host, self.port)
        return self.create_onvif_service('devicemgmt.wsdl', xaddr, 'devicemgmt')

    def create_media_service(self):
        xaddr = self.capabilities.Media.XAddr
        return self.create_onvif_service('media.wsdl', xaddr, 'media')

    def create_ptz_service(self):
        xaddr = self.capabilities.PTZ.XAddr
        return self.create_onvif_service('ptz.wsdl', xaddr, 'ptz')

    def create_imaging_service(self):
        xaddr = self.capabilities.Imaging.XAddr
        return self.create_onvif_service('imaging.wsdl', xaddr, 'imaging')

    def create_events_service(self):
        xaddr = self.capabilities.Events.XAddr
        return self.create_onvif_service('events.wsdl', xaddr, 'events')

    def create_analytics_service(self):
        xaddr = self.capabilities.Analytics.XAddr
        return self.create_onvif_service('analytics.wsdl', xaddr, 'analytics')
