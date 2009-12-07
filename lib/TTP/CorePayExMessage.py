#! /usr/bin/python
# -*- coding: iso-8859-15 -*-
# Modified 25-may-2007. Kristian Skarbø, kristian@lingit.no.
""" 
Implementerer et grensesnitt mot PayEx' Web Service-løsning for utgående SMS.
Copyright (C) 2007 LingIT AS (http://lingit.no).

API-dokumentasjon for PayEx' Web Service finnes på http://pim.payex.com/ 
(brukernavn: download, passord: loaddown). Selve grensesnittet defineres i 
external.payex.com-pxsms.wsdl, som kan lastes ned fra samme sted.

Siste fra Cirkus PayEx:
> Det er visst blitt gjort en endring på PIM sidene. Ikke helt heldig
> timing iforhold til dere dessverre. PxSms er flyttet til:
>
> http://pim.payex.com/AdditionalFunctions.html 

Merk at PayEx har en "testserver", men denne har ulikt kontonummer, ulik 
krypteringsnøkkel (ja, SMS-ene må krypteres), og implementerer ikke tjenesten
slik den er beskrevet på pim.payex.com. Så denne kan vi se bort fra.

Hver av tjenermaskinene til PayEx har administrasjonsgrensesnitt på hhv.
https://test.payex.com/Admin/Default.aspx (testserver) og
https://secure.payex.com/Admin/Default.aspx (produksjonsserver)


OPPSETT PÅ BUSSTUC.LINGIT.NO

Vi må legge til IP-adressa til busstuc-serveren i IP-filteret på PayEx'
administrasjonsnettside: 193.71.196.213.

Siden vi ikke har rottilgang på busstuc-serveren må vi sette opp ekstrapakker
i hjemmeområder. Vi bruker kontoen "tore".

Vi bruker Zolera SOAP Infrastructure (ZSI) for å snakke med Web Services, se 
http://pywebsvcs.sourceforge.net/. ZSI trenger videre PyXML, se 
http://pyxml.sourceforge.net/.

Installasjon:

    tar -xvzf ZSI-2.0.tar.gz
    cd ZSI-2.0
    python setup.py install --home=$HOME
    
    tar -xvzf PyXML-0.8.4.tar.gz
    cd PyXML-0.8.4
    python setup.py install --home=$HOME

ZSI kan nå generere python-kode fra .wsdl-filer:

    $ wsdl2py --file=external.payex.com-pxsms.wsdl
    $ ls
    external.payex.com-pxsms.wsdl PxSms_services.py PxSms_services_types.py 

Vi putter så disse filene i en katalog og importerer dem som en pakke.


BRUK

For å sende SMS-er med PayExMessage opprettes først en instans p, og så kalles
metoden p.sendMessage med argumentene destination, user_data, price og 
order_id.

Ved suksess returneres tuppelen (code, description, transactionStatus, 
transactionNumber) med verdier i henhold til PayEx' spesifikasjoner.
        
Eks. på returverdi ved vellykket sending: 
        
    (u'OK', u'OK', 0, u'16693180')
        
Ved feil returneres None.


FLYTEN BAK KULISSENE

For å sende en SMS gjennom PxSms gjør vi følgende:

(1) Sender en forespørsel til PxSms.SendCpa(). Det eneste interessante som 
returneres herfra er en transaksjonsreferanse. 

(2) Sender forespørseler til PxSms.Check med transaksjonsreferansen som
parameter inntil en respons indikerer suksess eller timeout. 

Både SendCpa() og Check() returnerer følgende parameter:

"code                String
Indicates the result of the request, returns OK if request is successful. 
This does NOT indicate wether the transaction requested was successful or not,
only wether the Sale request was carried out successfully.

description         String
A literal description explaining the result. Returns "OK" if request is 
successful.

transactionStatus   Integer
0=Sale, 1=Initialize, 2=Credit, 3=Authorize, 4=Cancel,5=Failure,6=Capture.
This field needs to be validated by the merchant to verify wether the 
transaction was successful or not.

transactionRef	    String
This parameter is only returned if the parameter is successful, and returns a 
32bit, hexadecimal value(value (Guid) identifying the transactionRef
Example: 129Aa9Aa7Dd12Cc4624419AAaa153Cc56Bb89Cc12

transactionNumber	String
Returns the transaction number if the transaction is successful. This is useful
for support reference as this is the number available in the merchant admin 
view and also the transaction number presented to the end user."

"""

