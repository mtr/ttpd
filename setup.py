#! /usr/bin/python
# -*- coding: latin-1 -*-

""" 
$Id$

Copyright (C) 2004, 2006, 2007 by Martin Thorsen Ranang
"""

import imp
import re

from distutils.core import setup


package = imp.load_source('package', 'ttpd')

author_re = re.compile('(?P<name>.*) <(?P<email>[^>]*)>$')

package_author, package_email = author_re.match(package.__author__).groups()

setup(name = 'TTPD',
      version = package.__version__,
      description = 'TUC Transfer Protocol Daemon and TUC Alert Daemon',
      author = package_author,
      author_email = package_email,
      url = 'http://www.ranang.org/',
      platforms = ['Linux-2.6.7-686-mtr-i686-with-debian-3.1',
                   'SunOS-5.9-sun4u-sparc-32bit-ELF'],
      packages = ['TTP'],
      scripts = ['ttpd', 'ttpc', 'ttpdctl', 'ttpd_analyze', 'log_filter'],
      data_files = [('share/doc', ['doc/ttpd_documentation.ps']),
                    ('statistics', ['statistics/general_config.sh',
                                    'statistics/last_52_weeks.sh',
                                    'statistics/last_week.sh',
                                    'statistics/this_week.sh',
                                    'statistics/today.sh',]),
                    ])
