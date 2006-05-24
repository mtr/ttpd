#! /bin/bash
#
# $Id$
#
# Copyright (C) 2004, 2006 by Martin Thorsen Ranang
#

export PATH=$PATH:$HOME/bin
export PYTHONPATH=$PYTHONPATH:$HOME/lib/python
export PYCHART_OPTIONS='scale=1.5 color=yes'

if [ -z "$LOGS" ]; then
    LOGS="/home/tore/export/ttpd.log"
fi

if [ -z "$EXPORT" ]; then
    EXPORT="$HOME/public_html/tucstats"
fi

INTERFACE="SMS"
#HOST="62.70.49.172"
HOST="62.70.49.173"
TRANS_TYPE="LINGSMSIN"

#RESTRICTIONS="interface=$INTERFACE,host=$HOST,trans_type=$TRANS_TYPE"
RESTRICTIONS="interface=$INTERFACE,trans_type=$TRANS_TYPE"
