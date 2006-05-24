#! /bin/bash
#
# $Id$
#
# Copyright (C) 2004 by Martin Thorsen Ranang
#

CONFPATH=$HOME/statistics

. $CONFPATH/general_config.sh

RESOLUTION=days
WEEK=this
FNAME=this_week_$RESOLUTION

ttpd_analyze $LOGS \
    --restrict-to=$RESTRICTIONS \
    --resolution=$RESOLUTION \
    --week=$WEEK \
    --chart=$EXPORT/graphics/$FNAME.png \
    > $EXPORT/$FNAME.txt

RESOLUTION=hours
FNAME=this_week_$RESOLUTION

ttpd_analyze $LOGS \
    --restrict-to=$RESTRICTIONS \
    --resolution=$RESOLUTION \
    --week=$WEEK \
    --chart=$EXPORT/graphics/$FNAME.png \
    > $EXPORT/$FNAME.txt