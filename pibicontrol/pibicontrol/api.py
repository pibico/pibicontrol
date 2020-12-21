# -*- coding: utf-8 -*-
# Copyright (c) 2020, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from pibicontrol.pibicontrol.doctype.mqtt_settings.mqtt_settings import send_mqtt
from frappe.utils import cstr
import datetime

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S.%f"
DATETIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT

@frappe.whitelist()
def get_image(slide):
  """ Get from database all images associated  """
  data = frappe.db.sql("""
		SELECT * FROM `tabWebsite Slideshow Item` WHERE  parent=%s and docstatus<2""", slide, True)
  return data

def ping_devices_via_mqtt():
  sensors = frappe.get_list(
    doctype = "Sensor",
    fields = ['hostname','lastseen'],
    filters = [['docstatus', '<', 2], ['disabled', '=', 0]]
  )
  if sensors:
    hostnames = []
    command = "is_alive"
    for device in sensors:
      lastseen = device.lastseen
      now = datetime.datetime.now()
      time_minutes = (now - lastseen).total_seconds()/60
      if 10 >= time_minutes > 5:
        hostnames.append(device.hostname + "/mqtt")
        send_mqtt(hostnames, cstr(command))
      elif time_minutes > 10:
        frappe.msgprint("[INFO] Not receiving data from " + device.hostname)