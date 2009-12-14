#! /usr/bin/python
# -*- coding: latin-1 -*-
# $Id$
"""
The TUC Alert Daemon.

A daemon responsible for handling alerts according to the TUC Alert
service.  This module is designed to work in co-existence with TTPD.

Copyright (C) 2004, 2007 by Martin Thorsen Ranang
"""

__version__ = "$Rev$"


import Queue
import bisect
import logging
import os
import random
import re
import sys
import threading
import time
import logging
import socket

import TTP.Message
import TTP.LogHandler

# The following values are only defaults and may be overridden in the
# constructor call to TUCAlertDaemon.
#LOG_FILENAME = 'tttp_tad.log'
LOG_CHANNEL = 'ttpd.tad'


class PriorityQueue(Queue.Queue):
    """A simple priority queue implementation.
    """
    def _put(self, item):
        bisect.insort(self.queue, item)
        

class GeneralThreadingScheduler(threading.Thread):
    """A thread-safe general purpose scheduler.  At the moment, it
    doesn't seem that the standard sched module in Python is
    thread-safe.  Hence, I wrote this class.  The sheduler thread is
    started with <instance>.start().
    """
    
    def __init__(self, log=None, time_func=time.time, delay_func=time.sleep,
                 delay=0.01):
        """Initialize the thread and remember timing options.
        """
        self.__queue = []
        self.__queue_lock = threading.Condition(threading.Lock())
        self.__shutdown = False
        self.__shutdown_lock = threading.Condition(threading.Lock())
        
        self.log = logging.getLogger('ttpd.tad.handler')
        
        threading.Thread.__init__(self)
        
        self.time_func = time_func
        self.delay_func = delay_func
        self.delay = delay
        
    def abs_enter(self, event):
        """Enter a new event with an absolute time reference into the
        priority queue.
        
        The event should argument should be a tuple of the form (time,
        priority, action, argument).
        """
        self.__queue_lock.acquire()
        try:
            #print 'entering:', event
            if self.__shutdown == True:
                return False
            else:
                bisect.insort(self.__queue, event)
                return event
        finally:
            self.__queue_lock.release()
            
    def cancel(self, event):
        """Remove an event from the queue.
        """
        self.__queue_lock.acquire()
        try:
            self.__queue.remove(event)
            return event
        finally:
            self.__queue_lock.release()

    def empty(self):
        """Return a boolean indicating whether the queue is empty or
        not.
        """
        self.__queue_lock.acquire()
        try:
            print 'len =', len(self.__queue)
            return len(self.__queue) == 0
        finally:
            self.__queue_lock.release()

    def __contains__(self, identity):
        """A membership test operator.  This enables the caller to
        perform a 'x in object' test.
        """
        self.__queue_lock.acquire()
        try:
            return identity in self.__queue
        finally:
            self.__queue_lock.release()

    
    def shutdown(self):
        """Tell the scheduling thread to shutdown.
        """
        self.__shutdown_lock.acquire()
        try:
            self.__shutdown = True
        finally:
            self.__shutdown_lock.release()
            
    def run(self):
        """Start scheduling.
        """
        while not self.__shutdown:
            # The first pending event will always be the first moment
            # in time.
            self.__queue_lock.acquire()
            try:
                if self.__queue != [] and \
                       self.__queue[0][0] <= self.time_func():
                    # If the moment of the most pending task has
                    # arrived (or passed, possibly self.delay time
                    # units ago), then remove it from the queue.
                    event = self.__queue.pop(0)
                else:
                    # If not, continue with a non-existing event.
                    event = None
                    
            finally:
                self.__queue_lock.release()
                
            if event:               # The queue might have been empty.
                # Perform the scheduled action with the supplied
                # arguments.
                moment, priority, action, arguments = event

                try:
                    action(arguments)
                except socket.error:
                    
                    # Delay somewhere between 30 seconds and 3
                    # minutes.
                    delay = random.randint(30, 3 * 60)
                    
                    self.__queue_lock.acquire()
                    try:
                        bisect.insort(self.__queue,
                                      (moment + delay, priority, action,
                                       arguments))
                        
                        self.delay_func(1)
                    finally:
                        self.__queue_lock.release()

                    #self.log.debug('Could not perform action %s. Will try ' \
                    #               'again in %d seconds (%s and %s)',
                    #               (action, arguments),
                    #               delay, moment, self.time_func())
             
                    
            # Wait some time while releasing the processor for other
            # threads.
            self.delay_func(self.delay)

    def hold(self):
        """Pause the scheduler until the release() method is called.
        """
        self.__queue_lock.acquire()

    def release(self):
        """Release the scheduler after a hold() call.
        """
        self.__queue_lock.release()
        
    def join(self):
        """Stop the scheduler and wait for its thread to join.
        """
        self.shutdown()
        threading.Thread.join(self)
        

