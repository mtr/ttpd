#! /bin/bash
#
# $Id$
#
# Copyright (C) 2004 by Martin Thorsen Ranang
#

PROGRAMS="ttpd ttpc"

for prog in $PROGRAMS; do
    ../$prog --help > "usage_$prog.txt";
done
