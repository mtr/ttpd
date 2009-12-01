#! /usr/bin/python
# -*- coding: latin-1 -*-
# $Id: Message.py 662 2007-02-06 13:59:26Z mtr $
"""
An implementation of the TUC Transfer Protocol.

This module contains a TTP message class and an XML parser that
transforms XML into a TTP message.

Copyright (C) 2004, 2007 by Martin Thorsen Ranang

Modified 25-may-2007, Kristian Skarbø, kristian@lingit.no.
"""

__version__ = "$Rev: 662 $"
__author__ = "Martin Thorsen Ranang"

import cStringIO
import logging
import Queue
import re
import socket
import sys
import time
import xml.sax
from contextlib import contextmanager

from CoreMessage import (Message, MessageAck, MessageRequest,
                         MessageResult, XML2Message, send, receive)

from CorePayExMessage import PayExMessage

__all__ = ['Message',
           'MessageAck',
           'MessageRequest',
           'MessageResult',
           'XML2Message']

# These variables are injected from the encapsulating environment:
options = None                        # Current configuration options.
payex_log = None                      # A 'logging' instance.

def setup_module(configuration_options):
    global options
    global payex_log
    
    options = configuration_options
    payex_log = logging.getLogger('ttpd.payex')
    
def _convert_reply(TransId, ORName, Billing):
    """Jukser til noe som ligner på et svar fra det gamle EAS-systemet.
    Returnerer tuppelen (meta, body) akkurat som recieve().
    
    Et typisk resultat fra _recv():

     <?xml version="1.0"?>
     <MxHead>
       <TransId>LINGSMSOUT</TransId>
       <ORName>4798233020</ORName>
       <Pri>0</Pri><Ack>0</Ack><Stat>0</Stat><Ref>0</Ref>
       <Aux>
	 <Billing>2</Billing>
	 <InitIf>IP</InitIf>
	 <InitProto>REMOTE</InitProto>
       </Aux>
       <Enc>0</Enc>
       <Len>1</Len>
     </MxHead>
     C

    """
    head = '<?xml version="1.0"?><MxHead>' \
           '<TransId>%s</TransId>' \
           '<ORName>%s</ORName>' \
           '<Pri>0</Pri><Ack>0</Ack><Stat>0</Stat><Ref>0</Ref>' \
           '<Aux><Billing>%s</Billing>' \
           '<InitIf>IP</InitIf><InitProto>REMOTE</InitProto></Aux>' \
           '<Enc>0</Enc><Len>1</Len></MxHead>' \
           % (TransId, ORName, Billing)
    body = "C"
    
    try:
        meta = build(head)
    except xml.sax.SAXParseException, info:
        what = '%s: %s' % (sys.exc_info()[0], info)
        
        w._setMessage("Server: TTPD.  Error: %s." % what)
        send(connection, w)
        
        return None, '%s, data = %s.' %  (what, (head, body))
    
    return (meta, body)

def communicate(message, remote_address, parser = None, timeout = False):
    """Communicate message and return with the reply.
    
    ENDRINGER
    
    Arbeidshypotesen her er at når message.MxHead.TransId = "LINGSMSOUT",
    så skal det sendes en utgående SMS.
    
    Det som forsøksvis da gjøres er å late som om alt er som før, mens vi
    egentlig sniker SMS-en ut via det nye "forbedrede" PxSms-grensesnittet.
    Forhåpentligvis vil da systemet tikke og gå inntil vi får opphavsmannen
    til å foreta en ordentlig omstrukturering.
    
    """
    try:
        TransId = message.MxHead.TransId
    except:
        TransId = ""
        
    payex_log.warn('TransId = "%s"', TransId)
    
    if TransId == "LINGSMSOUT":
        #Forsøker å sende via PxSMS
    
        destination = orig_ORName = message.MxHead.ORName
        # Gamlesystemet leverer strenger som '4798233020;1939;IPX',
        # der alt foran første semikolon er det aktuelle
        # mobilnummeret.
        sc = destination.find(";")
        if sc > -1:
            destination = destination[:sc]
        
        user_data = message._message
        price = str(int(message.MxHead.Aux.Billing) * 50)
        # FIXME: Det må da være mulig å få tak i en slags ID fra TTP?
        order_id = "777"

        if not options.payex_use_test_server:
            account_number = options.payex_account_number
            encryption_key = options.payex_encryption_key
            remote_service_type = 'production'
        else:
            account_number = options.payex_test_account_number
            encryption_key = options.payex_test_encryption_key
            remote_service_type = 'test'

        pem = PayExMessage(account_number, encryption_key,
                           options.originating_address, payex_log,
                           remote_service_type,
                           trace_file=options.payex_trace_file)

        payex_log.debug('Initialized code for communicating with %s server.',
                        remote_service_type)

        # Selve omrutingen:
        (code, description, Billing, _destination) = \
               pem.sendMessage(destination, user_data, price, order_id)

        # Tilbake til gammelt format på pris.
        Billing = str(int(Billing) / 50)  

        # Faker en respons videre i systemet. Sukk.
        reply = _convert_reply(TransId, orig_ORName, Billing)

        meta, body = reply
            
    else:
        # Bruker gamlemåten.
        connection = connect(remote_address)
        send(connection, message)
        reply = receive(connection, parser, timeout)
        connection.close()

        meta, body = reply

    return reply

def main():
    """Module mainline (for standalone execution).
    """
    return


if __name__ == "__main__":
    main()
