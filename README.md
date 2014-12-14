python-onvif
============

ONVIF Client Implementation in Python

## Install onvif
### Dependences
suds >= 0.4
suds-passworddigest

### From source
    You should clone this repository and run the setup.py.
```
cd python-onvif && python setup.py
```

### From pypi(TODO)
```
sudo pip install onvif
```

## Getting Started
To initialize an ONVIFCamera instance:

```python
from onvif import ONVIFCamera
mycam = ONVIFCamera('192.168.0.2', 80, 'user', 'passwd', '/etc/onvif/wsdl/')
```
Now, we get an ONVIFCamera instance. By default, a devicemgmt service is available if everything is OK.
So, all of the operations defined in the WSDL document:
    /etc/onvif/wsdl/devicemgmt.wsdl
are available.

### Get infomation from your camera

```python
    # Get Hostname
    resp = mycam.devicemgmt.GetHostname()
    print 'My camera`s hostname : ' + str(resp.Hostname)

    # Get system date and time
    dt = mycam.devicemgmt.GetSystemDateAndTime()
    tz = dt.TimeZone
    year = dt.UTCDateTime.Date.Year
    hour = dt.UTCDateTime.Time.Hour
```

### Configure(Control) your camera
    To configure your camera, parameters must be passed.  There are two ways
to pass parameter to services methods:
1. Dict
    This way is very simple.

```
    params = {'Name': 'NewHostName'}
    device_service.SetHostname(params)
```
2. Type Instance
    This way is simple and also recommended. For type instance will raise an
exception if you set an invalid(or nonexistent) parameter.

```
    params = mycam.devicemgmt.create_type('SetHostname')
    params.Hostname = 'NewHostName'
    mycam.devicemgmt.SetHostname(params)
    
    time_params = mycam.devicemgmt.create_type('SetSystemDateAndTime')
    time_params.DateTimeType = 'Manual'
    time_params.DaylightSavings = True
    time_params.TimeZone = 'CST-8:00:00'
    time_params.UTCDateTime.Date.Year = 2014
    time_params.UTCDateTime.Date.Month = 12
    time_params.UTCDateTime.Date.Day = 3
    time_params.UTCDateTime.Time.Hour = 9
    time_params.UTCDateTime.Time.Minute = 36
    time_params.UTCDateTime.Time.Second = 11
    mycam.devicemgmt.SetSystemDateAndTime(time_params)
```

### Create other service
    ONVIF protocol has defined many services.
You can find all the services and operations [here](http://www.onvif.org/onvif/ver20/util/operationIndex.html).
ONVIFCamera has support methods to create new services:

```
# Create ptz service
ptz_service = mycam.create_ptz_service()
# Get ptz configuration
mycam.ptz.GetConfiguration()
# Another way:
ptz_service.GetConfiguration()
```

Or create unofficial service:

```
xaddr = 'http://192.168.0.3:8888/onvif/yourservice'
yourservice = mycam.create_onvif_service('service.wsdl', xaddr, 'yourservice')
yourservice.SomeOperation()
# Be equivalent to
mycam.yourservice.SomeOperation()

```

## Reference
[1]. http://www.onvif.com "ONVIF offical website"
[2]. http://www.onvif.org/onvif/ver20/util/operationIndex.html "Operations Index"
[3]. http://www.onvif.org/specs/DocMap-2.4.2.html "ONVIF Develop Documents"
[4]. http://github.com/quatanium/foscam-python-lib "Foscam lib"
