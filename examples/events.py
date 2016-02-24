# -*- coding: utf-8 -*-
from onvif import ONVIFCamera
__author__ = 'vahid'


if __name__ == '__main__':
    mycam = ONVIFCamera('192.168.1.10', 8899, 'admin', 'admin') #, no_cache=True)
    event_service = mycam.create_events_service()
    print(event_service.GetEventProperties())
    
    pullpoint = mycam.create_pullpoint_service()
    req = pullpoint.create_type('PullMessages')
    req.MessageLimit=100
    print(pullpoint.PullMessages(req))
