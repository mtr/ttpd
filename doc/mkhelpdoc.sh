#! /bin/bash
#
# $Id$
#
# Copyright (C) 2004, 2009 by Lingit AS
#

. ../bin/config.sh

PROGRAMS="ttpd ttpc ttpdctl"

PYTHONPATH="$top_srcdir/lib"
echo "PYTHONPATH="$PYTHONPATH

for prog in $PROGRAMS; do
    PYTHONPATH="$top_srcdir/lib" ../src/$prog --help > "usage_$prog.txt";
done
