#! /usr/bin/python
# -*- coding: latin-1 -*-
# $Id$
"""
Classes to encapsulate a sub-process and communicate with it.

Copyright (C) 2004 by Martin Thorsen Ranang
"""

__version__ = "$Rev$"

import fcntl
import os
import popen2
import re
import select
import sys
import time

TYPE_NORMAL = 0
TYPE_SHUTDOWN = 1

class EncapsulateProcess:

    """ A class that encapsulates a generic command and establishes a
    two-way communication (through pipes) with the forked process. """
    
    def __init__(self, command):

        """ Initialize class instance. """
        
        self.command = command

    def set_nonblocking(self, fd):
        
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        try:
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NDELAY)
        except AttributeError:
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | fcntl.FNDELAY)
            
    def run(self):

        """ Encapsulate a sub-process and keep information about it,
        including input and ouput streams and the pid of the
        process.

        We use the popen2.Popen4() class because we need more control
        over the new process than the os.popen4() function provides
        (e.g., the child pid).

        Also, check that the command is available in the current
        path. """
        
        self.subprocess = popen2.Popen4(self.command)

        self.set_nonblocking(self.subprocess.fromchild)
                    
    def get_pid(self):

        """ Returns the PID of the subprocess. """

        return self.subprocess.pid

    def read(self, timeout = None):
        
        """ Perform non-blocking read until magic is reached. """
        
        started = time.time()
        
        data = ''
        
        fromchild_eof = False
        
        while True:
            
            if not fromchild_eof:
                ready = select.select([self.subprocess.fromchild], [], [],
                                      timeout)
                
            if len(ready[0]) == 0:      # No data -> timeout.
                return (1, data)
            
            else:
                delta = self.subprocess.fromchild.read()
                if delta == '':
                    fromchild_eof = True
                data += delta
                
                if fromchild_eof:
                    return (0, data)
                
                elif timeout:
                    if (time.time() - started) > timeout:
                        return (1, data) # Timeout -> may be more data.
                    

    def write(self, str, *args):
        
        self.subprocess.tochild.write(str % args)
        
    def flush(self):
        
        self.subprocess.tochild.flush()
        
    def readline(self):
        
        return self.subprocess.fromchild.readline()
    

class EncapsulateTUC(EncapsulateProcess):

    """ A class that encapsulates a TUC process. """
    
    def __init__(self, command, eos_magic, log = None):
        
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
                exception = info
                
            self.log = __ZeroLogger()
            
        # Call the parent's class constructor.
        
        EncapsulateProcess.__init__(self, command)

    def run(self):

        """ Start the encapsulated process and perform necessary
        ante-processing cleanups. """

        self.log.debug('Trying to encapsulate TUC process...')
        
        EncapsulateProcess.run(self)
        
        self.log.debug('... OK (PID = %d)... Cleaning up...' %
                       (self.subprocess.pid))
        
        # Remove "garbage" (licensing info) from SICStus.
        
        self.write('write(\'%s \'), flush_output.\n', self.magic)
        self.flush()
        self.read()
        
        self.log.info('Encapsulated TUC process (PID = %d).' %
                      (self.subprocess.pid))
        
        return

    def flush(self):

        """ A more robust flush method. """
        
        try:
            EncapsulateProcess.flush(self)
        except:
            self.log.exception('Error')
            
    def read(self, timeout = None):
        
        if not timeout:
            timeout = self.global_timeout
            
        data = ''
        done = False
        
        while not done:
            
            status, delta = EncapsulateProcess.read(self, self.local_timeout)
            if delta:
                data += delta
                
                m = self.eos_magic_re.search(data, -self.magic_len)
                if m:
                    data = data[:-(m.end() - m.start())]
                    done = True
                    
                    # self.log.debug('delta = "%s"' % delta)

                #print 'delta = "%s"' % delta

                #print 'data[-self.magic_len:] = "%s"' % data[-self.magic_len:]
                
            if status == 0:
                done = True
                
        return data
        
    def process(self, (type, query)):
        
        if type == TYPE_NORMAL:
            
            # Normal processing requested.
            
            self.write('mtrprocess("%s"). write(\'%s \'), flush_output.\n',
                       query, self.magic)
            
            self.flush()
            
            return self.read()
        
            #return self.readlines()
        
        elif type == TYPE_SHUTDOWN:

            # Shutdown requested.
            
            self.write('%s\n', query) # Usually a 'halt.' Prolog query.
            self.flush()
            
            self.subprocess.fromchild.close()
            self.subprocess.tochild.close()
            
            # Wait for the dead child process.
            
            self.subprocess.wait()
            
            self.log.info('Shut down TUC process (PID = %d).' % self.get_pid())
            
def main ():

    """ Module mainline (for standalone execution). """
    
    cmd = sys.argv[1]
    
    MAGIC = '!#%!MTR!%#!'
    
    L = [
        'Hva er klokka?',
        'georgewarrenbush',
        'Når går neste buss til dragvoll?',
        'johnforbeskerry',
        'Kan du varsle meg 20 minutter før neste buss til Samfunnet fra Gløs?'
        ]
    
    ep = EncapsulateTUC(cmd, MAGIC)
    ep.run()
    
    for l in L:
        print ep.process((TYPE_NORMAL, l))
        
    return

if __name__ == "__main__":
    main ()
