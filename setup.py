#! /usr/bin/python
# -*- coding: latin-1 -*-

""" 
$Id$

Copyright (C) 2004 by Martin Thorsen Ranang
"""

from distutils.core import setup

setup(name = 'TTPD',
      version = '0.9.0',
      description = 'TUC Transfer Protocol Daemon and TUC Alert Daemon',
      author = 'Martin Thorsen Ranang',
      author_email = 'mtr@ranang.org',
      url = 'http://www.ranang.org/',
      platforms = ['Linux-2.6.7-686-mtr-i686-with-debian-3.1',
                   'SunOS-5.9-sun4u-sparc-32bit-ELF'],
      packages = ['TTP'],
      scripts = ['ttpd', 'ttpc', 'ttpdctl', 'ttpd_analyze'],
      data_files = [('share/doc', ['doc/ttpd_documentation.ps'])]
      )
