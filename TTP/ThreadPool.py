#! /usr/bin/python
# -*- coding: latin-1 -*-
# $Id$
"""
A thread pool implementation.

Based on a generic-programming thread pool implementation written by
Tim Lesher 2003-09-24.

Copyright (C) 2004 by Martin Thorsen Ranang
"""

__version__ = "$Rev$"

import threading
import time


class ThreadPoolThread(threading.Thread):

    """ Pooled thread class. """
    
    thread_sleep_time = 0.01

    def __init__(self, pool):

        """ Initialize the thread and remember the pool. """
        
        threading.Thread.__init__(self)
        self.pool = pool
        self.is_dying = False
        
    def run(self):
        
        """ Until told to quit, retrieve the next task and execute it,
        calling the callback if any. """
        
        while self.is_dying == False:
            cmd, args, callback = self.pool.get_next_task()
            
            # If there's nothing to do, take a nap.
            
            if cmd is None:
                time.sleep(self.thread_sleep_time)
            elif callback is None:
                cmd(args)
            else:
                callback(cmd(args))
    
    def go_away(self):

        """ Exit the run loop next time through. """
        
        self.is_dying = True
        

class ThreadPool:

    """ Flexible thread pool class.  Creates a pool of threads, then
    accepts tasks that will be dispatched to the next available
    thread. """
    
    def __init__(self, num_threads, thread_class = ThreadPoolThread):

        """ Initialize the thread pool with NUM_THREADS workers. """

        self.ThreadClass = thread_class
        self.__threads = []
        self.__resize_lock = threading.Condition(threading.Lock())
        self.__task_lock = threading.Condition(threading.Lock())
        self.__tasks = []
        self.__is_joining = False
        self.set_thread_count(num_threads)

    def set_thread_count(self, new_num_threads):

        """ External method to set the current pool size.  Acquires the
        resizing lock, then calls the internal version to do real
        work. """
        
        # Can't change the thread count if we're shutting down the
        # pool.
        
        if self.__is_joining:
            return False
        
        self.__resize_lock.acquire()
        try:
            self.__set_thread_count_no_lock(new_num_threads)
        finally:
            self.__resize_lock.release()
        return True
    
    def __set_thread_count_no_lock(self, new_num_threads):
        
        """ Set the current pool size, spawning or terminating threads
        if necessary.  Internal use only; assumes the resizing lock is
        held. """
        
        # If we need to grow the pool, do so.
        
        while new_num_threads > len(self.__threads):
            new_thread = self.ThreadClass(self)
            self.__threads.append(new_thread)
            new_thread.start()
            
        # If we need to shrink the pool, do so.
        
        while new_num_threads < len(self.__threads):
            self.__threads[0].go_away()
            del self.__threads[0]
    
    def get_thread_count(self):

        """ Return the number of threads in the pool. """
        
        self.__resize_lock.acquire()
        try:
            return len(self.__threads)
        finally:
            self.__resize_lock.release()
    
    #def queue_task(self, task, args = None, task_callback = None):
    def queue_task(self, *task):
        
        """ Insert a task into the queue. """

        if self.__is_joining == True:
            return False
        #if not callable(task):
        #    return False
        
        self.__task_lock.acquire()
        try:
            #self.__tasks.append((task, args, task_callback))
            self.__tasks.append(task)
            return True
        finally:
            self.__task_lock.release()
    
    def get_next_task(self):

        """ Retrieve the next task from the task queue.  For use only
        by self.ThreadClass objects contained in the pool. """
        
        self.__task_lock.acquire()
        try:
            if self.__tasks == []:
                #return (None, None, None)
                return None
            else:
                return self.__tasks.pop(0)
        finally:
            self.__task_lock.release()
        return
    
    def join_all(self, wait_for_tasks = True, wait_for_threads = True):
        
        """ Clear the task queue and terminate all pooled threads,
        optionally allowing the tasks and threads to finish. """
        
        # Mark the pool as joining to prevent any more task queueing.
        
        self.__is_joining = True

        # Wait for tasks to finish.
        
        if wait_for_tasks:
            while self.__tasks != []:
                time.sleep(0.1)

        # Tell all the threads to quit.
        
        self.__resize_lock.acquire()
        try:
            
            # Wait until all threads have exited.
            
            if wait_for_threads:
                for t in self.__threads:
                    t.go_away()
                for t in self.__threads:
                    t.join()
                    #print t, "joined"
                    del t
            self.__set_thread_count_no_lock(0)
            self.__is_joining = True

            # Reset the pool for potential reuse.
            
            self.__is_joining = False
            
        finally:
            self.__resize_lock.release()
        return

        
def main ():
    """
    main ()
    Module mainline (for standalone execution)
    """
    from random import randrange

    # Sample task 1: given a start and end value, shuffle integers,
    # then sort them.
    
    def sort_task(data):
        print "sort_task starting for", data
        numbers = range(data[0], data[1])
        for a in numbers:
            rnd = randrange(0, len(numbers) - 1)
            a, numbers[rnd] = numbers[rnd], a
        print "sort_task sorting for", data
        numbers.sort()
        print "sort_task done for", data
        return "Sorter ", data

    # Sample task 2: just sleep for a number of seconds.

    def wait_task(data):
        print "wait_task starting for", data
        print "wait_task sleeping for %d seconds" % data
        time.sleep(data)
        return "Waiter", data
    
    # Both tasks use the same callback.

    def task_callback(data):
        print "Callback called for", data

    # Create a pool with three worker threads.

    pool = ThreadPool(3)
    
    # Insert tasks into the queue and let them run.
    
    pool.queue_task(sort_task, (1000, 100000), task_callback)
    pool.queue_task(wait_task, 5, task_callback)
    pool.queue_task(sort_task, (200, 200000), task_callback)
    pool.queue_task(wait_task, 2, task_callback)
    pool.queue_task(sort_task, (3, 30000), task_callback)
    pool.queue_task(wait_task, 7, task_callback)
    
    # When all tasks are finished, allow the threads to terminate.
    
    pool.join_all()
    return

if __name__ == "__main__":
    main ()
