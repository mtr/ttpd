#! /bin/bash
#
# $Id$
#
# Copyright (C) 2004, 2006, 2007 by Martin Thorsen Ranang
#

export PATH=$PATH:$HOME/bin
export PYTHONPATH=$PYTHONPATH:$HOME/lib/python
export PYCHART_OPTIONS='scale=1.5 color=yes'

function log() {
    echo "$(date +%Y%m%d-%H:%M:%S): $0: $1"
}

if [ -z "$LOGS" ]; then
    LOGS="/home/tore/export/ttpd-20050622.log /home/tore/export/ttpd.log"
fi

if [ -z "$EXPORT" ]; then
    EXPORT="$HOME/public_html/tucstats"
fi

INTERFACE="SMS"
#HOST="62.70.49.172"
#HOST="62.70.49.173"
HOST="remote_host"		# Used for unifying.
TRANS_TYPE="LINGSMSIN"

RESTRICTIONS="interface=$INTERFACE,host=$HOST,trans_type=$TRANS_TYPE"
UNIFIED_CLIENT_ADDRESS="$HOST"
#RESTRICTIONS="interface=$INTERFACE,trans_type=$TRANS_TYPE"

log "starting"
