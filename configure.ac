dnl Process this file with autoconf to produce a configure script.
dnl 
dnl $Id: configure.ac 335 2008-09-29 07:51:50Z mtr $
dnl
AC_INIT(ttpd, 2.2.0)
AC_CONFIG_SRCDIR(src/ttpd)
AM_INIT_AUTOMAKE

dnl AC_PREFIX_DEFAULT(/usr)

AM_PATH_PYTHON(2.5,, :)

AC_OUTPUT([Makefile
	   bin/Makefile
	   doc/Makefile
	   etc/Makefile
	   etc/apache2/Makefile
	   etc/apache2/sites-available/Makefile
	   etc/cron.d/Makefile
	   etc/default/Makefile
	   etc/init.d/Makefile
	   etc/logrotate.d/Makefile
	   src/Makefile
	   statistics/Makefile
	   www/Makefile
	   www/busstuc.lingit.no/Makefile
	   www/busstuc.lingit.no-team-trafikk/Makefile
	   ],
          [chmod +x src/ttpd])
