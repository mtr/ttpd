#! /usr/bin/python
# -*- coding: latin-1 -*-
# $Id$
"""
TUC Transfer Protocol socket server implementations.

These servers are designed to be used with connection handlers (see
the Handler module) supplied as an argument to the constructor.

Copyright (C) 2004 by Martin Thorsen Ranang
"""

__version__ = "$Rev$"
__author__ = "Martin Thorsen Ranang"

import SocketServer
import logging
import os
import Queue
import signal
import sys
import xml.sax

import EncapsulateTUC                   # For request-type constants.
import LogHandler
import Message
import TUCThread
import tad

# FIXME:  Actually send things to remote server (don't use netcat).

class BaseThreadingTCPServer(SocketServer.ThreadingTCPServer):

    """ A Minimal Threading TCP TTP Server.

    Servers instatiated from this class will be well suited for
    creating simple protocol testing interfaces. """
    
    # Allow the server to reuse its address (no need to wait for a
    # timeout).
    
    allow_reuse_address = True
    request_queue_size = 0
    
    # Set the log channel of this server.
    
    log_channel = 'base'
    server_name = 'Base TPP server'
    
    def __init__(self, server_address, RequestHandlerClass,
                 log_filename, log_level = logging.DEBUG,
                 request_queue_size = 5):
        
        # Set the request_queue_size.  If it takes a long time to
        # process a single request, any requests that arrive while the
        # server is busy are placed into a queue, up to
        # request_queue_size requests.
        
        self.request_queue_size = request_queue_size
        
        self.log_filename = log_filename
        self.log_level = log_level
        
        # Initialize the base class.
        
        SocketServer.ThreadingTCPServer.__init__(self, server_address,
                                                 RequestHandlerClass)
        
        # Initialize the logging facilities.
        
        self.log_init()

    def handle_error(self, request, client_address):

        """ Handle an error gracefully. """

        self.log.exception('Exception occurred during processing ' \
                           'of request from %s (port %d).',
                           client_address[0], client_address[1])
        
    def log_init(self):

        """ Intialize logging facilities and log some useful startup
        information. """
        
        self.log = logging.getLogger(self.log_channel)
        self.handler = LogHandler.LogHandler(self.log_filename)
        self.log.addHandler(self.handler)
        self.log.setLevel(self.log_level)
        
        self.log.info('%s, version %s, initialized.' % (self.server_name,
                                                        __version__))
        self.log.info('PID = %d, log_level = %s' %
                      (os.getpid(),
                       logging.getLevelName(self.log.getEffectiveLevel())))
        
        interface, port = self.server_address
        if interface == '0':
            interface = '"ANY"'

        self.log.info('Listening to interface %s on port %s.' %
                      (interface, port))
        
    def reopen(self):
        
        """ Reopen all (log) files.  This is necessary for rotating
        logs without restarting the whole daemon. """
        
        self.log.info('Reopening log files...')
        self.handler.reopen()
        self.log.info('... done reopening log files.')
        
    def hangup(self, signum, frame):
        
        """ Handler for the HUP signal (as receive from a 'kill -HUP
        <pid>' command. """

        # Reopen all files (used for logging).
        
        self.reopen()
        
    def shutdown(self, signum, frame):

        """ Stop the necessary sub-processes.  And shutdown in a
        controlled manner. """
        
        # Ignore SIGHUP, SIGINT and SIGTERM signals during shutdown.
        
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        
        self.log.info('Shutting down.')
        
        self.__shutdown = True
        sys.exit(0)
        

class ThreadingTCPServer(BaseThreadingTCPServer):

    """ A Full Threading TCP TTP Server.

    In addition to the features of servers instantiated from its base
    class, servers of this kind features support for running a pool of
    TUC sub-processes and an instance of the TUC Alert Daemon
    (TAD). """
    
    log_channel = 'ttpd'
    server_name = 'TTPD'
    
    def __init__(self, server_address, RequestHandlerClass,
                 log_filename, log_level, request_queue_size,
                 tuc_pool_size, tuc_command, run_tad,
                 remote_server_address):
        
        # Initialize base class.
        
        BaseThreadingTCPServer.__init__(self, server_address,
                                           RequestHandlerClass,
                                           log_filename, log_level,
                                           request_queue_size)

        # Store the remote server address.
        
        self.remote_server_address = remote_server_address
        
        self.log.info('Remote server is %s:%d' %
                      (self.remote_server_address))
        
        # Add a number of threads to the server TUC-thread pool.
        # Each thread controls an external TUC process that runs
        # in the background.
        
        self.tuc_pool_size = tuc_pool_size
        self.tuc_command = tuc_command
        
        logger = logging.getLogger('%s.etp' % self.log_channel)
        self.tuc_pool = TUCThread.TUCThreadPool(self.tuc_pool_size,
                                                self.tuc_command,
                                                TUCThread.TUCThread,
                                                logger)
        
        # Unless specified otherwise by the user, start a TUC
        # alert daemon.
        
        if run_tad:
            self.tad = tad.TUCAlertDaemon(self.remote_server_address,
                                          '%s.tad' % (self.log_channel),
                                          self.log_filename)
            self.tad.run()
        else:
            self.tad = None
        
    def store_tad_state(self, signum, frame):
        
        """ Signal handler to take care of storing the TAD scheduler
        state.
        
        To only perform a scheduler state store, send a USR1 signal to
        the parent process (as in 'kill -USR1 <pid of ttpd>')."""
        
        self.tad.store()
        
    def hangup(self, signum, frame):
        
        """ Handler for the HUP signal (as receive from a 'kill -HUP
        <pid>' command. """
        
        BaseThreadingTCPServer.hangup(self, signum, frame)
        
        if self.tad:
            self.store_tad_state(signum, frame)

    def shutdown(self, signum, frame):

        """ Stop the necessary sub-processes.  And shutdown in a
        controlled manner. """
        
        # Ignore SIGHUP, SIGINT and SIGTERM signals during shutdown.
        
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        
        self.log.info('Shutting down...')
        
        # Request that each TUC process halts.
        
        results = Queue.Queue(self.tuc_pool_size)
        task = (EncapsulateTUC.TYPE_SHUTDOWN, 'halt.')
        
        for i in range(self.tuc_pool_size):
            self.tuc_pool.queue_task(task, results)
            
        for i in range(self.tuc_pool_size):
            results.get()
            
        # Join all the running threads (wait for their exits).
        
        self.tuc_pool.join_all()
        self.log.info('... all TUC threads joined.')
        
        self.__shutdown = True
        sys.exit(0)
        

def main():
    
    """ Module mainline (for standalone execution). """

    return


if __name__ == "__main__":
    main()
