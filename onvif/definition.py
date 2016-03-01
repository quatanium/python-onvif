SERVICES = {
        # Name                              namespace                           wsdl file
        'devicemgmt': {'ns': 'http://www.onvif.org/ver10/device/wsdl',    'wsdl': 'devicemgmt.wsdl'},
        'media'     : {'ns': 'http://www.onvif.org/ver10/media/wsdl',     'wsdl': 'media.wsdl' },
        'ptz'       : {'ns': 'http://www.onvif.org/ver20/ptz/wsdl',       'wsdl': 'ptz.wsdl'},
        'imaging'   : {'ns': 'http://www.onvif.org/ver20/imaging/wsdl',   'wsdl': 'imaging.wsdl'},
        'deviceio'  : {'ns': 'http://www.onvif.org/ver10/deviceIO/wsdl',  'wsdl': 'deviceio.wsdl'},
        'events'    : {'ns': 'http://www.onvif.org/ver10/events/wsdl',    'wsdl': 'events.wsdl'},
        'pullpoint' : {'ns': 'http://www.onvif.org/ver10/events/wsdl/PullPointSubscription',    'wsdl': 'events.wsdl'},
        'analytics' : {'ns': 'http://www.onvif.org/ver20/analytics/wsdl', 'wsdl': 'analytics.wsdl'},
        'recording' : {'ns': 'http://www.onvif.org/ver10/recording/wsdl', 'wsdl': 'recording.wsdl'},
        'search'    : {'ns': 'http://www.onvif.org/ver10/search/wsdl',    'wsdl': 'search.wsdl'},
        'replay'    : {'ns': 'http://www.onvif.org/ver10/replay/wsdl',    'wsdl': 'replay.wsdl'},
        'receiver'  : {'ns': 'http://www.onvif.org/ver10/receiver/wsdl',  'wsdl': 'receiver.wsdl'},
        }


NSMAP = { }
for name, item in SERVICES.items():
    NSMAP[item['ns']] = name
