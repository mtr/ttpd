#! /usr/bin/python
# -*- coding: latin-1 -*-
# $Id: Message.py 662 2007-02-06 13:59:26Z mtr $
"""
An implementation of the TUC Transfer Protocol.

This module contains a TTP message class and an XML parser that
transforms XML into a TTP message.

Copyright (C) 2004, 2007 by Martin Thorsen Ranang
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

__all__ = ['Message',
           'MessageAck',
           'MessageRequest',
           'MessageResult',
           'XML2Message']

log = logging.getLogger('ttpd.core_message')

msg_re = re.compile('^(?P<head><\?xml .*</MxHead>)(?P<body>.*)$',
                    re.MULTILINE | re.DOTALL | re.IGNORECASE)


class Hierarchy(object):
    """Organizes hierarchical data as a tree.
    """

    def __init__(self):
        """Initialize member variables.
        """
        self._class = Hierarchy
        # self._d stores subtrees.
        self._d = {}

    def __getattr__(self, name):
        # Only attributes not starting with "_" are organinzed in the
        # tree.

        #print 'in __getattr__:', name
        
        if not name.startswith("_"):
            return self._d.setdefault(name, self._class())
        raise AttributeError("Object %r has no attribute %s." % (self, name))
    
    def _attributes(self):
        # Return 'leaves' of the data tree.
        return [(s, getattr(self, s))
                for s in dir(self) if not s.startswith("_")]
    
    def _get_leaves(self, prefix = ""):
        # _get_leaves tree, starting with self prefix stores name of
        # tree node above.
        prefix = prefix and prefix + "."
        rv = {}
        atl = self._d.keys()
        for at in atl:
            ob = getattr(self, at)
            #print 'ob =', ob
            trv = ob._get_leaves(prefix + at)
            rv.update(trv)
        for at, ob in self._attributes():
            rv[prefix+at] = ob
        return rv

    def __getstate__(self):
        # For pickling.
        return self._d, self._attributes()
    
    def __setstate__(self, tp):
        # For unpickling.
        d, l = tp
        self._d = d
        for name, obj in l[:]:
            setattr(self, name, obj)

    def __str__(self):
        """Easy to read string representation of data.
        """
        rl = [] 
        for k,v in self._get_leaves().items():
            rl.append('%s = %s' %  (k,v))
        return '\n'.join(rl)


class Message(Hierarchy):
    """A class for representing and handling hierarchally structured
    TTP messages.
    """
    
    def __init__(self, meta=None):
        Hierarchy.__init__(self)
        
        self._class = Message
        self._message = ''
        
        if meta:
            self.__setstate__(meta.__getstate__())
                            
    def _xmlify(self, prefix=""):
        """Return a string that represents the hierarchy as XML
        elements.
        """
        str = ''
        atl = self._d.keys()
        for at in atl:
            obj = getattr(self, at)
            str += '<%s>%s</%s>' % (at, obj._xmlify(), at)
        for at, obj in self._attributes():
            if obj == None:
                obj = ''                # None attributes becomes ''.
            str += '<%s>%s</%s>' % (at, obj, at)
        return str

    def _setMessage(self, message):
        """Set the textual data of this Message.
        """
        self._message = message
        
    def _generate(self, data=''):
        """Generate a string ready to be sent over a network
        connection, accroding to the protocol specifications by
        eSolutions.
        """
        if not data:
            data = self._message
            
        self.MxHead.Len = len(data)
        
        tmp = '<?xml version="1.0"?>%s%s' % (str(self._xmlify()), data)
        
        return '%010d%s' % (len(tmp), tmp)

class MessageAck(Message):
    """A Message with some parameters set according to 'ACK' messages
    of the protocol.
    """
    def __init__(self):
        
        Message.__init__(self)
        
        # Ack = 0 gives an immediate response from Message Switch (no end
        # to end confirmation).
        
        # Ack = 1 returns a response when the message has been processed
        # by the end application.
        
        # Ack = 2 returns a separate message if delivery fails.
        
        # Ack = 3 returns a separate message (report) both if the message
        # fails and when successfully delivered.
        
        self.MxHead.Ack = 0
        
        self.MxHead.Enc = 0        # Always.
        self.MxHead.Pri = 0        # Always.
        
        self.MxHead.ORName = None
        self.MxHead.Ref = 0
        self.MxHead.Stat = 0


class MessageRequest(MessageAck):
    """A Message pre-fit for sending requests.
    """
    def __init__(self):
        MessageAck.__init__(self)

        del self.MxHead.Stat

        
class MessageResult(MessageAck):
    """A Message pre-fit for providing results.
    """
    def __init__(self):
        MessageAck.__init__(self)
        
        self.MxHead.Aux.Billing = 0
        self.MxHead.Aux.InitIf = 'IP'
        self.MxHead.Aux.InitProto = 'REMOTE'


class XML2Message(xml.sax.ContentHandler):
    all_whitespace_re = re.compile('^\s+$')
    
    def startDocument(self):
        self.element_stack = []
        self.buffer_stack = []
        self.data = Message()
    
    def set_current(self, value):
        obj = self.data
        for node in self.element_stack[:-1]:
            obj = getattr(obj, node)
            
        if self.element_stack[-1] not in obj._d:
            setattr(obj, self.element_stack[-1], value)

    def characters(self, content):
        self.buffer_stack[-1].append(content)

    def startElement(self, name, attrs):
        self.element_stack.append(name)
        self.buffer_stack.append([])
        
    def endElement(self, name):
        if len(self.buffer_stack[-1]):
            self.set_current(''.join(self.buffer_stack[-1]))
        else:
            self.set_current(None)

        self.buffer_stack.pop()            
        self.element_stack.pop()

      
def _recv(connection, buf_size, timeout=False):
    """Read bufsize bytes or error on timeout.
    """
    started = time.time()
    buf = ''
    
    while ((buf_size - len(buf)) > 0) and \
              (not timeout or ((time.time() - started) < timeout)):
        buf += connection.recv(buf_size - len(buf))
        
    return buf

def build(data, parser=None):
    """Build a Message object based on an input XML string.
    """
    sinput = cStringIO.StringIO(data)
    inpsrc = xml.sax.InputSource()
    inpsrc.setByteStream(sinput)
    
    if not parser:
        parser = xml.sax.make_parser()
        parser.setContentHandler(XML2Message())
        parser.setErrorHandler(xml.sax.ErrorHandler())
        
    parser.parse(inpsrc)
    
    sinput.close()
    
    return parser.getContentHandler().data

def receive(connection, parser=None, timeout=False, builder=build):
    """Receive a message from a socket connection.
    """
    w = MessageAck()
    w.MxHead.Stat = 10 # Communication problems btw sender and switch.
    
    preamble_len = 10
    len_data = _recv(connection, preamble_len, timeout)

    try:
        data_len = int(len_data)
    except ValueError, info:
        what = '%s: %s' % (sys.exc_info()[0], info)
        
        log.error('Message did not start with a length specifier: %s.', what)
        
        # Try to receive some more data, but not more than 4096 bytes.
        data = len_data + _recv(connection, 4096, 3)
        
        w._setMessage("Server: TTPD.  Error: Malformed input.")
        send(connection, w)
        
        return None, '%s: all = "%s".\n' % (what, data)
    
    data = _recv(connection, data_len, timeout)

    m = msg_re.match(data)
    if m:
        head, body = m.groups()
    else:
        head, body = data, None
        
    try:
        meta = builder(head, parser)
    except xml.sax.SAXParseException, info:
        what = '%s: %s' % (sys.exc_info()[0], info)
        
        log.error(what)

        w._setMessage("Server: TTPD.  Error: %s." % what)
        send(connection, w)
        
        return None, '%s, data = %s.' %  (what, (head, body))
    
    return meta, body


def send(connection, message):
    """Send a message to the remote address.
    """
    connection.send(message._generate())

    
def connect(remote_address):
    """Connect to the remote_address.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(remote_address)
    return s


def communicate(message, remote_address, parser = None, timeout = False):
    """Communicate message and return with the reply.
    """
    connection = connect(remote_address)
    send(connection, message)
    reply = receive(connection, parser, timeout)
    connection.close()
    
    return reply

def main():
    """Module mainline (for standalone execution).
    """
    return


if __name__ == "__main__":
    main()
