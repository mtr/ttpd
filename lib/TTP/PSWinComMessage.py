#! /usr/bin/python
# -*- coding: latin-1 -*-
# $Id$
"""
An implementation of the TUC Transfer Protocol.

This module contains a TTP message class and an XML parser that
transforms XML into a TTP message.

Copyright (C) 2004, 2007, 2009 by Martin Thorsen Ranang
"""

__version__ = "$Rev$"
__author__ = "Martin Thorsen Ranang"

import CoreMessage
import cStringIO
import Queue
import re
import socket
import sys
import time
import xml.sax
import logging

log = logging.getLogger('ttpd.pswincom')

Message = CoreMessage.Message
MessageAck = CoreMessage.MessageAck
MessageRequest = CoreMessage.MessageRequest
MessageResult = CoreMessage.MessageResult
XML2Message = CoreMessage.XML2Message
send = CoreMessage.send

def communicate(message, remote_address, parser=None, timeout=False):
    """Communicate message and return with the reply.
    """
    if message.MxHead.TransId == 'LINGSMSOUT':
        log.debug('Will send message to the PSWin.com gateway.')

    connection = connect(remote_address)
    send(connection, message)
    reply = receive(connection, parser, timeout, build)
    connection.close()
    
    return reply
