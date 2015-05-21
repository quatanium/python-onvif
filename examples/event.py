# -*- coding: utf-8 -*-
import os.path
from onvif import ONVIFCamera
__author__ = 'vahid'


this_dir = os.path.abspath(os.path.dirname(__file__))
wsdl_dir = os.path.abspath(os.path.join(this_dir, '../wsdl'))

def get_event_srv():
    mycam = ONVIFCamera('192.168.1.10', 8899, 'admin', 'admin', wsdl_dir) #, no_cache=True)
    #print mycam.devicemgmt.GetServices()
    event_service = mycam.create_events_service()
    return event_service


if __name__ == '__main__':
    e_service = get_event_srv()
    pp = e_service.GetEventProperties()
