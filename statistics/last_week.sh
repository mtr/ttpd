#! /bin/bash
#
# $Id$
#
# Copyright (C) 2004 by Martin Thorsen Ranang
#

CONFPATH=$HOME/statistics

. $CONFPATH/general_config.sh

RESOLUTION=days
year=`date +%Y`
week=$((`date +%V` - 1))
WEEK=$year,$week
FNAME=last_week_$RESOLUTION

ttpd_analyze $LOGS \
    --restrict-to=interface=$INTERFACE,host=$HOST,trans_type=$TRANS_TYPE \
    --resolution=$RESOLUTION \
    --week=$WEEK \
    --chart=$EXPORT/graphics/$FNAME.png \
    > $EXPORT/$FNAME.txt

RESOLUTION=hours
FNAME=last_week_$RESOLUTION

ttpd_analyze $LOGS \
    --restrict-to=interface=$INTERFACE,host=$HOST,trans_type=$TRANS_TYPE \
    --resolution=$RESOLUTION \
    --week=$WEEK \
    --chart=$EXPORT/graphics/$FNAME.png \
    > $EXPORT/$FNAME.txt
