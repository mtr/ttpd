#! /bin/bash
#
# $Id$
#
# Copyright (C) 2004, 2007 by Martin Thorsen Ranang
#

CONFPATH=$HOME/statistics

. $CONFPATH/general_config.sh

WEEK=this

RESOLUTION=days
FNAME=this_week_$RESOLUTION

ttpd_analyze $LOGS \
    --unify-client-addresses-to=$UNIFIED_CLIENT_ADDRESS \
    --restrict-to=$RESTRICTIONS \
    --resolution=$RESOLUTION \
    --week=$WEEK \
    --chart=$EXPORT/graphics/$FNAME.png \
    > $EXPORT/$FNAME.txt

RESOLUTION=hours
FNAME=this_week_$RESOLUTION

ttpd_analyze $LOGS \
    --unify-client-addresses-to=$UNIFIED_CLIENT_ADDRESS \
    --restrict-to=$RESTRICTIONS \
    --resolution=$RESOLUTION \
    --week=$WEEK \
    --chart=$EXPORT/graphics/$FNAME.png \
    > $EXPORT/$FNAME.txt
