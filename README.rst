python-onvif
============

ONVIF Client Implementation in Python

Dependences
------------
suds >= 0.4

suds-passworddigest

Install onvif
-------------
**From source**

You should clone this repository and run the setup.py::

    cd python-onvif && python setup.py install

**From pypi**

::

    pip install onvif

Getting Started
---------------

initialize an ONVIFCamera instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    from onvif import ONVIFCamera
    mycam = ONVIFCamera('192.168.0.2', 80, 'user', 'passwd', '/etc/onvif/wsdl/')

Now, we get an ONVIFCamera instance. By default, a devicemgmt service is available if everything is OK.

So, all of the operations defined in the WSDL document::

/etc/onvif/wsdl/devicemgmt.wsdl

are available.

Get infomation from your camera
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    # Get Hostname
    resp = mycam.devicemgmt.GetHostname()
    print 'My camera`s hostname : ' + str(resp.Hostname)

    # Get system date and time
    dt = mycam.devicemgmt.GetSystemDateAndTime()
    tz = dt.TimeZone
    year = dt.UTCDateTime.Date.Year
    hour = dt.UTCDateTime.Time.Hour

Configure(Control) your camera
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To configure your camera, parameters must be passed.  There are two ways
to pass parameter to services methods.

**Dict**

This way is very simple::

    params = {'Name': 'NewHostName'}
    device_service.SetHostname(params)

**Type Instance**

This way is simple and also recommended. For type instance will raise an
exception if you set an invalid(or nonexistent) parameter.

::

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

Create other service
~~~~~~~~~~~~~~~~~~~~
ONVIF protocol has defined many services.
You can find all the services and operations `here <http://www.onvif.org/onvif/ver20/util/operationIndex.html>`_.
ONVIFCamera has support methods to create new services::

    # Create ptz service
    ptz_service = mycam.create_ptz_service()
    # Get ptz configuration
    mycam.ptz.GetConfiguration()
    # Another way:
    ptz_service.GetConfiguration()

Or create unofficial service::

    xaddr = 'http://192.168.0.3:8888/onvif/yourservice'
    yourservice = mycam.create_onvif_service('service.wsdl', xaddr, 'yourservice')
    yourservice.SomeOperation()
    # Be equivalent to
    mycam.yourservice.SomeOperation()

ONVIF CLI
---------
python-onvif also provide command line interactive interface: onvif-cli.
onvif-cli will be installed automatically.

single command example
~~~~~~~~~~~~~~~~~~~~~~

::

    $ onvif-cli devicemgmt GetHostname --user 'admin' --password '12345' --host '192.168.0.112' --port 80
    Nethostname
    $ onvif-cli devicemgmt SetHostname "{'Name': 'NewerHostname'}" --user 'admin' --password '12345' --host '192.168.0.112' --port 80

Interactive mode
~~~~~~~~~~~~~~~~

::

    $ onvif-cli -u 'admin' -a '12345' --host '192.168.0.112' --port 80 --wsdl /etc/onvif/wsdl/
    ONVIF >>> cmd
    analytics   devicemgmt  events      imaging     media       ptz
    ONVIF >>> cmd devicemgmt GetWsdlUrl
    True: http://www.onvif.org/
    ONVIF >>> cmd devicemgmt SetHostname {'Name': 'NewHostname'}
    ONVIF >>> cmd devicemgmt GetHostname
    True: {'Name': 'NewHostName'}
    ONVIF >>> cmd devicemgmt SomeOperation
    False: No Operation: SomeOperation

NOTE: Completion are supported for interactive mode.

In Batch
~~~~~~~~

::

    $ vim batchcmds
    $ cat batchcmds
    cmd devicemgmt GetWsdlUrl
    cmd devicemgmt GetServices {'Include': False}
    cmd devicemgmt SetHostname {'Name': 'NewHostname', 'FromDHCP': True}
    $ onvif-cli --host 192.168.0.112 --u admin -a 12345 -e -w /etc/onvif/wsdl/ < batchcmds
    # result in order...

Reference
---------

* `ONVIF Offical Website <http://www.onvif.com>`_

* `Operations Index <http://www.onvif.org/onvif/ver20/util/operationIndex.html>`_

* `ONVIF Develop Documents <http://www.onvif.org/specs/DocMap-2.4.2.html>`_

* `Foscam Python Lib <http://github.com/quatanium/foscam-python-lib>`_
