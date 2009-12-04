# Copyright (C) 2007 by Martin Thorsen Ranang
#
# $Id: Makefile.am 299 2007-06-20 19:35:26Z mtr $
#
SUBDIRS = src doc etc statistics www #lib/

#EXTRA_DIST = src/*.py #lib/

include ${top_srcdir}/extradefs.mk

ignore_in = Makefile.in MANIFEST.in

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

pysetyp = setup.py

GET_RELEASE = $(top_srcdir)/bin/get_release

RELEASE := $(shell $(GET_RELEASE))

DISTDIR = $(top_srcdir)/dist

all: $(generated) all-recursive

release:
	$(top_srcdir)/bin/increase_release

next_release:
	$(top_srcdir)/bin/increase_release

tag_release:
	$(top_srcdir)/bin/tag_release

rpm: all release tag_release changelog $(pysetyp)
	@python $(pysetyp) clean
	@python $(pysetyp) bdist_rpm --python=$(PYTHON) --release=$(RELEASE) --post-install=$(top_srcdir)/src/post-install.sh --pre-uninstall=$(top_srcdir)/src/pre-uninstall.sh

deb_sign: deb
	pushd $(DISTDIR) && dpkg-sig --sign builder $(PACKAGE)_$(VERSION)-$(RELEASE)_all.deb && popd

deb: rpm
	pushd $(DISTDIR) && EMAIL="mtr@ranang.org" fakeroot alien --to-deb --keep-version --scripts $(PACKAGE)-$(VERSION)-$(RELEASE).noarch.rpm && popd

tests:
	PYTHONPATH=$(top_srcdir)/lib pytest test

etags:
	etags --language-force=Python \
		src/* \
		$$(find lib -name \*\.py |tr '\n' ' ')

changelog: 
	svn2cl --break-before-msg --group-by-day --authors=AUTHORS 
