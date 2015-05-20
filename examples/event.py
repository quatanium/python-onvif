# -*- coding: utf-8 -*-
import os.path
from onvif import ONVIFCamera
__author__ = 'vahid'


this_dir = os.path.abspath(os.path.dirname(__file__))
wsdl_dir = os.path.abspath(os.path.join(this_dir, '../wsdl'))


if __name__ == '__main__':
    mycam = ONVIFCamera('192.168.1.10', 8899, 'admin', 'admin', wsdl_dir) #, no_cache=True)
    event_service = mycam.create_events_service()
    pp = event_service.CreatePullPointSubscription()