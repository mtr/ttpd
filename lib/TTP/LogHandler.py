#! /usr/bin/python
# -*- coding: latin-1 -*-
# $Id$
"""
A log file handler to be used by daemon processes.

Copyright (C) 2004 by Martin Thorsen Ranang
"""

__version__ = "$Rev$"

import logging
import types

log_line_re_date = '(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3})'

# Define a new logging level.

NOTSET = logging.NOTSET
PROTOCOL = (logging.NOTSET + logging.DEBUG) / 2
DEBUG = logging.DEBUG
INFO = logging.INFO

logging.addLevelName(PROTOCOL, 'PROTOCOL')

# Create a mapping between the user-supplied log level string and the
# constants define by the logging module.

log_levels = dict([(logging.getLevelName(l).lower(), l)
                   for l in logging._levelNames if type(l) == types.IntType])

def get_log_levels():
    """Return a sorted list of log levels.
    """
    items = [(v, k) for k, v in log_levels.items()]
    items.sort()
    return [k for v, k in items]
    
class DaemonFileHandler(logging.FileHandler):
    """A log file handler implementation well suited for daemon usage.
    It's considered nice behavior for a daemon to reopen its log files
    when it recieves a certain signal (usually SIGHUP).
    """
    def reopen(self, mode='a'):
        """Reopen the log file.  This is necessary for rotating logs
        without restarting the whole daemon.
        """
        new_stream = open(self.baseFilename, self.mode)
        self.stream.close()
        self.stream = new_stream

class LogHandler(DaemonFileHandler):
    """A handler class which writes formatted logging records to disk
    files.
    """
    def __init__(self, filename, mode='a'):
        """Open the specified file and use it as the stream for
        logging.
        """
        DaemonFileHandler.__init__(self, filename, mode)
        
        self.setFormatter(logging.Formatter('%(asctime)s %(name)s ' \
                                            '%(levelname)s ' \
                                            '%(message)s',
                                            #'%Y-%m-%d %H:%M:%S.%N'
                                            ))

def main ():
    """Module mainline (for standalone execution).
    """
    return

if __name__ == "__main__":
    main ()
