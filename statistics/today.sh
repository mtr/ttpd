#! /bin/bash
#
# $Id$
#
# Copyright (C) 2004 by Martin Thorsen Ranang
#

CONFPATH=$HOME/statistics

. $CONFPATH/general_config.sh

RESOLUTION=days
START=`date +%Y-%m-%d`
END=`date +%Y-%m-%d`
FNAME=today_$RESOLUTION

ttpd_analyze $LOGS \
    --restrict-to=interface=$INTERFACE,host=$HOST,trans_type=$TRANS_TYPE \
    --resolution=$RESOLUTION \
    --from=$START --to=$END \
#    --chart=$EXPORT/graphics/$FNAME.png \
    > $EXPORT/$FNAME.txt

RESOLUTION=hours
FNAME=today_$RESOLUTION

ttpd_analyze $LOGS \
    --restrict-to=interface=$INTERFACE,host=$HOST,trans_type=$TRANS_TYPE \
    --resolution=$RESOLUTION \
    --from=$START --to=$END \
    --chart=$EXPORT/graphics/$FNAME.png \
    > $EXPORT/$FNAME.txt
