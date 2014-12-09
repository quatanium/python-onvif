#!/usr/bin/python
'''ONVIF Client Command Line Interface'''

import argparse
from cmd import Cmd
from ast import literal_eval
from json import loads, dumps

from suds.sax.text import Text
from onvif import ONVIFCamera, ONVIFService, ONVIFError

SUPPORTED_SERVICE = ('Device', 'PTZ', 'Media')


class ONVIFCLI(Cmd):
    prompt = 'ONVIF >>> '
    client = None
    cmd_parser = None

    def setup(self, args):
        ''' `args`: Instance of `argparse.ArgumentParser` '''
        # Create onvif camera client
        self.client = ONVIFCamera(args.host, args.port,
                                  args.user, args.password,
                                  args.wsdl, encrypt=args.encrypt)


        # Create cmd argument parser
        self.create_cmd_parser()

    def create_cmd_parser(self):
        cmd_parser = argparse.ArgumentParser()
        cmd_parser.add_argument('service')
        cmd_parser.add_argument('operation')
        cmd_parser.add_argument('params', default='{}', nargs='?')
        self.cmd_parser = cmd_parser

    def do_cmd(self, line):

        args = self.cmd_parser.parse_args(line.split())

        # Get ONVIF service
        service = self.client.get_service(args.service)

        # Actually execute the command and get the response
        args.params = dict(literal_eval(args.params))
        response = getattr(service, args.operation)(args.params)

        if isinstance(response, Text):
            print True, response
        try:
            print True, ONVIFService.to_dict(response)
        except ONVIFError:
            return False, dumps({})

    def do_EOF(self, line):
        return 'Good Bye'

    def emptyline(self):
        return ''

def create_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    # Dealwith dependency for service, operation and params
    parser.add_argument('service', nargs='?',
                        help='Service defined by ONVIF WSDL document')
    parser.add_argument('operation', nargs='?', default='',
                        help='Operation to be execute defined'
                                          ' by ONVIF WSDL document')
    parser.add_argument('params', default='', nargs='?',
                        help='JSON format params passed to the operation.'
                             'E.g., "{"Name": "NewHostName"}"')
    parser.add_argument('--host',  required=True,
                        help='ONVIF camera host, e.g. 192.168.2.123, '
                             'www.example.com')
    parser.add_argument('--port', default=80, type=int, help='Port number for camera, default: 80')
    parser.add_argument('-u', '--user', required=True,
                        help='Username for authentication')
    parser.add_argument('-a', '--password', required=True,
                        help='Password for authentication')
    parser.add_argument('-w', '--wsdl',  help='directory to store ONVIF WSDL documents')
    parser.add_argument('-e', '--encrypt', action='store_true',
                        help='Encrypt password or not')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase output verbosity')
    parser.add_argument('--cache-location', dest='cache_location', default='/tmp/onvif/',
                        help='location to cache suds objects, default to /tmp/onvif/')
    parser.add_argument('--cache-duration', dest='cache_duration',
                        help='how long will the cache be exist')

    return parser

def main():
    INTRO = __doc__

    # Create argument parser
    parser = create_parser()
    args = parser.parse_args()
    # Also need parse configuration file.

    # Interactive command loop
    cli = ONVIFCLI(INTRO)
    cli.setup(args)
    if args.service:
        cmd = ' '.join(['cmd', args.service, args.operation, args.params])
        cli.onecmd(cmd)
    # Execute command specified and exit
    else:
        cli.cmdloop()

if __name__ == '__main__':
    main()
