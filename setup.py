#! /usr/bin/python
# -*- coding: latin-1 -*-

""" 
$Id$

Copyright (C) 2004 by Martin Thorsen Ranang
"""

from distutils.core import setup

setup(name = 'TTPD',
      version = '0.9.0',
      description = 'TUC Transfer Protocol Daemon',
      author = 'Martin Thorsen Ranang',
      author_email = 'mtr@ranang.org',
      url = 'http://www.ranang.org/',
      packages = ['ttp'],
      scripts = ['ttpd', 'ttpc']
      )