# Antall sekunder vi sjekker status på sendte SMS-er.  PayEx anbefaler
# 30.
CHECK_TIMEOUT_SECONDS = 60

# Antall sekunder mellom hver sjekk av status på sendte SMS-er.
CHECK_INTERVAL_SECONDS = 6

# Kode-streng før vi mottar bekreftelse på mottak av SMS.
CODE_WAITING_FOR_DELIVERY = "Sms_WaitingForDeliveryNotification"

# Returverdier som angir en vellykket sending.
CODE_SUCCESS = "OK"
DESCRIPTION_SUCCESS = "OK"
STATUS_SUCCESS = 0

# Returverdier som angir en vellykket sending av en gratis-SMS.
LA_CODE_SUCCESS = "OK"
LA_DESCRIPTION_SUCCESS = "OK"

# Tegnsett for generering av MD5-hash.
HASH_ENCODING = "iso-8859-1"

# Tegnsett strengene vi får inn er kodet i.
import sys
INPUT_ENCODING = sys.stdin.encoding

import hashlib
from time import sleep
from xml.dom.minidom import parseString
import logging

import payex_prod.PxSms_client
import payex_test.PxSms_client
  
class ezXmlParser(object):
    """ Miniparser for å lese svar fra PayEx. 
    """
    def __init__(self): 
        self._dom = None
        
    def parse(self, xml):
        if self._dom is not None:
            self._dom.unlink()  #bryter opp evt. sirkulære referanser
        self._dom = parseString(xml)
    
    def getNodeByName(self, n):
        """ Returnerer teksten fra en node uten (andre) barn.
        """
        nl = self._dom.getElementsByTagName(n)
        #hvis noden ikke finnes er nl lik []
        if len(nl) == 1:
            try:
                return nl[0].firstChild.data
            except AttributeError:
                pass
        return ""


