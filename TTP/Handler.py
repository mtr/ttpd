#! /usr/bin/python
# -*- coding: latin-1 -*-
# $Id$
"""
Socket server handler implementation for the TUC Transfer Protocol
(TTP).

Copyright (C) 2004, 2007 by Martin Thorsen Ranang
"""

__version__ = "$Rev$"
__author__ = "Martin Thorsen Ranang"

import Queue
import SocketServer
import cStringIO
import htmlentitydefs
import random
import re
import socket
import time
import xml.sax

import EncapsulateTUC
import LogHandler
import Message
import num_hash


class BaseHandler(SocketServer.StreamRequestHandler):
    def setup(self):
        """Create an XML parser for this handler instance.
        
        Additionally get this requests transaction number.
        """
        # Call the base class setup method.
        SocketServer.StreamRequestHandler.setup(self)
        
        # Initialize the XML parser.  We keep one parser per thread,
        # in an attempt to avoid any shared resource problems.
        self.xml_handler = Message.XML2Message()
        
        self.xml_error_handler = xml.sax.ErrorHandler()
        
        self.xml_parser = xml.sax.make_parser()
        self.xml_parser.setContentHandler(self.xml_handler)
        self.xml_parser.setErrorHandler(self.xml_error_handler)

        # Get a transaction ID.
        self.transaction = self.server.get_next_transaction_id()
        
    def handle(self):
        meta, body = Message.receive(self.connection, self.xml_parser)
        
        self.server.log.log(LogHandler.PROTOCOL, '[%0x], \n%s\n%s',
                            self.transaction, meta, body)
        
        ack = Message.MessageAck()
        ack.MxHead.TransId = 'LINGSMSOUT'
        
        Message.send(self.connection, ack)
        
    def escape(self, data):
        """Replace special characters with escaped equivalents.
        """
        data = data.replace('"', '\\"')

        return data
    
    def unescape(self, data):
        """Replace escaped special characters with unescaped
        equivalents.
        """
        data = data.replace('\\"', '"')
        
        return data

    
