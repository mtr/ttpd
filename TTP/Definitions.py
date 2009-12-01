#! /usr/bin/python
# -*- coding: iso-8859-1 -*-
# $Id$
"""
Copyright (C) 2009 by Martin Thorsen Ranang
"""
__author__ = ""
__revision__ = "$Rev$"
__version__ = "@VERSION@"

import os

VERSION      = __version__
PREFIX       = '/usr/local'
PACKAGE_NAME = 'ttpd'

DATA_DIR     = os.path.join(PREFIX, 'share', PACKAGE_NAME)
if not os.path.isdir(DATA_DIR):
    DATA_DIR = 'data'                   # For development purposes.
    
LOG_DIR      = os.path.join(os.path.sep, 'var', 'log', PACKAGE_NAME)
RUN_DIR      = os.path.join(os.path.sep, 'var', 'run')

CONFIG_FILE  = os.path.join(os.path.sep, 'etc', 'default', PACKAGE_NAME)
