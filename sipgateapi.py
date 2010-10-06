#!/usr/bin/env python
# coding=utf8
"""From:

http://github.com/mbr/sipgate-api
"""

import xmlrpclib

VERSION = '0.1'
SIPGATE_URL = 'https://%(username)s:%(password)s@samurai.sipgate.net/RPC2'

CLIENT_NAME = 'sipgate-api.py'
CLIENT_VENDOR = 'mbr'

PHONE_TO_SIP_TEMPLATE = 'sip:%s@sipgate.de'

class SanityCheckError(Exception): pass

class SipgateAPI(object):
	def __init__(self, username, password, sanity_checks = True):
		# connect
		self.sg = xmlrpclib.Server(SIPGATE_URL % {'username': username, 'password': password})
		self.sanity_checks = sanity_checks

		# identify
		self.sg.samurai.ClientIdentify({'ClientName': CLIENT_NAME,
		                                'ClientVersion': str(VERSION),
		                                'ClientVendor': CLIENT_VENDOR})

	def send_sms(self, recipient_number, text):
		if self.sanity_checks:
			if recipient_number.startswith('0'):
				raise SanityCheckError('Number probably not in E.164 format, since it starts with a zero (should start with country code).')

			if not recipient_number.isdigit():
				raise SanityCheckError('Recipient number must be a string of digits.')

		self.sg.samurai.SessionInitiate({'RemoteUri': PHONE_TO_SIP_TEMPLATE % recipient_number,
		                              'TOS': 'text',
		                              'Content': str(text)})