#! /usr/bin/python
# -*- coding: latin-1 -*-
# $Id$
"""
An implementation of the TUC Transfer Protocol.

This module contains a TTP message class and an XML parser that
transforms XML into a TTP message.

Copyright (C) 2004, 2007, 2009 by Lingit AS
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
import urllib
import urllib2
import xml.sax
import logging

log = logging.getLogger('ttpd.pswincom')

Message = CoreMessage.Message
MessageAck = CoreMessage.MessageAck
MessageRequest = CoreMessage.MessageRequest
MessageResult = CoreMessage.MessageResult
XML2Message = CoreMessage.XML2Message

build = CoreMessage.build
connect = CoreMessage.connect
send = CoreMessage.send
receive = CoreMessage.receive 

def pswincom_communicate(message, remote_address, parser=None, timeout=False):
    """Communicate message and return with the reply.

    Example message:

    {'MxHead.Aux.InitProto': 'REMOTE', 
     'MxHead.Enc': 0, 
     'MxHead.Ack': 0, 
     'MxHead.Stat': 0, 
     'MxHead.Aux.Billing': 2, 
     'MxHead.TransId': 'LINGSMSOUT', 
     'MxHead.ORName': '95853086', 
     'MxHead.Aux.InitIf': 'IP', 
     'MxHead.Ref': 0, 
     'MxHead.Pri': 0,
    }

    According to "Online Interface EAS Message Switch 2.4", a
    billing value of 1 == 0.5 NOK.

    """
    #connection = connect()
    log.debug('message._get_leaves(): %s', message._get_leaves())
    log.debug('message._message: "%s".', message._message)

    remote_address = 'http://sms.pswin.com/http4sms/send.asp'
    
    data = {
        'USER': 'atb2027',
        'PW': 'metiony5',
        'RCV': message.MxHead.ORName,
        'SND': '2027',
        'TARIFF': int(message.MxHead.Aux.Billing * 50),
        'TXT': message._message.decode('utf-8').encode('iso-8859-1'),
        }
    
    stream = urllib2.urlopen(remote_address, urllib.urlencode(data))

    reply = stream.read()
    
    log.debug('Received "%s" from %s.', reply, remote_address)
    
    stream.close()
    
    return (None, None)         # (meta, body)

def communicate(message, remote_address, parser=None, timeout=False):
    """Communicate message and return with the reply.
    """
    if message.MxHead.TransId == 'LINGSMSOUT':
        log.debug('Will send message to the PSWin.com gateway.')
        reply = pswincom_communicate(message, remote_address, parser, timeout)
    else:
        connection = connect(remote_address)
        send(connection, message)
        reply = receive(connection, parser, timeout, build)
        connection.close()
    
        log.debug('reply._get_leaves(): %s', reply._get_leaves())

    return reply
