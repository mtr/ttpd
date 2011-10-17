#! /usr/bin/python
# -*- coding: latin-1 -*-
# $Id$
"""
A class of worker threads that will encapsulate and controll a TUC
process.

Copyright (C) 2004, 2007 by Lingit AS
"""

__version__ = "$Rev$"
__author__ = "Martin Thorsen Ranang"

import Queue
import time
import TTP.EncapsulateTUC
import TTP.ThreadPool


class TUCThreadPool(TTP.ThreadPool.ThreadPool):
    """A thread pool class tailored to the needs of TTPD.

    One of the additional features of this class is the log member
    variable.
    """

    def __init__(self, num_threads, command='./busestuc.sav', environment=None,
                 thread_class=TTP.ThreadPool.ThreadPoolThread, log=None):
        
        """Intialize a new class instance.
        """
        self.log = log
        self.command = command
        self.environment = environment
        
        TTP.ThreadPool.ThreadPool.__init__(self, num_threads, thread_class)
        

class TUCThread(TTP.ThreadPool.ThreadPoolThread):
    """A pooled thread class to process TUC queries.
    """
    MAGIC = '!#%!MTR!%#!'
    
    def __init__(self, pool):
        """Initialize thread instance and logging facilities.
        """
        self.log = pool.log

        self.__ep = None
        
        # Perform superclass initialization.
        TTP.ThreadPool.ThreadPoolThread.__init__(self, pool)
        
    def encapsulate(self):
        """Perform a TUC subprocess encapsulation.
        """
        self.__ep = TTP.EncapsulateTUC.EncapsulateTUC(self.pool.command,
                                                      self.MAGIC,
                                                      self.log,
                                                      self.pool.environment)
        
        # Run the encapsulated process.
        self.__ep.run()
        
    def watchdog(self):
        dead = self.__ep.subprocess.poll()

        if dead:
            self.log.error("TUC process with PID = %d died " \
                           "unexpectedly with exit status '%d'.",
                           self.__ep.subprocess.pid, dead)
            self.log.error("Last words: '%s'",
                           self.__ep.subprocess.stdout.read())
            
            del self.__ep
            
            # Encapsulate a new TUC process.
            self.encapsulate()

    def process(self, ((kind, query), callback)):
        # Process the incoming task and place the result in the
        # callback queue.
        callback.put(self.__ep.process((kind, query)))
        
        if kind == TTP.EncapsulateTUC.QUERY_TYPE_SHUTDOWN:
            # A shutdown command was recieved.
            self.go_away()
            
    def run(self):
        # Encapsulate a TUC process.
        self.encapsulate()
        
        while self.is_dying == False:
            # Perform some sub-process watch-dogging.
            self.watchdog()
            
            # Check the next task in the pool.
            task = self.pool.get_next_task()
            
            if task is None:
                # If there's nothing to do, take a nap.
                time.sleep(self.thread_sleep_time)
            else:
                # Process the incoming task.
                self.process(task)
                
    
def main():
    """Module mainline (for standalone execution).
    """
    pool = TTP.ThreadPool.ThreadPool(3, TUCThread)
    result = Queue.Queue(1)
    
    # Insert tasks into the queue and let them run.
    #queries = ['Når går bussen fra nardo til byen?', 'Hva er klokka?'] * 10
    queries = ['Hva er klokka?']

    print 'waiting...'
    time.sleep(10)

    print 'starting...'
    pool.queue_task(queries[0], result)
    
    print result.get()

    # When all tasks are finished, allow the threads to terminate.
    pool.join_all()
    
    return

if __name__ == "__main__":
    main ()
