# $Id$
#
# Copyright (C) 2009 by Lingit AS

include ${top_srcdir}/extradefs.mk

dist_sbin_SCRIPTS = ttpd
dist_bin_SCRIPTS = ttpc ttpd_analyze ttpd_log_filter ttpdctl

ignore_in = Makefile.in

in_src = $(filter-out $(ignore_in),$(wildcard *.in))
generated = $(in_src:.in=)

$(generated): $(in_src) Makefile $(top_srcdir)/extradefs.mk
	rm -f $@ $@.tmp
	srcdir=''; \
	  test -f ./$@.in || srcdir=$(srcdir)/; \
	  $(edit) $${srcdir}$@.in >$@.tmp
	chmod a-w $@.tmp
	mv $@.tmp $@

CLEANFILES = $(generated)

all: $(generated)
