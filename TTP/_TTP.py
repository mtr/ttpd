#! /usr/bin/python
# -*- coding: latin-1 -*-

""" 
$Id$

An implementation of the TUC Transfer Protocol.

This module contains a TTP message class and an XML parser that
transforms XML into a TTP message.

Copyright (C) 2004 by Martin Thorsen Ranang
"""

__version__ = "$Rev$"
__author__ = "Martin Thorsen Ranang"

import cStringIO
import Queue
import re
import sys
import xml.sax
import copy

class Hierarchy(object):
    
    """ Organizes hierarchical data as a tree. """
    
    def __init__(self):

        """ Initialize member variables. """
        
        # self._d stores subtrees.

        self._class = Hierarchy
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
        
        """ Easy to read string representation of data. """
        
        rl = [] 
        for k,v in self._get_leaves().items():
            rl.append('%s = %s' %  (k,v))
        return '\n'.join(rl)


class Message(Hierarchy):
    
    """ A class for representing and handling hierarchally structured
    TTP messages. """
    
    def __init__(self, meta = None):
        
        Hierarchy.__init__(self)
        
        self._class = Message
        
        if meta:
            self.__setstate__(meta.__getstate__())
                            
    def _xmlify(self, prefix = ""):

        """ Return a string that represents the hierarchy as XML
        elements. """
        
        str = ''
        atl = self._d.keys()
        for at in atl:
            obj = getattr(self, at)
            str += '<%s>%s</%s>' % (at, obj._xmlify(), at)
        for at, obj in self._attributes():
            if obj == None:
                obj = ''                # None attributes becomes ''
            str += '<%s>%s</%s>' % (at, obj, at)
        return str
   
    def _generate(self, data = ''):
        
        """ Generate a string ready to be sent over a network
        connection, accroding to the protocol specifications by
        eSolutions. """
        
        self.MxHead.Len = len(data)
        
        tmp = '<?xml version="1.0"?>%s%s' % (self._xmlify(), data)
        
        return '%010d%s' % (len(tmp), tmp)

class MessageAck(Message):

    """ A Message with some parameters set according to 'ACK'
    messages of the protocol. """

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

    """ A Message pre-fit for sending requests. """
    
    def __init__(self):

        MessageAck.__init__(self)

        del self.MxHead.Stat
        
class MessageResult(MessageAck):

    """ A Message pre-fit for providing results. """
    
    def __init__(self):

        MessageAck.__init__(self)
        
        self.MxHead.Aux.Billing = 0
        self.MxHead.Aux.InitIf = 'IP'
        self.MxHead.Aux.InitProto = 'REMOTE'


class XML2Message(xml.sax.ContentHandler):
    
    all_whitespace_re = re.compile('^\s+$')
    
    def startDocument(self):

        self.stack = []
        self.data = Message() #Hierarchy()
        
    def set_current(self, value):
        
        obj = self.data
        for node in self.stack[:-1]:
            obj = getattr(obj, node)
        setattr(obj, self.stack[-1], value)
        
    def characters(self, content):
        
        if not self.all_whitespace_re.match(content):
            self.set_current(content)
            self.set = True

    def startElement(self, name, attrs):
        
        self.stack.append(name)
        self.set = False
        
    def endElement(self, name):
        
        if self.set == False:
            self.set_current(None)
        self.stack.pop()

def main():
    
    """ Module mainline (for standalone execution). """

    return


if __name__ == "__main__":
    main()
