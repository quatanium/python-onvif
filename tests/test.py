#!/usr/bin/python
#-*-coding=utf-8

import unittest

from suds import WebFault

from onvif import ONVIFCamera, ONVIFError

CAM_HOST      = '192.168.0.112'
CAM_PORT      = 80
CAM_USER      = 'admin'
CAM_PASS      = '12345'
WSDL_URL      = '/home/linuxdev3/workspace/python-onvif/wsdl/'

DEBUG = False

def log(ret):
    if DEBUG:
        print ret

class TestDevice(unittest.TestCase):

    # Class level cam. Run this test more efficiently..
    cam = ONVIFCamera(CAM_HOST, CAM_PORT, CAM_USER, CAM_PASS, WSDL_URL, encrypt=True)

    # ***************** Test Capabilities ***************************
    def test_GetWsdlUrl(self):
        ret = self.cam.devicemgmt.GetWsdlUrl()

    def test_GetServices(self):
        '''
        Returns a cllection of the devices
        services and possibly their available capabilities
        '''
        params = {'IncludeCapability': True }
        ret = self.cam.devicemgmt.GetServices(params)
        params = self.cam.devicemgmt.create_type('GetServices')
        params.IncludeCapability=False
        ret = self.cam.devicemgmt.GetServices(params)

    def test_GetServiceCapabilities(self):
        '''Returns the capabilities of the devce service.'''
        ret = self.cam.devicemgmt.GetServiceCapabilities()
        ret.Network._IPFilter

    def test_GetCapabilities(self):
        '''
        Probides a backward compatible interface for the base capabilities.
        '''
        categorys = ['PTZ', 'Media', 'Imaging',
                     'Device', 'Analytics', 'Events']
        ret = self.cam.devicemgmt.GetCapabilities()
        for category in categorys:
            ret = self.cam.devicemgmt.GetCapabilities({'Category': category})

        with self.assertRaises(ONVIFError):
            self.cam.devicemgmt.GetCapabilities({'Category': 'unknown'})

    # *************** Test Network *********************************
    def test_GetHostname(self):
        ''' Get the hostname from a device '''
        self.cam.devicemgmt.GetHostname()

    def test_SetHostname(self):
        '''
        Set the hostname on a device
        A device shall accept strings formated according to
        RFC 1123 section 2.1 or alternatively to RFC 952,
        other string shall be considered as invalid strings
        '''
        pre_host_name = self.cam.devicemgmt.GetHostname()

        self.cam.devicemgmt.SetHostname({'Name':'testHostName'})
        self.assertEqual(self.cam.devicemgmt.GetHostname().Name, 'testHostName')

        self.cam.devicemgmt.SetHostname(pre_host_name)

    def test_SetHostnameFromDHCP(self):
        ''' Controls whether the hostname shall be retrieved from DHCP '''
        ret = self.cam.devicemgmt.SetHostnameFromDHCP(dict(FromDHCP=False))
        self.assertTrue(isinstance(ret, bool))

    def test_GetDNS(self):
        ''' Gets the DNS setting from a device '''
        ret = self.cam.devicemgmt.GetDNS()
        self.assertTrue(hasattr(ret, 'FromDHCP'))
        if ret.FromDHCP == False:
            log(ret.DNSManual[0].Type)
            log(ret.DNSManual[0].IPv4Address)

    def test_SetDNS(self):
        ''' Set the DNS settings on a device '''
        ret = self.cam.devicemgmt.SetDNS(dict(FromDHCP=False))

    def test_GetNTP(self):
        ''' Get the NTP settings from a device '''
        ret = self.cam.devicemgmt.GetNTP()
        if ret.FromDHCP == False:
            self.assertTrue(hasattr(ret, 'NTPManual'))
            log(ret.NTPManual)

    def test_SetNTP(self):
        '''Set the NTP setting'''
        ret = self.cam.devicemgmt.SetNTP(dict(FromDHCP=False))

    def test_GetDynamicDNS(self):
        '''Get the dynamic DNS setting'''
        ret = self.cam.devicemgmt.GetDynamicDNS()
        log(ret)

    def test_SetDynamicDNS(self):
        ''' Set the dynamic DNS settings on a device '''
        ret = self.cam.devicemgmt.GetDynamicDNS()
        ret = self.cam.devicemgmt.SetDynamicDNS(dict(Type=ret.Type, Name="random"))

if __name__ == '__main__':
    unittest.main()