class PayExMessage(object):
    """ Klasse som implementerer en melding til PayEx.
    """
    remote_service = {
        'production': payex_prod.PxSms_client,
        'test': payex_test.PxSms_client,
        }
    
    def __init__(self, account_number, encryption_key, originating_address,
                 log, remote_service_type, trace_file=None):
        self.log = log
        
        # Define which Web Service interface to use.
        self.wsi = self.remote_service[remote_service_type]
        
        # Account number from PayEx.
        self.account_number = account_number
        
        # Encryption key from PayEx.
        self.encryption_key = encryption_key

        # The number that the SMS gets sent from.
        self.originating_address = originating_address
        
        # "Data coding scheme". 0 = settes ikke
        self.dcs = u"0"
        # Tid før SMS-en foreldes. 0 = settes ikke
        self.validity_time = u"0"

        if trace_file is None:
            self._trace_stream = None
        else:
            self._trace_stream = open(trace_file, 'a')
            
        # Oppretter proxyinstans.
        self._locator = self.wsi.PxSmsLocator()
        self._pxsmssoap = \
                        self._locator.getPxSmsSoap(tracefile=self._trace_stream)
        
        # Oppretter parser-instans.
        self._xp = ezXmlParser()
        
        self._cpa_request = None
        self._check_request = None
        self._la_request = None

        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug("PxSmsSoap_address = '%s'",
                           self._locator.PxSmsSoap_address)

    def __del__(self):
        if self._trace_stream is not None:
            self._trace_stream.close()
            
    def _parseCheckResult(self, xml):
        """ Returnerer tuppelen (code, description, transaction_status, 
        transaction_number).
        """
        self._xp.parse(xml)
        code = self._xp.getNodeByName("code")
        description = self._xp.getNodeByName("description")
        transaction_status = int(self._xp.getNodeByName("transactionStatus"))
        transaction_number = self._xp.getNodeByName("transactionNumber")
        return code, description, transaction_status, transaction_number

    def _parseSendCpaResult(self, xml):
        """ Returnerer tuppelen (transaction_ref, code, description).
        """
        self._xp.parse(xml)
        transaction_ref = self._xp.getNodeByName("transactionRef")
        code = self._xp.getNodeByName("code")
        description = self._xp.getNodeByName("description")
        return transaction_ref, code, description

    def _parseSendLaResult(self, xml):
        """ Returnerer tuppelen (code, description).
        """
        self._xp.parse(xml)
        code = self._xp.getNodeByName("code")
        description = self._xp.getNodeByName("description")
        return code, description


    def _sendCpaRequest(self):
        """ Sender en CPA-forespørsel (premium) til PayEx' SMS-gateway.
        Returnerer tuppelen (code, description, transactionStatus, 
        transactionNumber) med verdier i henhold til PayEx' spesifikasjoner.
        
        Eks. på returverdi ved vellykket sending: 
        
            (u'OK', u'OK', 0, u'16693180')
        
        Kaster RuntimeError ved feil.
        
        I henhold til anbefalt prosedyre fra PayEx sendes så en 
        Check-forespørsel hvert tredje sekund i 30 sekunder, eller inntil
        forespørselen returnerer med en annen kode enn strengen 
        'Sms_WaitingForDeliveryNotification'. 
        """
        res = self._pxsmssoap.SendCpa(self._cpa_request)

        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug("_SendCpaResult = '%s'", res._SendCpaResult)
        
        tref, cpa_code, cpa_desc = self._parseSendCpaResult(res._SendCpaResult)

        if tref == "":
            msg = "SendCpa missing transactionRef.\nCode: '%s'\n" \
                  "Description: '%s'\n_SendCpaResult = '%s'\n" \
                  "self._cpa_request.__dict__= '%s'\n" \
                  % (cpa_code, cpa_desc, res._SendCpaResult, 
                     repr(self._cpa_request.__dict__))

            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug(msg)
            
            raise RuntimeError, msg
        
        else:
            wait = 0
            code, desc, tstatus, tnumber = "", "", "", ""
            self._populateCheckRequest(tref)
            
            while wait < CHECK_TIMEOUT_SECONDS:
                if self.log.isEnabledFor(logging.DEBUG):
                    self.log.debug("Sending check request...")
                
                cres = self._pxsmssoap.Check(self._check_request)
                code, desc, tstatus, tnumber \
                      = self._parseCheckResult(cres._CheckResult)
                
                if code != CODE_WAITING_FOR_DELIVERY:
                    if self.log.isEnabledFor(logging.DEBUG):
                        self.log.debug('PxSms.Check:\n code: %s\n' \
                                       'description: %s\n' \
                                       'transaction_status: %s\n' \
                                       'transaction_number: %s',
                                       code, desc, tstatus, tnumber)
                    
                    if ((code == CODE_SUCCESS) and 
                        (desc == DESCRIPTION_SUCCESS) and 
                        (tstatus == STATUS_SUCCESS)): 

                        return (code, desc, tstatus, tnumber)
                    else:
                        break
                else:
                    wait = wait + CHECK_INTERVAL_SECONDS

                    if self.log.isEnabledFor(logging.DEBUG):
                        self.log.debug("%s: Skal sove i %s sekunder.",
                                       strftime("%Y-%b-%d %H:%M:%S", gmtime()),
                                       CHECK_INTERVAL_SECONDS)
                        
                    sleep(CHECK_INTERVAL_SECONDS)
                    
                    if self.log.isEnabledFor(logging.DEBUG):
                        self.log.debug("%s: Ferdig å sove.",
                                       strftime("%Y-%b-%d %H:%M:%S", gmtime()))

            
            msg = "TIMEOUT PxSms.Check. code: %s, description: %s, " + \
                    "transaction_status: %s, transaction_number: %s" \
                    % (code, desc, tstatus, tnumber)

            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug(msg)
                
            raise RuntimeError, msg

    def _sendLaRequest(self):
        """ Sender en LA-forespørsel (gratis) til PayEx' SMS-gateway.
        Returnerer tuppelen (code, description) med verdier i henhold til 
        PayEx' spesifikasjoner.
        
        Eks. på returverdi ved vellykket sending: 
        
            (u'OK', u'OK')
        
        Kaster RuntimeError ved feil.
        
        Fra PayEx-manualen: 
        
        code        String
        Indicates the result of the request, returns OK if request is 
        successful. This does NOT indicate wether the transaction requested 
        was successful or not, only wether the Sale request was carried out 
        successfully.
        
        description String
        A literal description explaining the result. Returns "OK" if request 
        is successful.
        
        ---
        
        Merk at mine tester tyder på at vi IKKE vil oppnå suksess i henhold til
        manualen, siden vi ser ut til å bare få returnert strengen
        
            "Waiting for deliveryNotification  SmsStatus 1"
            
        istedenfor "OK" i "description"-feltet. Eks:
        
        <?xml version="1.0" encoding="utf-8" ?><payex>
        <header name="Payex Header v1.0">
        <id>b2e16ba92c454e3b880db4b70d498245</id>
        <date>2007-05-08 20:32:32</date></header>
        <status><code>OK</code><description>Waiting for deliveryNotification  
        SmsStatus 1</description><paramName /></status></payex>
        
        
        Og det ser ikke ut til å være definert noe grensesnitt for å sjekke 
        status på LA-meldinger. De er jo gratis...
        """
        res = self._pxsmssoap.SendLa(self._la_request)

        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug("_SendLaResult = '%s'\n", res._SendLaResult)
        
        code, desc = self._parseSendLaResult(res._SendLaResult)

        if (code != LA_CODE_SUCCESS):
            msg = "SendLa failed. Code: %s, Description: %s" % (code, desc)

            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug(msg)
                
            raise RuntimeError, msg
        
        return code, desc
    
    def _get_md5_hash(self, string):
        string = string.encode(HASH_ENCODING)

        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug("encryption_key = '%s'\n" \
                           "string = '%s'", self.encryption_key, string)
        
        string = string + self.encryption_key.encode(HASH_ENCODING)
        hashed = hashlib.md5(string).hexdigest().upper()

        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug("hash = '%s'", hashed)
        
        return hashed

    def _get_md5_hash_for_cpa_request(self, obj):
        """ Returnerer MD5-hash av en CPA-forespørsel <obj>.
        I henhold til PayEx' spesifikasjon skal dette være en heksadesimal 
        MD5-hash av  
            accountNumber + orderId + productNumber + description + 
            orginatingAddress + destination + userData + dataHeader + 
            price + dcs + validityTime + deliveryTime
        Krypteringsnøkkelen skal legges til denne strengen før hashing.
        Merk at strengene skal være latin-1 for hash-formål, men ellers 
        alltid UTF-8.
        """
        s = u"".join([unicode(obj._accountNumber), obj._orderId, 
                      obj._productNumber, obj._description, 
                      obj._originatingAddress, obj._destination, 
                      obj._userData, obj._dataHeader, obj._price, 
                      obj._dcs, obj._validityTime, 
                      obj._deliveryTime])


        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug("Hashing CPA request...")
            self.log.debug("account_number = '%s'", obj._accountNumber)
        
        return self._get_md5_hash(s)

    def _get_md5_hash_for_check_request(self, obj):
        """ Returnerer MD5-hash av en Check-forespørsel <obj>.
        I henhold til PayEx' spesifikasjon skal dette være en heksadesimal 
        MD5-hash av  
            accountNumber + transactionRef
        Krypteringsnøkkelen skal legges til denne strengen før hashing.
        Merk at strengene skal være latin-1 for hash-formål, men ellers 
        alltid UTF-8.
        """
        s = u"".join([unicode(x)
                      for x in (obj._accountNumber, obj._transactionRef)])

        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug("Hashing Check request...")
            self.log.debug("account_number = '%s', transactionRef = '%s'",
                           obj._accountNumber, obj._transactionRef)
        
        return self._get_md5_hash(s)

    def _get_md5_hash_for_la_request(self, obj):
        """ Returnerer MD5-hash av en LA-forespørsel <obj>.
        I henhold til PayEx' spesifikasjon skal dette være en heksadesimal 
        MD5-hash av  
            accountNumber + orderId + productNumber + description + 
            orginatingAddress + addressAlpha + destination + userData + 
            dataHeader + dcs + validityTime + deliveryTime 
        Krypteringsnøkkelen skal legges til denne strengen før hashing.
        Merk at strengene skal være latin-1 for hash-formål, men ellers 
        alltid UTF-8.
        
        Vi trenger ikke addressAlpha, så vi antar bare at den er tom.
        """
        s = u"".join([unicode(obj._accountNumber), obj._orderId, 
                      obj._productNumber, obj._description, 
                      obj._originatingAddress, obj._destination, 
                      obj._userData, obj._dataHeader,  
                      obj._dcs, obj._validityTime, 
                      obj._deliveryTime])

        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug("Hashing LA request...")
            self.log.debug("account_number = '%s'", obj._accountNumber)
        
        return self._get_md5_hash(s)
    
    def _populateCpaRequest(self, destination, user_data, price, order_id, 
                            enc=INPUT_ENCODING):
        """ Oppretter en forespørselinstans for PxSms.SendCpa.
        """
        req = self.wsi.SendCpaSoapIn()
        req._accountNumber = int(self.account_number)
        req._orderId = unicode(order_id, enc)
        req._productNumber = u""
        req._description = u""
        req._originatingAddress = self.originating_address
        req._destination = unicode(destination, enc)
        req._userData = unicode(user_data, enc)
        req._dataHeader = u""
        req._price = unicode(price, enc)
        req._dcs = self.dcs
        req._validityTime = self.validity_time
        req._deliveryTime = u""
        req._hash = self._get_md5_hash_for_cpa_request(req)
        self._cpa_request = req

    def _populateCheckRequest(self, transaction_ref):
        """ Oppretter en forespørselinstans for PxSms.Check.
        """
        req = self.wsi.CheckSoapIn()
        req._accountNumber = int(self.account_number)
        req._transactionRef = transaction_ref
        req._hash = self._get_md5_hash_for_check_request(req)
        self._check_request = req

    def _populateLaRequest(self, destination, user_data, order_id, 
                           enc=INPUT_ENCODING):
        """ Oppretter en forespørselinstans for PxSms.SendLa.
        """
        req = self.wsi.SendLaSoapIn()
        req._accountNumber = int(self.account_number)
        req._orderId = unicode(order_id, enc)
        req._productNumber = u""
        req._description = u""
        req._originatingAddress = self.originating_address
        #addressAlpha
        req._destination = unicode(destination, enc)
        req._userData = unicode(user_data, enc)
        req._dataHeader = u""
        req._dcs = self.dcs
        req._validityTime = self.validity_time
        req._deliveryTime = u""
        req._hash = self._get_md5_hash_for_la_request(req)
        self._la_request = req

    def sendMessage(self, destination, user_data, price, order_id, 
                    enc=INPUT_ENCODING):
        """ Sender en SMS til nummeret <destination> med meldingen <user_data>.
        
        Prisen <price> angis i øre:
            "Price of the SMS. It must be submitted in the lowest monetary unit
            of the selected currency. Example: 1000 = 10.00 NOK"
        
        <order_id> er en lokal identifikator for SMS-en.
        
        returnerer tuppelen (code, description, price, destination).
        """
        if (price != "") and (int(price) == 0):
            self._populateLaRequest(destination, user_data, order_id, enc)
            code, description = self._sendLaRequest()
        else:
            try:
                self._populateCpaRequest(destination, user_data, price,
                                         order_id, enc)
            except UnicodeDecodeError, e:
                self.log.exception("Could not populate CPA request " \
                                   "(destination = '%s', user_data = '%s', " \
                                   "price = '%s', " \
                                   "order_id = '%s', enc = '%s').  " \
                                   "[%s]",
                                   destination, user_data, price,
                                   order_id, enc, e)
                
            (code, description, transactionStatus, transactionNumber) \
                   = self._sendCpaRequest()
            
        return code, description, price, destination

