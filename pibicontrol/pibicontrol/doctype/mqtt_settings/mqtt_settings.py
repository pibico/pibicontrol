# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals
import frappe

from frappe import _, throw, msgprint
from frappe.utils import nowdate, cstr

from frappe.model.document import Document
import six
from six import string_types

import paho.mqtt.client as mqtt
import os, ssl, urllib, time, json
from frappe.utils.password import get_decrypted_password

class MQTTSettings(Document):
	pass

@frappe.whitelist()
def send_mqtt(receiver_list, msg, sender_name = '', success_msg = True):
	arg = {
		'receiver_list' : receiver_list,
		'message'		: frappe.safe_decode(msg).encode('utf-8'),
		'success_msg'	: success_msg
	}

	if frappe.db.get_value('MQTT Settings', None, 'broker_gateway'):
		send_via_gateway(arg)
	else:
		msgprint(_("Please Update MQTT Settings"))

def send_via_gateway(arg):
	path = "/home/erpnext/erpnext-prd/sites/" 
	client = frappe.get_doc('MQTT Settings', 'MQTT Settings')

	msg = arg.get('message')

	if len(arg.get('receiver_list')) > 0:
		server = client.broker_gateway
		port = client.port
		user = client.user
		client.secret = get_decrypted_password('MQTT Settings', 'MQTT Settings', 'secret', False)
		secret = client.secret
		do_ssl = client.is_ssl
		if client.ca:
			ca = path + frappe.utils.get_url().replace("http://","").replace("https://","") + client.ca
		if client.client_crt:
			client_crt = path + frappe.utils.get_url().replace("http://","").replace("https://","") + client.client_crt
		if client.client_key:
			client_key = path + frappe.utils.get_url().replace("http://","").replace("https://","") + client.client_key
		port_ssl = client.ssl_port
		# connect to MQTT Broker to Publish Message
		pid = os.getpid()
		client_id = '{}:{}'.format('client', str(pid))
		try:
			backend = mqtt.Client(client_id=client_id, clean_session=True)
			backend.username_pw_set(user, password=secret)
			if do_ssl == True:
				backend.tls_set(ca_certs=ca, certfile=client_crt, keyfile=client_key, cert_reqs=ssl.CERT_REQUIRED, ciphers=None)
				backend.tls_insecure_set(False)
				time.sleep(.5)
				backend.connect(server, port_ssl)
			else:
				backend.connect(server, port)

			payload = cstr(msg)
			for mqtt_topic in arg.get('receiver_list'):
				backend.publish(mqtt_topic, payload)
			backend.disconnect()
		except:
			frappe.msgprint(_("Error in MQTT Broker sending to " + str(arg.get('receiver_list'))))
			#raise
			arg['success_msg'] = False
			pass

		if arg.get('success_msg'):
			frappe.msgprint(_("MQTT sent to following topics: {0}").format("\n" + "\n".join(arg.get('receiver_list'))))
