#! /bin/bash
#
# $Id$
#
# Copyright (C) 2004 by Martin Thorsen Ranang
#

PROGRAMS="ttpd ttpc ttpdctl"

for prog in $PROGRAMS; do
    ../$prog --help > "usage_$prog.txt";
done
