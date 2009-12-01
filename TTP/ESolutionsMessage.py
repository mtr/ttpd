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

from CoreMessage import (Message, MessageAck, MessageRequest,
                         MessageResult, XML2Message, communicate,
                         send, receive)
