#! /usr/bin/python
# -*- coding: latin-1 -*-
"""

$Id$

The TUC Alert Daemon.

A daemon responsible for handling alerts according to the TUC Alert
service.  This module is designed to work in co-existence with TTPD.

Copyright (C) 2004 by Martin Thorsen Ranang
"""

__version__ = "$Rev$"


import Queue
import bisect
import logging
import os
import re
import sys
import time

import random
import threading

import TTPDLogHandler

# The following values are only defaults and may be overridden in the
# constructor call to TUCAlertDaemon.

LOG_FILENAME = 'tttp_tad.log'
LOG_CHANNEL = 'ttpd.tad'


class PriorityQueue(Queue.Queue):

    """ A simple priority queue implementation. """
    
    def _put(self, item):
        bisect.insort(self.queue, item)
        

class GeneralThreadingScheduler(threading.Thread):
    
    """ A thread-safe general purpose scheduler.  At the moment, it
    doesn't seem that the standard sched module in Python is
    thread-safe.  Hence, I wrote this class.  The sheduler thread is
    started with <instance>.start(). """
    
    def __init__(self, time_func = time.time, delay_func = time.sleep,
                 delay = 0.01):
        
        """ Initialize the thread and remember timing options. """
        
        self.__queue = []
        self.__queue_lock = threading.Condition(threading.Lock())
        self.__shutdown = False
        self.__shutdown_lock = threading.Condition(threading.Lock())
        
        threading.Thread.__init__(self)
        
        self.time_func = time_func
        self.delay_func = delay_func
        self.delay = delay
        
    def abs_enter(self, event):
        
        """ Enter a new event with an absolute time reference into the
        priority queue.
        
        The event should argument should be a tuple of the form (time,
        priority, action, argument). """
        
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
        
        """ Remove an event from the queue. """

        self.__queue_lock.acquire()
        try:
            self.__queue.remove(event)
            return event
        finally:
            self.__queue_lock.release()

    def empty(self):

        """ Return a boolean indicating whether the queue is empty or
        not. """
        
        self.__queue_lock.acquire()
        try:
            print 'len =', len(self.__queue)
            return len(self.__queue) == 0
        finally:
            self.__queue_lock.release()

    def __contains__(self, id):

        """ A membership test operator.  This enables the caller to
        perform a 'x in object' test. """
        
        self.__queue_lock.acquire()
        try:
            return id in self.__queue
        finally:
            self.__queue_lock.release()

    
    def shutdown(self):

        """ Tell the scheduling thread to shutdown. """
        
        self.__shutdown_lock.acquire()
        try:
            self.__shutdown = True
        finally:
            self.__shutdown_lock.release()
            
    def run(self):
        
        """ Start scheduling. """
        
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
                
                action(arguments)
                
            # Wait some time while releasing the processor for other
            # threads.
            
            self.delay_func(self.delay)

    def hold(self):

        """ Pause the scheduler until the release() method is
        called. """
        
        self.__queue_lock.acquire()

    def release(self):

        """ Release the scheduler after a hold() call. """
        
        self.__queue_lock.release()
        
    def join(self):
        
        """ Stop the scheduler and wait for its thread to join. """
        
        self.shutdown()
        threading.Thread.join(self)
        

