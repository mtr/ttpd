#! /usr/bin/python
# -*- coding: latin-1 -*-
# $Id$
"""
A function that daemonifies its caller process.

This script creates a daemon in a standard Unix way.

Copyright (C) 2004, 2007 by Martin Thorsen Ranang
"""

__author__ = "Martin Thorsen Ranang"
__version__ = "$Rev$"

import os
import signal
import sys

def create_daemon():
    """Detach a process from the controlling terminal and run it in
    the background as a daemon.
    """
    try:
        # Fork a child process and exit the parent.
        pid = os.fork()
    except OSError, e:
        return((e.errno, e.strerror))
    
    if (pid == 0):                      # The first child.
        # Become the session leader of this new session.
        os.setsid()

        # Ignore the SIGHUP, because when the first child terminates,
        # all second child processes are sent a SIGHUP.
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        
        try:
            # Fork a second child to prevent zombies.
            pid = os.fork()             
        except OSError, e:
            return((e.errno, e.strerror))
        
        if (pid == 0):                  # The second child.
            # Don't keep any non-root directory in use.  Avoid umount
            # troubles.
            os.chdir("/")
            
            # Give the child complete control over permissions.
            os.umask(0)
        else:
            # Why _exit()?  It behaves much like exit(), but it does
            # not call any functions registered with atexit().
            os._exit(0)             # Exit parent of the second child.
    else:
        os._exit(0)                  # Exit parent of the first child.

    # Only the second-stage child will get this far.
    
    # Close all open files.
    maxfd = os.sysconf("SC_OPEN_MAX")
    if maxfd == -1:
        maxfd = 256
        
    for fd in xrange(maxfd):
        try:
            os.close(fd)
        except OSError:
            pass
        
    # Redirect the standard file descriptors to /dev/null.
    os.open("/dev/null", os.O_RDONLY)   # stdin
    os.open("/dev/null", os.O_WRONLY)   # stdout
    os.open("/dev/null", os.O_WRONLY)   # stderr
    
    return 0

# import pwd, grp

# def get_uid_gid(username, groupname):
#     return pwd.getpwnam(username)[2], grp.getgrnam(groupname)[2]

# def get_username_groupname(uid, gid):
#     return pwd.getpwuid(uid)[0], grp.getgrgid(gid)[0]

def drop_root_privileges(target_uid, target_gid, permanently=True):
    '''Change the real and effective user and group ID, possibly
    permanently.
    '''
    os.setgid(target_gid)
    os.setuid(target_uid)

        
def main():
    """Module mainline (for standalone execution).
    """
    create_daemon()
    
    return

if __name__ == '__main__':
    main()