def __test():
    print "Oppretter instans: pem = PayExMessage()"
    pem = PayExMessage()
    print "Sender melding: pem.sendMessage(\"4798233020\", \"Dette er ikke en test, nei! ÆØÅæøå\", \"100\", \"666\")"
    res = pem.sendMessage("4798233020", "Dette er ikke en test, nei! ÆØÅæøå", "100", "666")
    print "Returnerte %s" % (repr(res))

__eksempel = """
>>> from PayExMessage import *
>>> pem = PayExMessage()
Initialiserte kode for produksjons-server
PxSmsSoap_address=https://external.payex.com/pxsms/pxsms.asmx
pem.sendMessage("4798233020", "Dette er ikke en test, nei! ÆØÅæøå", "100", "666")                 
Hashing CPA request:
account_number=21217859, encryption_key=PgHzip4b2RH8u43XSE6V
s=2121785966619394798233020Dette er ikke en test, nei! ÆØÅæøå10000
hash=98611EE805AB572BEF5AA5C380567865
_SendCpaResult=
<?xml version="1.0" encoding="utf-8" ?><payex><header name="Payex Header v1.0"><id>93564714f99d45868a5e2a1e01128290</id><date>2007-05-08 08:49:10</date></header><status><code>Sms_WaitingForDeliveryNotification</code><description>OK</description><paramName /></status><transactionStatus>1</transactionStatus><transactionRef>d7b9d0b1ce59483abeae701cf773a52a</transactionRef><transactionNumber>16693147</transactionNumber></payex>
Hashing Check request:
account_number=21217859, encryption_key=PgHzip4b2RH8u43XSE6V
transactionRef=d7b9d0b1ce59483abeae701cf773a52a
string=21217859d7b9d0b1ce59483abeae701cf773a52a
hash=3421BBDADCAF7E73AD8FA0FB36D6DEAE
Sending check request...
Sending check request...
PxSms.Check:
 code: OK
description: OK
transaction_status: 0
transaction_number: 16693147
(u'OK', u'OK', u'0', u'16693147')
>>> 
"""
