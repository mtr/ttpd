#! /usr/bin/python
# -*- coding: latin-1 -*-
# $Id$
"""
Module to ease the maintainance of option parsing for the two
programs ttpd and ttpc.

Copyright (C) 2004 by Martin Thorsen Ranang
"""

__version__ = "$Rev$"
__author__ = "Martin Thorsen Ranang"

import sys
import os

import LogHandler

basename = os.path.basename(sys.argv[0])

common_options = [
    
    (['-a', '--ip-address'],
     {'dest': 'ip_address',
      'default': '0',
      'metavar': 'ADDRESS',
      'help': 'the ADDRESS of the interface on which to listen for ' \
      'connections from clients; if ADDRESS is 0 (the default) the ' \
      'server will listen on all available network interfaces'}),
    
    (['-p', '--port'],
     {'dest': 'port',
      'type': 'int',
      'default': 2004,
      'metavar': 'PORT',
      'help': 'listen for connections from clients on PORT; ' \
      'the default is %(default)d'}),

    (['-A', '--remote-ip-address'],
     {'dest': 'remote_ip_address',
      'default': 'localhost',
      'metavar': 'ADDRESS',
      'help': "the ADDRESS of the interface on which to send outgoing " \
      "communication; default is '%(default)s'"}),
        
    (['-P', '--remote-port'],
     {'dest': 'remote_port',
      'type': 'int',
      'default': 2005,
      'metavar': 'PORT',
      'help': 'the remote PORT; the default is %(default)d'}),
    
    (['-q', '--socket-queue-size'],
     {'dest': 'socket_queue_size',
      'type': 'int',
      'default': 5,
      'metavar': 'SIZE',
      'help': 'the SIZE of the socket queue; the default is %(default)d'}),
    
    (['-Q', '--high-load-limit'],
     {'dest': 'high_load_limit',
      'type': 'int',
      'default': 50,
      'metavar': 'THREADS',
      'help': 'maximum number of concurrently running THREADS; ' \
      'the default is %(default)d'}),
    
    (['-L', '--log-level'],
     {'dest': 'log_level',
      'default': 'info',
      'metavar': 'LEVEL',
      'help': "the filter LEVEL used when logging; possible values are " \
      "%(log_levels)s; " \
      "the default is '%(default)s'" % \
      {'log_levels':
       ' < '.join(["'%s'" % x for x in LogHandler.get_log_levels()]),
       'default': '%(default)s'}}),
    
    (['-f', '--log-file'],
     {'dest': 'log_file',
      'default': '%s.log' % basename,
      'metavar': 'FILE',
      'help': 'store the log in FILE; the default is \'%(default)s\''}),

    ]

ttpd_options = [
    
    (['-t', '--without-tad'],
     {'dest': 'run_tad',
      'default': True,
      'action': 'store_false',
      'help': 'don\'t start the TUC Alert Daemon (TAD)'}),
    
    (['-T', '--without-tuc'],
     {'dest': 'run_tuc',
      'default': True,
      'action': 'store_false',
      'help': 'don\'t start the TUC processes'}),
    
    (['-n', '--tuc-threads'],
     {'dest': 'tuc_pool_size',
      'type': 'int',
      'default': 3,
      'metavar': 'NUMBER',
      'help': 'start NUMBER concurrent TUC processes; the default is ' \
      '%(default)d'}),
    
    (['-s', '--path-to-tuc'],
     {'dest': 'tuc_command',
      'default': './busestuc.sav',
      'metavar': 'COMMAND',
      'help': 'run COMMAND as TUC subprocess; the default is %(default)s'}),
    
    (['-d', '--no-daemon'],
     {'dest': 'daemon',
      'default': True,
      'action': 'store_false',
      'help': 'don\'t run as a daemon process'}),
    
    ]

ttpdctl_options = [
    (['-o', '--old-log-file'],
     {'dest': 'old_log_file',
      'default': None,
      'metavar': 'FILE',
      'help': 'location of the old log FILE, used to ' \
      'retrieve the PID of the current process, when ' \
      'restarting after a file has been moved ' \
      '(e.g., log rotated)'}),
    (['-e', '--executable'],
     {'dest': 'executable',
      'default': 'ttpd',
      'metavar': 'EXECUTABLE',
      'help': 'location of the ttpd EXECUTABLE; ' \
      'the default is %(default)s'})]

ttpc_options = [
    
    (['-I', '--transaction-id'],
     {'dest': 'trans_id',
      'default': 'LINGSMSIN',
      'metavar': 'TRANS_ID',
      'help': "the TRANS_ID to use when communicating with " \
      "a remote server.  The default is '%(default)s'."}),
    
    (['-l', '--listen-mode'],
     {'dest': 'listen_mode',
      'default': False,
      'action': 'store_true', 
      'help': 'listen for inbound connections'}),
    
    (['-t', '--test'],
     {'dest': 'test_mode',
      'default': False,
      'action': 'store_true', 
      'help': 'run in looping test-mode'}),
    
    (['-T', '--phone-number'],
     {'dest': 'phone_number',
      'default': None, 
      'metavar': 'PHONE',
      'help': "the number that the message supposedly was sent from; " \
      "the deault is '%(default)s'"}),

    (['-F', '--fake-outgoing'],
     {'dest': 'fake_outgoing',
      'default': False,
      'action': 'store_true',
      'help': "fake an outgoing message from the server"}),

    (['-i', '--input-file'],
     {'dest': 'input_file',
      'default': None,
      'metavar': 'FILE',
      'help': 'read input from FILE'}),
    
    (['-w', '--web'],
     {'dest': 'web',
      'default': False,
      'action': 'store_true', 
      'help': 'generate output suitable for the Web; this implicates ' \
      '--transaction-id=WEB'}),
    
    (['-W', '--show-technical'],
     {'dest': 'show_technical',
      'default': False,
      'action': 'store_true',
      'help': 'show technical information (semantics)'}),
    
    ]


def set_default(options, flag, value):
    
    v = [o for o in options if o[0][1] == flag][0]
    v[1]['default'] = value
    
    return v

def update_help(option):
    
    if 'default' in option:
        value = option['default']
        option['help'] = option['help'] % {'default': value}


class PlaceHolder:

    """ Only kept here to create the domentation for this module. """
    
def main():
    
    """ Module mainline (for standalone execution). """
    
    import optparse
    
    parser = optparse.OptionParser(version = '%%prog test')
    
    options = common_options + ttpc_options
    
    set_default(options, '--port', 2005)
    
    for option, description in options:
        update_help(description)
        parser.add_option(*option, **description)
        
    options, args = parser.parse_args()
    
    return


if __name__ == "__main__":
    main()
