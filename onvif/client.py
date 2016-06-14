__version__ = '0.0.1'

import os.path
from types import InstanceType
import urlparse
import urllib
from threading import Thread, RLock

import logging
logger = logging.getLogger('onvif')
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.CRITICAL)

from suds.client import Client
from suds.wsse import Security, UsernameToken
from suds.cache import ObjectCache, NoCache
from suds_passworddigest.token import UsernameDigestToken
from suds.bindings import binding
binding.envns = ('SOAP-ENV', 'http://www.w3.org/2003/05/soap-envelope')

from onvif.exceptions import ONVIFError
from definition import SERVICES, NSMAP
from suds.sax.date import UTC
import datetime as dt
# Ensure methods to raise an ONVIFError Exception
# when some thing was wrong
def safe_func(func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            raise ONVIFError(err)
    return wrapped


class UsernameDigestTokenDtDiff(UsernameDigestToken):
    '''
    UsernameDigestToken class, with a time offset parameter that can be adjusted;
    This allows authentication on cameras without being time synchronized.
    Please note that using NTP on both end is the recommended solution, 
    this should only be used in "safe" environements.
    '''
    def __init__(self, user, passw, dt_diff=None) :
#        Old Style class ... sigh ...
        UsernameDigestToken.__init__(self, user, passw)
        self.dt_diff = dt_diff
        
    def setcreated(self, *args, **kwargs):
        dt_adjusted = None
        if self.dt_diff :
            dt_adjusted = (self.dt_diff + dt.datetime.utcnow())
        UsernameToken.setcreated(self, dt=dt_adjusted, *args, **kwargs)
        self.created = str(UTC(self.created))


class ONVIFService(object):
    '''
    Python Implemention for ONVIF Service.
    Services List:
        DeviceMgmt DeviceIO Event AnalyticsDevice Display Imaging Media
        PTZ Receiver RemoteDiscovery Recording Replay Search Extension

    >>> from onvif import ONVIFService
    >>> device_service = ONVIFService('http://192.168.0.112/onvif/device_service',
    ...                           'admin', 'foscam',
    ...                           '/etc/onvif/wsdl/devicemgmt.wsdl')
    >>> ret = device_service.GetHostname()
    >>> print ret.FromDHCP
    >>> print ret.Name
    >>> device_service.SetHostname(dict(Name='newhostname'))
    >>> ret = device_service.GetSystemDateAndTime()
    >>> print ret.DaylightSavings
    >>> print ret.TimeZone
    >>> dict_ret = device_service.to_dict(ret)
    >>> print dict_ret['TimeZone']

    There are two ways to pass parameter to services methods
    1. Dict
        params = {'Name': 'NewHostName'}
        device_service.SetHostname(params)
    2. Type Instance
        params = device_service.create_type('SetHostname')
        params.Hostname = 'NewHostName'
        device_service.SetHostname(params)
    '''

    @safe_func
    def __init__(self, xaddr, user, passwd, url,
                 cache_location='/tmp/suds', cache_duration=None,
                 encrypt=True, daemon=False, ws_client=None, no_cache=False, portType=None, dt_diff = None):

        if not os.path.isfile(url):
            raise ONVIFError('%s doesn`t exist!' % url)

        if no_cache:
            cache = NoCache()
        else:
            # Create cache object
            # NOTE: if cache_location is specified,
            # onvif must has the permission to access it.
            cache = ObjectCache(location=cache_location)
            # cache_duration: cache will expire in `cache_duration` days
            if cache_duration is not None:
                cache.setduration(days=cache_duration)


        # Convert pathname to url
        self.url = urlparse.urljoin('file:', urllib.pathname2url(url))
        self.xaddr = xaddr
        # Create soap client
        if not ws_client:
            self.ws_client = Client(url=self.url,
                                    location=self.xaddr,
                                    cache=cache,
                                    port=portType,
                                    headers={'Content-Type': 'application/soap+xml'})
        else:
            self.ws_client = ws_client
            self.ws_client.set_options(location=self.xaddr)

        # Set soap header for authentication
        self.user = user
        self.passwd = passwd
        # Indicate wether password digest is needed
        self.encrypt = encrypt

        self.daemon = daemon

        self.dt_diff = dt_diff
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
            token = UsernameDigestTokenDtDiff(self.user, self.passwd, dt_diff=self.dt_diff)
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
				
    adjust_time parameter allows authentication on cameras without being time synchronized.
    Please note that using NTP on both end is the recommended solution, 
    this should only be used in "safe" environements.
    Also, this cannot be used on AXIS camera, as every request is authenticated, contrary to ONVIF standard		

    >>> from onvif import ONVIFCamera
    >>> mycam = ONVIFCamera('192.168.0.112', 80, 'admin', '12345')
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
    use_services_template = {'devicemgmt': True, 'ptz': True, 'media': True,
                         'imaging': True, 'events': True, 'analytics': True }
    def __init__(self, host, port ,user, passwd, wsdl_dir=os.path.join(os.path.dirname(os.path.dirname(__file__)), "wsdl"),
                 cache_location=None, cache_duration=None,
                 encrypt=True, daemon=False, no_cache=False, adjust_time=False):
        self.host = host
        self.port = int(port)
        self.user = user
        self.passwd = passwd
        self.wsdl_dir = wsdl_dir
        self.cache_location = cache_location
        self.cache_duration = cache_duration
        self.encrypt = encrypt
        self.daemon = daemon
        self.no_cache = no_cache
        self.adjust_time = adjust_time

        # Active service client container
        self.services = { }
        self.services_lock = RLock()

        # Set xaddrs
        self.update_xaddrs()

        self.to_dict = ONVIFService.to_dict

    def update_xaddrs(self):
        # Establish devicemgmt service first
        self.dt_diff = None
        self.devicemgmt  = self.create_devicemgmt_service()
        if self.adjust_time :
            cdate = self.devicemgmt.GetSystemDateAndTime().UTCDateTime
            cam_date = dt.datetime(cdate.Date.Year, cdate.Date.Month, cdate.Date.Day, cdate.Time.Hour, cdate.Time.Minute, cdate.Time.Second)
            self.dt_diff = cam_date - dt.datetime.utcnow()
            self.devicemgmt.dt_diff = self.dt_diff
            self.devicemgmt.set_wsse()
        # Get XAddr of services on the device
        self.xaddrs = { }
        capabilities = self.devicemgmt.GetCapabilities({'Category': 'All'})
        for name, capability in capabilities:
            try:
                if name.lower() in SERVICES:
                    ns = SERVICES[name.lower()]['ns']
                    self.xaddrs[ns] = capability['XAddr']
            except Exception:
                logger.exception('Unexcept service type')

        with self.services_lock:
            try:
                self.event = self.create_events_service()
                self.xaddrs['http://www.onvif.org/ver10/events/wsdl/PullPointSubscription'] = self.event.CreatePullPointSubscription().SubscriptionReference.Address
            except:
                pass                


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

        with self.services_lock:
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

        with self.services_lock:
            for service in self.services.keys():
                self.services[service].set_wsse(user, passwd)

    def get_service(self, name, create=True):
        service = None
        service = getattr(self, name.lower(), None)
        if not service and create:
            return getattr(self, 'create_%s_service' % name.lower())()
        return service

    def get_definition(self, name):
        '''Returns xaddr and wsdl of specified service'''
        # Check if the service is supported
        if name not in SERVICES:
            raise ONVIFError('Unknown service %s' % name)
        wsdl_file = SERVICES[name]['wsdl']
        ns = SERVICES[name]['ns']

        wsdlpath = os.path.join(self.wsdl_dir, wsdl_file)
        if not os.path.isfile(wsdlpath):
            raise ONVIFError('No such file: %s' % wsdlpath)

        # XAddr for devicemgmt is fixed:
        if name == 'devicemgmt':
            xaddr = 'http://%s:%s/onvif/device_service' % (self.host, self.port)
            return xaddr, wsdlpath

        # Get other XAddr
        xaddr = self.xaddrs.get(ns)
        if not xaddr:
            raise ONVIFError('Device doesn`t support service: %s' % name)

        return xaddr, wsdlpath

    def create_onvif_service(self, name, from_template=True, portType=None):
        '''Create ONVIF service client'''

        name = name.lower()
        xaddr, wsdl_file = self.get_definition(name)

        with self.services_lock:
            svt = self.services_template.get(name)
            # Has a template, clone from it. Faster.
            if svt and from_template and self.use_services_template.get(name):
                service = ONVIFService.clone(svt, xaddr, self.user,
                                             self.passwd, wsdl_file,
                                             self.cache_location,
                                             self.cache_duration,
                                             self.encrypt,
                                             self.daemon,
                                             no_cache=self.no_cache, portType=portType, dt_diff=self.dt_diff)
            # No template, create new service from wsdl document.
            # A little time-comsuming
            else:
                service = ONVIFService(xaddr, self.user, self.passwd,
                                       wsdl_file, self.cache_location,
                                       self.cache_duration, self.encrypt,
                                       self.daemon, no_cache=self.no_cache, portType=portType, dt_diff=self.dt_diff)

            self.services[name] = service

            setattr(self, name, service)
            if not self.services_template.get(name):
                self.services_template[name] = service

        return service

    def create_devicemgmt_service(self, from_template=True):
        # The entry point for devicemgmt service is fixed.
        return self.create_onvif_service('devicemgmt', from_template)

    def create_media_service(self, from_template=True):
        return self.create_onvif_service('media', from_template)

    def create_ptz_service(self, from_template=True):
        return self.create_onvif_service('ptz', from_template)

    def create_imaging_service(self, from_template=True):
        return self.create_onvif_service('imaging', from_template)

    def create_deviceio_service(self, from_template=True):
        return self.create_onvif_service('deviceio', from_template)

    def create_events_service(self, from_template=True):
        return self.create_onvif_service('events', from_template)

    def create_analytics_service(self, from_template=True):
        return self.create_onvif_service('analytics', from_template)

    def create_recording_service(self, from_template=True):
        return self.create_onvif_service('recording', from_template)

    def create_search_service(self, from_template=True):
        return self.create_onvif_service('search', from_template)

    def create_replay_service(self, from_template=True):
        return self.create_onvif_service('replay', from_template)

    def create_pullpoint_service(self, from_template=True):
        return self.create_onvif_service('pullpoint', from_template, portType='PullPointSubscription')

    def create_receiver_service(self, from_template=True):
        return self.create_onvif_service('receiver', from_template)