class Handler(BaseHandler):
    """A handler class for request received over the TUC Transfer
    Protocol.
    """
    result_separator = '~' * 80
    
    prices = {'+': 'BILLING',
              '-': 'FREE',
              '!': 'VARSEL'}
    
    # According to "Online Interface EAS Message Switch 2.4", a
    # billing value of 1 == 0.5 NOK.
    billings = {'BILLING': 2,
                'FREE': 0,
                'VARSEL': 2,
                'AVBEST': 2,
                'AVBEST_WRONG_ID': 2}
    
    sms_trans_id = 'LINGSMS'            # Followed by 'IN' and 'OUT'.
    
    service_name = 'TEAM'
    
    cancel_command_info = 'Avbestill ved å sende ' \
                          '%s AVBEST %%s til 1939.' % (service_name)
    
    command = 'avbestill'
    # Define COMMAND_MISSPELLINGS as
    #
    #   ['av', 'avb', 'avbe', 'avbes', 'avbest', 'avbesti',
    #    'avbestil', 'avbestill']:
    command_misspellings = [command[:i + 1] for i in xrange(1, len(command))]

    # Set some time values for attempts to resend messages to the
    # remote server.  Time values are given in seconds.
    resend_timeout = 15 * 60
    resend_delay_range = [60 * m for m in [1, 3]]
    
    def setup(self):
        """Setup some thread-specific resources before handling the
        request.
        """
        # Call the base class setup method first.
        BaseHandler.setup(self)
        
        self.whitespace_replace_re = re.compile('\s+', re.MULTILINE)
        self.dangerous_removes_re = re.compile('[\\\´`\'"]', re.MULTILINE)
        self.service_re = re.compile('^(?P<service>%s) (?P<body>.*)$' % \
                                     (self.service_name), re.IGNORECASE)
        self.cancel_command_re = \
                               re.compile('^(?P<command>%s) ' \
                                          '(?P<ext_id>[0-9a-z]+)' %
                                          '|'.join(self.command_misspellings),
                                          re.IGNORECASE)

    def reply_sms(self, ans, answer, cost, meta):
        # The maximum length of an SMS message is 160 tokens.
        if len(answer) > 160:
            answer = answer[:160]

            # If the answer had to be cut down to 160 tokens, it
            # should be free, unless it was an alert-related message.
            if cost != 'VARSEL':
                cost == 'FREE'
                
        ans._setMessage(answer)

        ans.MxHead.ORName = str(meta.MxHead.ORName)
        ans.MxHead.Aux.Billing = self.billings[cost]

        # If necessary, try multiple times to deliver the answer, but
        # we might time out before it's sent.
        sent = False
        retries = 0
        resend_delay = 0
        
        while not sent and (resend_delay < self.resend_timeout):
            try:
                meta, body = \
                      Message.communicate(ans,
                                          self.server.remote_server_address,
                                          self.xml_parser)
                
            except socket.error, desc:
                delta = random.randint(*self.resend_delay_range)
                
                if (resend_delay + delta) > self.resend_timeout:
                    delta = self.resend_timeout - resend_delay
                    
                resend_delay += delta

                # Sleep a little while and try again.
                time.sleep(delta)

                retries += 1
                
                self.server.log.debug('[%0x] Could not connect to ' \
                                      'remote server %s: reason: %s. ' \
                                      'Will retry in %d seconds',
                                      self.transaction,
                                      self.server.remote_server_address,
                                      desc, delta)
                
            else:
                sent = True
                
        if sent:
            if self.server.log.isEnabledFor(LogHandler.PROTOCOL):
                self.server.log.log(LogHandler.PROTOCOL,
                                    '[%0x] Recieved ACK:\n%s\n%s',
                                    self.transaction,
                                    meta, body)
        else:
            self.server.log.error('[%0x] Could not connect to ' \
                                  'remote server %s: reason: %s. ' \
                                  'Even tried %d resends.',
                                  self.transaction,
                                  self.server.remote_server_address,
                                  desc, retries)
            
            answer = 'Fikk ikke sendt svaret. ' \
                     'Det opprinnelige svaret var "%s"' % (answer)
            cost = 'FREE'

        return answer, cost

    def reply_web(self, ans, pre_answer, answer):
        # A Web-ish client.  Send the answer back to the same socket
        # we received the request from.
        tuc_ans = Message.Message()

        tuc_ans.TUCAns.Technical = pre_answer, # Becomes a tuple.
        tuc_ans.TUCAns.NaturalLanguage = answer

        ans._setMessage('<?xml version="1.0" encoding="iso-8859-1"?>' \
                        '%s' % (tuc_ans._xmlify()))

        Message.send(self.connection, ans)
        
    def handle(self):
        """Handles a query received by the socket server.
        
        The incoming data is available through self.rfile and feedback
        to the client should be written to self.wfile.  The query is
        first classified.  If it is not a cancelation of an alert, the
        natural language query is 'piped' through TUC.
        
        Depending on the nature of the TUC results, the appropriate
        action is taken.  If it is an alert canelation, the request
        will be handled in another method.
        """
        self.server.log.info('[%0x] Connection from %s:%d.',
                             self.transaction, self.client_address[0],
                             self.client_address[1])
        
        # Retrieve incoming request.
        meta, body = Message.receive(self.connection, self.xml_parser)
        
        # If nothing was received, or there was an error, we skip
        # further processing.
        if not meta:
            if body:
                self.server.log.warn('[%0x] Did not receive complete ' \
                                     'request from %s: %s', self.transaction,
                                     self.client_address, body)
            self.request.close()
            return

        if self.server.log.isEnabledFor(LogHandler.PROTOCOL):
            self.server.log.log(LogHandler.PROTOCOL,
                                '[%0x] Received package:\n%s\n%s',
                                self.transaction, meta, body)
        
        # Remove "dangerous" tokens from the request.
        body = self.dangerous_removes_re.sub('', body)
        
        if meta.MxHead.TransId[:len(self.sms_trans_id)] == self.sms_trans_id:
            is_sms_request = True
            
            # Since it is a SMS request, send an ACK.
            ack = Message.MessageAck()
            ack.MxHead.TransId = meta.MxHead.TransId
            Message.send(self.connection, ack)
            
        else:
            
            is_sms_request = False
            
        # The preprocessing returns a method and some arguments.  The
        # method should be applied on the arguments.
        method, args = self.preprocess(body, is_sms_request)
        
        self.server.log.debug('[%0x] "%s"', self.transaction, body)
        
        # Apply method to args.
        cost, pre_answer, answer, extra = method(args)
        
        # Some special considerations to make when we answer an SMS
        # request.
        if is_sms_request:
            if cost == 'VARSEL':
                alert_date = extra
                
                # Insert the alert into the TAD scheduler.
                id = self.server.tad.insert_alert(time.mktime(alert_date),
                                                  answer[:160],
                                                  str(meta.MxHead.ORName))
                
                # Make the ID's seem a little more random.
                id = (id * 97) + 1003
                
                # Convert the decimal ID into a base 36.
                ext_id = num_hash.num2alpha(id)
                
                answer = 'Du vil bli varslet %s. %s %s' % \
                         (time.strftime('%H:%M:%S, %d.%m.%y', alert_date),
                          self.cancel_command_info % ext_id.upper(), answer)
                
            elif cost == 'AVBEST':
                ext_id = extra
            else:
                ext_id = ''
        else:
            # Non-SMS request for SMS-only services.
            if cost in ['VARSEL', 'AVBEST']:
                tmp = 'Beklager, %s av varsel er ' \
                             'kun mulig via SMS.' % \
                             ({'VARSEL': 'bestilling',
                               'AVBEST': 'avbestilling'}[cost])
                answer = '%s: Du ville blitt varslet %s med meldingen: ' \
                         '%s' % \
                         (tmp,
                          time.strftime('%H:%M:%S, %d.%m.%y', extra), answer)
                
                cost = 'FREE'
                
            ext_id = ''
            
        # Hide "machinery" error messages from the user, but log them
        # for internal use.
        if cost == 'FREE' and (not answer) or answer[0] == '%':
            self.server.log.error('[%0x] "%s"', self.transaction, answer)
            answer = 'Forespørselen ble avbrutt. Vennligst prøv igjen senere.'
            
        # Send the answer to the client.
        ans = Message.MessageResult()
        ans.MxHead.TransId = 'LINGSMSOUT'
        
        # Again, if it is an SMS request we're handling, take special
        # care.
        if is_sms_request:
            answer, cost = self.reply_sms(ans, answer, cost, meta)
            log_id = 'SMS'
            
        else:
            self.reply_web(ans, pre_answer, answer)
            log_id = 'WEB'
            
        # Log some interesting information.  Used for billing and
        # statistics.  The format of the first line is:
        #
        # [transaction_id] billing=<price> <interface> (<host>, <TransId>) <W>
        #
        # Where <W> signifies what kind of action this was.
        self.server.log.info('[%0x] billing=%d %s (%s, %s) %s' \
                             '\n%s %s %s\n' \
                             '"%s"' \
                             '\n"%s"\n-',
                             self.transaction,
                             self.billings[cost],
                             log_id,
                             self.client_address[0],
                             str(meta.MxHead.TransId),
                             cost,
                             log_id,
                             cost,
                             ext_id,
                             body,
                             answer)

        # Close the socket.
        self.request.close()
   
    def parse_result(self, data):
        """Parse the result received from TUC.
        """
        if data.find(self.result_separator) != -1:
            # Split the output from TUC according to its "block
            # separators".
            pre, main, post = data.split(self.result_separator)

            main, post = (block.strip() for block in (main, post))
            
            # The first line of the main block should contain billing
            # and timing information.
            if main[0] in self.prices:
                meta, answer = main.split('\n', 1)
                
                # The first character of meta may not be a cost
                # identifyer.
                cost = self.prices[meta[0]]
            else:
                cost, answer = self.prices['-'], main
        else:
            # If no block separators where found, consider the answer
            # from TUC as a "simple answer" or an error message (like
            # "% Execution aborted").
            self.server.log.debug('[%0x] Found no separator.',
                                  self.transaction)
            
            pre, cost, alert_date, answer = (None, self.prices['-'],
                                             None,
                                             data.rstrip('\nno\n').strip())
            
        answer = self.whitespace_replace_re.sub(' ', answer)
        
        if cost == 'VARSEL':
            alert_date = time.strptime(meta[2:], '%Y%m%d%H%M%S')
        else:
            alert_date = None
            
        # The variable post is deliberately not returned.
        return pre, cost, alert_date, answer
    
    def cancel_alert(self, ext_id):
        """Cancel the alert signified by ext_id.
        """
        num_id = num_hash.alpha2num(ext_id)
        
        if ((num_id - 1003) % 97):
            self.server.log.warn('[%0x] Received non-valid alert ID = "%s"',
                                 self.transaction, ext_id)
            return ('AVBEST_WRONG_ID', None,
                    'Kan ikke avbestille "%s".' % (ext_id), ext_id)
        else:
            num_id = (num_id - 1003) / 97
                
            if self.server.tad.cancel_alert(num_id):
                return ('AVBEST', None, 'Varsling med referanse ' \
                        '%s ble avbestilt.' % (ext_id.upper()), ext_id)
            else:
                return ('FREE', None,
                        'Kunne ikke avbestille. Fant ikke bestilling "%s".'
                        % (ext_id), ext_id)
            
        
    def tuc_query(self, data):
        """Pipe request through TUC and parse the result.
        """
        # Create a thread safe FIFO with a length of 1.  It will only
        # be used to receive the results produced by an encapsulated
        # TUC process (in a thread-safe manner).
        result_queue = Queue.Queue(1)
        
        # Because only the thread that picks up _this_task_ will know
        # about this particular result_queue, we don't need to supply
        # any id with the task.
        self.server.tuc_pool.queue_task((EncapsulateTUC.TYPE_NORMAL, data),
                                        result_queue)

        # Possibly wait some time and retrieve the result from the
        # result_queue.
        result = result_queue.get()
        if not result:
            self.server.log.error('[%0x] Received empty result from ' \
                                  'TUC process', self.transaction)
            result = 'Forespørselen ble avbrutt.  Vennligst prøv igjen senere.'
            
        try:
            pre, cost, alert_date, answer = self.parse_result(result)
        except:
            self.server.log.exception('[%0x] There was a problem handling ' \
                                      'the result:\n%s\nInput: "%s"',
                                      self.transaction, result, data)
            
            pre, cost, alert_date, answer = None, 'FREE', \
                                            None, 'Beklager, ' \
                                            'det oppstod en feil.'
        return cost, pre, answer, alert_date
        
    def preprocess(self, request, is_sms_request = False):
        """Perform pre-processing of the request.
        """
        # Check for (and handle) "TEAM ..." in start of message.
        m = self.service_re.match(request)
        if m:
            # Service should become 'TEAM' here.
            service, body = m.groups()
            
            m = self.cancel_command_re.match(body)
            if m and is_sms_request:
                ext_id = m.group('ext_id').lower()
                return self.cancel_alert, ext_id
            elif m:
                # Return a function that always returns _one_
                # particular result, regardless of its input.  The
                # return values should match those of self.tuc_query
                # and self.cancel_alert.
                return (lambda x: ('AVBEST', None, None)), None
            
            else:
                return self.tuc_query, body
        else:
            return self.tuc_query, request
        
def main():
    """Module mainline (for standalone execution).
    """
    return

if __name__ == "__main__":
    main()