class TUCAlertDaemon(object):
    log_line_re = re.compile('%s ' \
                             '%s CRITICAL ' \
                             '(?P<command>\S+) ' \
                             '\((?P<id>\d+),? ?' \
                             '(?P<moment>\d+.\d+|),? ?(?P<ext_id>\w*),? ?' \
                             '"?(?P<message>.*?)"?\)' % \
                             (TTP.LogHandler.log_line_re_date, LOG_CHANNEL))
    
    # Long format: 'COMMAND (id, moment, ext_id, "message")'.
    #
    # Used by the INSERTED command.  Must contain this info in order
    # to restore the scheduler based on the last log.
    log_format = '%s (%d, %f, %s, "%s")'
    
    # Short format: 'COMMAND (id)'.
    #
    # Used for ALERTED and CANCELED commands.
    short_log_format = '%s (%d)'
    
    def __init__(self, remote_server_address, log_channel=LOG_CHANNEL,
                 log_filename=None, log_level=logging.DEBUG):
        """Initialize the daemon.
        """
        # Setup a reentrant lock in order to ensure thread safety.
        self.__lock = threading.Condition(threading.RLock())
        
        self.__lock.acquire()
        try:
            # Remember the address of the remote to which we will send
            # our alerts.
            self.remote_server_address = remote_server_address

            # First, initialize the logging facilities and start
            # logging.
            self.log_channel = log_channel
            self.__log_filename = log_filename
            
            self.log_init(log_level)
            
            # A map from the ids of events to the events themselves.
            # The map is used to lookup the events given an id; needed
            # by e.g. cancel_alert.
            self.__events = {}
            
            self.scheduler = GeneralThreadingScheduler()
            self.__shutdown = False
            
            self.__highest_id = 0

            # Then restore the state of the scheduler based on the
            # very same (current) logs.
            self.restore()
            
        finally:
            self.__lock.release()
            
    def log_init(self, log_level = logging.DEBUG):
        """Intialize logging facilities and log some useful startup
        information.
        """
        
        self.__lock.acquire()
        try:
            self.log = logging.getLogger(self.log_channel)
        finally:
            self.__lock.release()
            
    def handle_restore_item(self, item, now):
        """Handle a single restore item.
        """
        self.__lock.acquire()
        try:
            date, command, identity, moment, ext_id, message = item
        
            identity = int(identity)
        
            self.__highest_id = max([self.__highest_id, identity])
        
            # print item
            
            if command == 'INSERTED':
                if identity in self.__pre_inserted:
                    del self.__pre_inserted[identity]
                    
                self.__pre_inserted[identity] = item
                
                # Because the INSERTED has to have appeared earlier
                # than ALERTED and CANCELED (for a specific identity),
                # there should be no need to check for existence of
                # the alert.  However, we might be reading from a
                # broken-time-line/rotated log.
                
            elif command in ['ALERTED', 'CANCELED']:
                
                if identity in self.__pre_inserted:
                    del self.__pre_inserted[identity]
                    
        finally:
            self.__lock.release()
            
    def restore(self):
        """Restore the state of the scheduler after a startup, based
        on an existing log file (if there is one).
        """
        self.__lock.acquire()
        try:
            if not os.access(self.__log_filename, os.F_OK | os.R_OK):
                self.log.warn("Scheduler state not restored.  Couldn't open " \
                              "'%s'." % self.__log_filename)
                return
            
            log = open(self.__log_filename, 'r')

            self.__pre_inserted = {}

            now = time.time()

            for line in log:
                try:
                    m = self.log_line_re.match(line)
                    if m:
                        # Act upon the read "command line".  The
                        # handle_restore_item() has the side-effect that
                        # self.__pre_inserted and self.__highest_number
                        # are changed according to its input.
                        self.handle_restore_item(m.groups(), now)
                except:
                    # CRITICAL: If this exception is reached, we will most
                    # probably try to restore the scheduler state
                    # indefinitely because we read from the file we are
                    # logging to (and it's growing).
                    self.log.exception('An exception occurred.')

            log.close()

            self.log.info('Scheduler state restored based on ' \
                          'the old/above contents of this file.')

            #print self.__pre_inserted

            for identity, item in self.__pre_inserted.items():
                date, command, s_id, s_moment, ext_id, message = item

                # Convert the moment _string_ to a timestamp-float.
                moment = float(s_moment)
                
                self._insert_alert(moment, message, identity, ext_id)
                
            del self.__pre_inserted
        
        finally:
            self.__lock.release()

    def store(self):
        """Store all the current contents of the sceduler to a file.
        This ensures a scheduler state memory after log rotations.
        """
        self.__lock.acquire()
        try:
            self.log.info('Storing the current scheduler state...')
            
            self.scheduler.hold()
            
            ids = self.__events.keys()
            ids.sort()
            
            for identity in ids:
                moment, priority, handler, data = self.__events[identity]
                ignore_id, ext_id, message = data
                
                self.log.critical(self.log_format, 'INSERTED', identity,
                                  moment, ext_id, message)
                
            self.scheduler.release()
            
            self.log.info('... done storing the scheduler state.')
        finally:
            self.__lock.release()
            
    def shutdown(self, signum, frame):
        """Shutdown the daemon gracefully.
        """
        self.__lock.acquire()
        try:
            
            self.__shutdown = True
            
            self.log.handler.close()
            
            self.scheduler.join()
            
        finally:
            self.__lock.release()
            
    def run(self):
        """Start the scheduler (thread).
        """
        self.__lock.acquire()
        try:
            
            self.scheduler.start()
            
        finally:
            self.__lock.release()
            
    def handle_alert(self, data):
        """A thread-safe alert handler.
        
        @param data: A variable that holds the necessary information
        to perform a meaningful alert.
        """
        self.__lock.acquire()
        try:
            
            identity, ext_id, message = data
            
            ans = TTP.Message.MessageAck()
            ans.MxHead.TransId = 'LINGSMSOUT'
            ans.MxHead.ORName = ext_id
            ans.MxHead.Aux.InitIf = 'IP'
            ans.MxHead.Aux.InitProto = 'REMOTE' # FIXME: Is this correct?
            ans.MxHead.Aux.Billing = 2
            ans._setMessage(message)
            
            TTP.Message.communicate(ans, self.remote_server_address)
            
            self.log.critical(self.short_log_format, 'ALERTED', identity)
            
            del self.__events[identity]
            
        finally:
            self.__lock.release()
            
    def next_id(self):
        """Return the next (internal) id.
        """
        self.__lock.acquire()
        try:
        
            self.__highest_id += 1
            return self.__highest_id

        finally:
            self.__lock.release()
            
    def _insert_alert(self, moment, message, identity, ext_id):
        """The core functionality of insert_alert().

        Called both by outside objects (through insert_alarm()) and
        from the inside (through the restore() method).
        """
        self.__lock.acquire()
        try:
            event = (moment, 1, self.handle_alert, (identity, ext_id, message))
            self.__events[identity] = self.scheduler.abs_enter(event)
        finally:
            self.__lock.release()
        
    def insert_alert(self, moment, message, ext_id):
        """Insert an alert into the TAD scheduler.
        
        @param moment: The time at which the alert should take place.

        @param message: The message to be included in the alert.

        @param ext_id: The ID of the entity to be alerted.
        """
        self.__lock.acquire()
        try:
            identity = self.next_id()
            self._insert_alert(moment, message, identity, ext_id)
            
            self.log.critical(self.log_format, 'INSERTED', identity, moment,
                              ext_id, message)
            
            return identity
        finally:
            self.__lock.release()
            
    def cancel_alert(self, identity, command='CANCELED'):
        """Cancel an alert from the scheduler.

        @param identity: The identity of the alert to be canceled.
        
        @param command: The command word to write in the log file
        (used for later restore operations).
        """
        self.__lock.acquire()
        try:
            if identity not in self.__events:
                return False
            
            event = self.__events[identity]
            
            (moment, priority, handle_alert,
             (identity, ext_id, message)) = event
            
            self.log.critical(self.short_log_format % (command, identity))
            
            self.scheduler.cancel(event)
            
            del self.__events[identity]

            return True
            
        finally:
            self.__lock.release()
        
        
def main ():
    """Module mainline (for standalone execution).
    """
    
    d = TUCAlertDaemon()
    
    a = d.insert_alert(time.time(), 'A short test message', 'Spoofz')
    
    print 'id =', a
    
    b = d.insert_alert(time.time() + 20,
                       'Another short test message', 'Spoofx')
    
    print 'id =', b
    
    d.run()
    
    d.cancel_alert(a)
    
    time.sleep(30)

    d.store()
    
    return

if __name__ == "__main__":
    main ()
