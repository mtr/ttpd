#! /bin/bash
#
# $Id$
#
# Copyright (C) 2004, 2006, 2007 by Martin Thorsen Ranang
#

CONFPATH=$HOME/statistics

. $CONFPATH/general_config.sh

RESOLUTION=days
year=`date +%Y`
week=$((`date +%V` - 1))
WEEK=$year,$week
FNAME=last_week_$RESOLUTION

ttpd_analyze $LOGS \
    --unify-client-addresses-to=$UNIFIED_CLIENT_ADDRESS \
    --restrict-to=$RESTRICTIONS \
    --resolution=$RESOLUTION \
    --week=$WEEK \
    --chart=$EXPORT/graphics/$FNAME.png \
    > $EXPORT/$FNAME.txt

RESOLUTION=hours
FNAME=last_week_$RESOLUTION

ttpd_analyze $LOGS \
    --unify-client-addresses-to=$UNIFIED_CLIENT_ADDRESS \
    --restrict-to=$RESTRICTIONS \
    --resolution=$RESOLUTION \
    --week=$WEEK \
    --chart=$EXPORT/graphics/$FNAME.png \
    > $EXPORT/$FNAME.txt