class TUCAlertDaemon(object):
    
    log_line_re = re.compile('(?P<date>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) ' \
                             '%s CRITICAL ' \
                             '(?P<command>\S+) ' \
                             '\((?P<id>\d+),? ?' \
                             '(?P<moment>\d+.\d+|),? ?(?P<ext_id>\w*),? ?' \
                             '"?(?P<message>.*?)"?\)' % (LOG_CHANNEL))
    
    # Long format: 'COMMAND (id, moment, ext_id, "message")'.
    #
    # Used by the INSERTED command.  Must contain this info in order
    # to restore the scheduler based on the last log.
    
    log_format = '%s (%d, %f, %s, "%s")'
    
    # Short format: 'COMMAND (id)'.
    #
    # Used for ALERTED and CANCELED commands.
    
    short_log_format = '%s (%d)'
    
    def __init__(self, log_channel = LOG_CHANNEL,
                 log_filename = None, log_level = logging.DEBUG):
        
        """ Initialize the daemon. """
        
        # Setup a reentrant lock in order to ensure thread safety.
        
        self.__lock = threading.Condition(threading.RLock())
        
        self.__lock.acquire()
        try:

            # A map from the ids of events to the events themselves.
            # The map is used to lookup the events given an id; needed
            # by e.g. cancel_alert.
        
            self.__events = {}
            
            self.scheduler = GeneralThreadingScheduler()
            self.__shutdown = False
            
            self.__log_channel = log_channel
            self.__log_filename = log_filename
            
            self.__highest_id = 0
            
            # First, initialize the logging facilities and start logging.
        
            self.log_init(log_level)

            # Then restore the state of the scheduler based on the
            # very same (current) logs.
        
            self.restore()
            
        finally:
            self.__lock.release()
            
    def log_init(self, log_level = logging.DEBUG):
        
        """ Intialize logging facilities and log some useful startup
        information. """
        
        self.__lock.acquire()
        try:
            self.log = logging.getLogger(self.__log_channel)
            
            #self.handler = TTPDLogHandler.TTPDLogHandler(self.__log_filename)
            #self.log.addHandler(self.handler)
            #self.log.setLevel(log_level)
        finally:
            self.__lock.release()
            
    def handle_restore_item(self, item, now):
        
        """ Handle a single restore item. """

        self.__lock.acquire()
        try:
            date, command, id, moment, ext_id, message = item
        
            id = int(id)
        
            self.__highest_id = max([self.__highest_id, id])
        
            # print item
        
            if command == 'INSERTED':
                if id in self.__pre_inserted:
                    del self.__pre_inserted[id]
                    
                self.__pre_inserted[id] = item
                
                # Because the INSERTED has to have appeared earlier
                # than ALERTED and CANCELED (for a specific id), there
                # should be no need to check for existence of the
                # alert.  However, we might be reading from a
                # broken-time-line/rotated log.
                
            elif command in ['ALERTED', 'CANCELED']:
                
                if id in self.__pre_inserted:
                    del self.__pre_inserted[id]
                    
        finally:
            self.__lock.release()
            
    def restore(self):
        
        """ Restore the state of the scheduler after a startup, based
        on an existing log file (if there is one). """

        self.__lock.acquire()
        try:
            if not os.access(self.__log_filename, os.F_OK | os.R_OK):
                self.log.warn("Scheduler state not restored.  Couldn' open " \
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

            for id, item in self.__pre_inserted.items():
                date, command, s_id, s_moment, ext_id, message = item

                # Convert the moment _string_ to a timestamp-float.
                moment = float(s_moment)
                
                self._insert_alert(moment, message, id, ext_id)
                
            del self.__pre_inserted
        
        finally:
            self.__lock.release()

    def store(self):

        """ Store all the current contents of the sceduler to a file.
        This ensures a scheduler state memory after log rotations. """

        self.__lock.acquire()
        try:

            self.log.info('Storing the current scheduler state...')
            
            self.scheduler.hold()
            
            ids = self.__events.keys()
            ids.sort()
            
            for id in ids:
                moment, priority, handler, data = self.__events[id]
                ignore_id, ext_id, message = data
                
                self.log.critical(self.log_format % ('INSERTED', id, moment,
                                                     ext_id, message))
            self.scheduler.release()
            
            self.log.info('... done storing the scheduler state.')
        finally:
            self.__lock.release()
            
    def shutdown(self, signum, frame):

        """ Shutdown the daemon gracefully. """
        
        self.__lock.acquire()
        try:
            
            self.__shutdown = True
            
            self.log.handler.close()
            
            self.scheduler.join()
            
        finally:
            self.__lock.release()
            
    def run(self):
        
        """ Start the scheduler (thread). """

        self.__lock.acquire()
        try:
            
            self.scheduler.start()
            
        finally:
            self.__lock.release()
            
    def handle_alert(self, data):
        
        self.__lock.acquire()
        try:

            id, ext_id, message = data

            self.log.critical(self.short_log_format % ('ALERTED', id))

            del self.__events[id]
            
        finally:
            self.__lock.release()
            
    def next_id(self):

        """ Return the next (internal) id. """

        self.__lock.acquire()
        try:
        
            self.__highest_id += 1
            return self.__highest_id

        finally:
            self.__lock.release()
            
    def _insert_alert(self, moment, message, id, ext_id):
        
        self.__lock.acquire()
        try:
            event = (moment, 1, self.handle_alert, (id, ext_id, message))
            self.__events[id] = self.scheduler.abs_enter(event)
        finally:
            self.__lock.release()
        
    def insert_alert(self, moment, message, ext_id):

        self.__lock.acquire()
        try:
            print 'moment', moment
        
            id = self.next_id()
            self._insert_alert(moment, message, id, ext_id)
            self.log.critical(self.log_format % ('INSERTED', id, moment,
                                                 ext_id, message))
            return id
        finally:
            self.__lock.release()
        
    def cancel_alert(self, id, command = 'CANCELED'):
        
        self.__lock.acquire()
        try:
            if id not in self.__events:
                return False
            
            event = self.__events[id]

            (moment, priority, self.handle_alert, (id, ext_id, message)) = \
                     event

            self.log.critical(self.short_log_format %
                              (command, id))
            
            self.scheduler.cancel(event)
            
            del self.__events[id]

            return True
            
        finally:
            self.__lock.release()
        
        
def main ():
    """
    main ()
    Module mainline (for standalone execution)
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
