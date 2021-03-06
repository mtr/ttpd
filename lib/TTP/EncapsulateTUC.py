#! /usr/bin/python
# -*- coding: latin-1 -*-
# $Id$
"""
Classes to encapsulate a sub-process and communicate with it.

Copyright (C) 2004, 2007 by Lingit AS
"""

__version__ = "$Rev$"

import fcntl
import logging
import os
import re
import select
import signal
import subprocess
import sys
import time


QUERY_TYPE_NONE     = 0
QUERY_TYPE_SMS      = 1
QUERY_TYPE_WEB      = 2
QUERY_TYPE_NORMAL   = QUERY_TYPE_SMS | QUERY_TYPE_WEB
QUERY_TYPE_SHUTDOWN = 4

class EncapsulateProcess:
    """A class that encapsulates a generic command and establishes a
    two-way communication (through pipes) with the forked process.
    """
    
    def __init__(self, command, environment=None):
        """Initialize class instance."""
        self.command = command
        self.environment = environment
        
    def set_nonblocking(self, fd):
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        try:
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NDELAY)
        except AttributeError:
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | fcntl.FNDELAY)
            
    def run(self):
        """Encapsulate a sub-process and keep information about it,
        including input and ouput streams and the pid of the process.

        We use the popen2.Popen4() class because we need more control
        over the new process than the os.popen4() function provides
        (e.g., the child pid).

        Also, check that the command is available in the current path.
        """
        try:
            self.subprocess = subprocess.Popen(self.command,
                                               stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.STDOUT,
                                               close_fds=True,
                                               env=self.environment)
        except OSError, e:
            self.log.error('Unable to run and encapsulate "%s".  %s.  ' \
                           'Shutting down...',
                           self.command, e)

            os.kill(os.getpid(), signal.SIGTERM)

        self.set_nonblocking(self.subprocess.stdout)
                    
    def get_pid(self):
        """Returns the PID of the subprocess.
        """
        return self.subprocess.pid

    def read(self, timeout = None):
        """Perform non-blocking read until magic is reached.
        """
        started = time.time()
        
        data = ''
        
        while True:
            ready = select.select([self.subprocess.stdout], [], [],
                                  timeout)
            
            if len(ready[0]) == 0:      # No data -> timeout.
                return (1, data)
            
            delta = self.subprocess.stdout.read()
            if delta == '':
                if __debug__:  # Optimized away with Python's -O flag.
                    self.log.debug("Read data = '%s'.", data)
                    
                return (0, data)
            
            data += delta
            
            if timeout and ((time.time() - started) > timeout):
                if __debug__: # Optimized away with Python's -O flag.
                    self.log.debug("Timed out.  Read data = '%s'.", data)
                    
                return (1, data) # Timeout -> may be more data.

    def write(self, string, *args):
        self.subprocess.stdin.write(string % args)
        
    def flush(self):
        self.subprocess.stdin.flush()
        
    def readline(self):
        return self.subprocess.stdout.readline()
    

class EncapsulateTUC(EncapsulateProcess):
    """A class that encapsulates a TUC process.
    """
    def __init__(self, command, eos_magic, log=None, environment=None):
        self.magic = eos_magic
        
        # In SICStus 3.8.7 self.eos_magic should look like:
        #    '%s \nyes\n' % self.magic
        #self.eos_magic = '%s yes\n' % self.magic
        self.eos_magic_re = re.compile('%s \n?yes\n$' %
                                       (re.escape(self.magic)), re.MULTILINE)
        self.magic_len = len('%s \nyes\n' % (self.magic))
        
        self.global_timeout = 60
        self.local_timeout = .01
        
        if log:
            self.log = log
        else:
            class __ZeroLogger(object):
                def info(self, *args): pass
                debug = info
                error = info
                warn = info
                exception = info
                
            self.log = __ZeroLogger()
            
        # Call the parent's class constructor.
        EncapsulateProcess.__init__(self, command, environment)

    def run(self):
        """Start the encapsulated process and perform necessary
        ante-processing cleanups.
        """
        self.log.debug('Trying to encapsulate TUC process...')

        EncapsulateProcess.run(self)

        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('... OK (PID = %d)... Cleaning up...',
                           self.subprocess.pid)
        
        # Remove "garbage" (licensing info) from SICStus.
        self.write('write(\'%s \'), flush_output.\n', self.magic)
        self.flush()
        self.read()
        
        self.log.info('Encapsulated TUC process (PID = %d).',
                      self.subprocess.pid)
        
        return

    def flush(self):
        """A more robust flush method.
        """
        try:
            EncapsulateProcess.flush(self)
        except:
            self.log.exception('Error')
            
    def read(self, timeout=None):
        if not timeout:
            timeout = self.global_timeout
            
        data = ''
        done = False
        
        while not done:
            status, delta = EncapsulateProcess.read(self, self.local_timeout)

            if delta:
                data += delta

                for m in self.eos_magic_re.finditer(data, -self.magic_len):
                    data = data[:-(m.end() - m.start())]
                    done = True
                
            if status == 0:
                done = True
                
        return data

    __predicate = {
        QUERY_TYPE_WEB: 'mtrprocessweb',
        QUERY_TYPE_SMS: 'mtrprocess',
        }
    
    def process(self, (kind, query)):
        if kind & QUERY_TYPE_NORMAL:
            # Normal processing requested.
            self.write('%s("%s"). write(\'%s \'), flush_output.\n',
                       self.__predicate[kind], query, self.magic)
            
            self.flush()
            
            return self.read()
        
        elif kind == QUERY_TYPE_SHUTDOWN:
            # Shutdown requested.
            self.write('%s\n', query) # Usually a 'halt.' Prolog query.
            self.flush()
            
            self.subprocess.stdout.close()
            self.subprocess.stdin.close()
            
            # Wait for the dead child process.
            self.subprocess.wait()
            
            self.log.info('Shut down TUC process (PID = %d).', self.get_pid())
            
def main ():
    """Module mainline (for standalone execution).
    """
    cmd = sys.argv[1]

    MAGIC = '!#%!MTR!%#!'
    
    L = [
        'Hva er klokka?',
        'georgewarrenbush',
        'N�r g�r neste buss til dragvoll?',
        'johnforbeskerry',
        'Kan du varsle meg 20 minutter f�r neste buss til Samfunnet fra Gl�s?'
        ]

    ep = EncapsulateTUC(cmd, MAGIC)
    ep.run()
    
    for l in L:
        print ep.process((QUERY_TYPE_NORMAL, l))

    ep.process((QUERY_TYPE_SHUTDOWN, 'halt.'))
    
    return

if __name__ == "__main__":
    main ()
