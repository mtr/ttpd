#! /usr/bin/python
# -*- coding: latin-1 -*-
# $Id$
"""
Socket server handler implementation for the TUC Transfer Protocol
(TTP).

Copyright (C) 2004 by Martin Thorsen Ranang
"""

__version__ = "$Rev$"
__author__ = "Martin Thorsen Ranang"

import Queue
import SocketServer
import cStringIO
import re
import time
import xml.sax

import TTP.Message
import EncapsulateTUC
import num_hash


class BaseHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        
        meta, body = TTP.Message.receive(self.connection,
                                         self.server.xml_parser)
        
        self.server.log.info('\n%s\n%s' % (meta, body))
        
        ack = TTP.Message.MessageAck()
        ack.MxHead.TransID = meta.MxHead.TransID

        TTP.Message.send(self.connection, ack)
        
    def escape(self, data):

        """ Replace special characters with escaped equivalents. """

        data = data.replace('"', '\\"')

        return data
    
    def unescape(self, data):
        
        """ Replace escaped special characters with unescaped
        equivalents. """

        data = data.replace('\\"', '"')
        
        return data

    
class Handler(BaseHandler):
    
    """ A handler class for request received over the TUC Transfer
    Protocol. """
    
    result_separator = '~' * 80
    
    prices = {'+': 'BILLING',
              '-': 'FREE',
              '!': 'VARSEL'}
    
    billings = {'BILLING': 2,
                'FREE': 0,
                'VARSEL': 2,
                'AVBEST': 2}
    
    whitespace_replace_re = re.compile('\s+', re.MULTILINE)

    cancel_command_info = 'Avbestill ved å sende ' \
                          'TEAM AVBEST %s til 1939.'
    
    command = 'avbestill'
    command_misspellings = [command[:i + 1] for i in range(1,len(command))]
    cancel_command_re = re.compile('team ' \
                                   '(?P<command>%s) ' \
                                   '(?P<ext_id>\S+)' %
                                   '|'.join(command_misspellings),
                                   re.IGNORECASE)

    def handle(self):

        """ Handles a query received by the socket server.
        
        The incoming data is available through self.rfile and feedback
        to the client should be written to self.wfile.  The query is
        first classified.  If it is not a cancelation of an alert, the
        natural language query is 'piped' through TUC.
        
        Depending on the nature of the TUC results, the appropriate
        action is taken.  If it is an alert canelation, the request
        will be handled in another method.  """
        
        self.server.log.debug('Connection from %s:%d.' %
                              (self.client_address[0], self.client_address[1]))

        # Retrieve incoming request.
        
        meta, body = TTP.Message.receive(self.connection,
                                         self.server.xml_parser)
        
        #print meta, body
        if meta.MxHead.TransID == 'LINGSMSOUT':
            #self.rfile.close()
            #self.wfile.close()

            ack = TTP.Message.MessageAck()
            ack.MxHead.TransID = meta.MxHead.TransID
            
            TTP.Message.send(self.connection, ack)
            
        method, args = self.preprocess(body)
        
        self.server.log.debug('"%s"' % body)
        
        cost, answer, extra = method(args)
        
        if cost == 'VARSEL':
            alert_date = extra
            
            id = self.server.tad.insert_alert(time.mktime(alert_date),
                                              answer, None)
            ext_id = num_hash.num2alpha(id)
            
            answer = 'Du vil bli varslet %s. %s %s' % \
                     (time.strftime('%X, %x', alert_date),
                      self.cancel_command_info % ext_id.upper(), answer)
            
        elif cost == 'AVBEST':
            ext_id = extra
        else:
            ext_id = ''
            
        # Hide "machinery" error messages from the user, but log them
        # for internal use.
        
        if cost == 'FREE' and answer[0] == '%':
            self.server.log.error('"%s"' % answer)
            answer = 'Forespørselen ble avbrutt.  Vennligst prøv igjen senere.'
            
        # Send the answer to the client.
        
        ans = TTP.Message.MessageAck()
        ans.MxHead.TransID = meta.MxHead.TransID
        ans._setMessage(answer)

        TTP.Message.communicate(ans, self.server.remote_server_address,
                                self.server.xml_parser)
        
        #self.wfile.write(answer)
        
        # Log any interesting information.
        
        self.server.log.info('billing =%d\n%s %s\n"%s"\n"%s"\n-'
                             % (self.billings[cost], cost, ext_id, body,
                                answer.replace('\n', ' ')))

        # Close the socket.
        
        self.request.close()
   
    def parse_result(self, data):

        """ Parse the result received from TUC. """

        self.server.log.debug('Parsing result: "%s".' % data)
        
        if data.find(self.result_separator) != -1:
            
            # Split the output from TUC according to its "block
            # separators".
            
            pre, main, post = [x.strip() for x in
                               data.split(self.result_separator)]
            
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
            
            self.server.log.debug('Found no separator.')
            
            pre, cost, alert_date, answer = (None, self.prices['-'],
                                             None,
                                             data.rstrip('\nno\n').strip())
            
        answer = self.whitespace_replace_re.sub(' ', answer)
        
        if cost == 'VARSEL':
            alert_date = time.strptime(meta[2:], '%Y%m%d%H%M%S')
        else:
            alert_date = None

        # POST is deliberately not returned.
        
        return pre, cost, alert_date, answer

    def cancel_alert(self, ext_id):
        
        """ Cancel the alert signified by ext_id. """
        
        if self.server.tad.cancel_alert(num_hash.alpha2num(ext_id)):
            return ('AVBEST', 'Varsling med referanse ' \
                    '%s ble avbestilt.' % (ext_id), ext_id)
        else:
            return ('FREE',
                    'Kunne ikke avbestille.  Fant ikke bestilling %s.'
                    % ext_id, ext_id)
        
    def tuc_query(self, data):
        
        """ Pipe request through TUC and parse the result. """
        
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
            self.server.log.error('Received empty result from TUC process')
            result = 'Forespørselen ble avbrutt.  Vennligst prøv igjen senere.'
            
        # self.server.log.debug('result = "%s"' % result)
        
        try:
            pre, cost, alert_date, answer = self.parse_result(result)
        except:
            self.server.log.exception('There was a problem handling ' \
                                      'the result:\n%s\nInput: "%s"'
                                      % (result, data))
            
        return cost, answer, alert_date
    
    def preprocess(self, request):

        """ Perform pre-processing of the request. """
        
        m = self.cancel_command_re.match(request)
        if m:
            ext_id = m.group('ext_id').lower()
            return self.cancel_alert, ext_id
        else:
            return self.tuc_query, request

def main():
    
    """ Module mainline (for standalone execution). """

    return


if __name__ == "__main__":
    main()
