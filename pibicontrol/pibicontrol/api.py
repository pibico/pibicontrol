# -*- coding: utf-8 -*-
# Copyright (c) 2020, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from pibicontrol.pibicontrol.doctype.mqtt_settings.mqtt_settings import send_mqtt
from frappe.utils import cstr

@frappe.whitelist()
def get_image(slide):
  """ Get from database all images associated  """
  data = frappe.db.sql("""
		SELECT * FROM `tabWebsite Slideshow Item` WHERE  parent=%s and docstatus<2""", slide, True)
  return data

def ping_devices_via_mqtt():
  command = "is_alive"
  sensors = frappe.get_list(
    doctype = "Sensor",
    fields = ['hostname'],
    filters = [['docstatus', '<', 2], ['disabled', '=', 0]]
  )
  if sensors:
    hostnames = []
    for device in sensors:
      hostnames.append(device.hostname + "/mqtt")
    send_mqtt(hostnames, cstr(command))
  