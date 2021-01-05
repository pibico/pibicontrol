# -*- coding: utf-8 -*-
# Copyright (c) 2020, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime, json, subprocess
from frappe import _, msgprint

from frappe.utils import cstr
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from pibicontrol.pibicontrol.doctype.telegram_settings.telegram_settings import send_telegram
from pibicontrol.pibicontrol.doctype.mqtt_settings.mqtt_settings import send_mqtt

import paho.mqtt.client as mqtt
import os, ssl, urllib, time, json
from frappe.utils.password import get_decrypted_password

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S.%f"
CHART_FORMAT = "%H:%M"
DATETIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT

@frappe.whitelist()
def get_image(slide):
  """ Get from database all images associated  """
  data = frappe.db.sql("""
		SELECT * FROM `tabWebsite Slideshow Item` WHERE  parent=%s and docstatus<2""", slide, True)
  return data

@frappe.whitelist()
def switch(value, action):
  sensor = frappe.get_doc("Sensor", value)
  trigger = sensor.trigger_pin
  info = sensor.info_pin
  pos = value.find("-")
  topic = []
  topic.append(sensor.hostname + "/mqtt")
  type = value[:pos]
  msg = type + "_" + action + "(" + str(trigger) + "," + str(info) + ")"
  send_mqtt(topic, cstr(msg))

@frappe.whitelist()
def mqtt_command(host, action):
  topic = []
  topic.append(host + "/mqtt")
  send_mqtt(topic, cstr(action))
  
@frappe.whitelist()
def get_chart_dataset (doc):
  label = []
  main_read = []
  second_read = []
  third_read = []
  second_var = ''
  second_uom = ''
  third_var = ''
  third_uom = ''
  data = frappe.get_doc("Sensor Log", doc)
  #print("data = {}".format(frappe.as_json(data)))
  if data.log_item:
    if len(data.log_item) > 0:
      variable = data.log_item[0].main_reading
      uom = data.log_item[0].uom
      if "cpu-" in data.sensor:
        second_var = "mem_pct"
        second_uom = "%"
        third_var = "disk_pct"
        third_uom = "%"       
      elif "th-" in data.sensor:
        second_var = "env_humid"
        second_uom = "%"
      elif "ut-" in data.sensor:
        second_var = "env_vol"
        second_uom = "l"
      for item in data.log_item:
        main_read.append(item.value)
        label.append(item.datadate.strftime(CHART_FORMAT))
        payload = json.loads(item.payload)
        if "cpu-" in data.sensor:
          second_read.append(payload['payload']['mem']['mem_pct']) 
          third_read.append(payload['payload']['disk']['disk_pct'])
        elif "th-" in data.sensor:
          second_read.append(payload['payload']['reading']['val_humid'])  
        elif "ut-" in data.sensor:
          second_read.append(payload['payload']['reading']['val_vol'])               
    
  return {
    'label': label,
    'main_read': main_read,
    'variable': variable,
    'uom': uom,
    'second_read': second_read,
    'second_var': second_var,
    'second_uom': second_uom,
    'third_read': third_read,
    'third_var': third_var,
    'third_uom': third_uom
  }

def get_alert(variable, name):
  start = True
  ## Get active alerts for the Sensor based on not having to_time value in record
  last_log = frappe.get_list(
    doctype = "Alert Log",
    fields = ['*'],
    filters = [['date', '=', datetime.datetime.now().strftime(DATE_FORMAT)],['docstatus', '<', 2], ['sensor', '=', name], ['variable','=', variable]],
    order_by = 'date desc',
    limit_start = 0,
    limit_page_length = 1
  )
  ## Get last Alert Log
  active_alert = None
  if len(last_log) > 0:
    active_alert = frappe.get_doc("Alert Log", last_log[0].name)
    ## If recorded alert is not closed then will be a starting alert
    if active_alert:
      if not active_alert.alert_item[len(active_alert.alert_item)-1].to_time:
        start = False
  return (active_alert, start)

def mng_alert(sensor, variable, value, start, alert_log):
  """ doc is Sensor, variable is variable, value is actual value for variable, start is True or False whether the alert is beginning or ending, active_alert is active_alert """
  if not sensor.disabled and sensor.alerts_active:
    ## Prepare message to send
    if start:
      if variable == "last_seen":
        msg = sensor.name + " offline. Please check!"
      elif variable == "status":
          msg = sensor.name + ". Sensor has been switched on. Please check!"
      else:
        msg = sensor.name + " detected abnormal value " + str(value) + " in " + variable + ". Please check!"
    else:
      if variable == "last_seen":
        msg = sensor.name + " again online. Rest easy!"
      elif variable == "status":
        msg = sensor.name + ". Sensor has been switched off. Rest easy!"
      else:
        msg = sensor.name + " recovered normal value " + str(value) + " in " + variable + ". Rest easy!"
    ## Check Active Channels and prepare a thread to alert
    ## Fill main parameters
    doSend = True
    datadate = datetime.datetime.now()
    by_sms = by_telegram = by_mqtt = by_email = 0
    sms_list = []
    telegram_list = []
    mqtt_list = []
    email_list = []
    if sensor.sms_alert and sensor.sms_recipients != '':
      alert_sms = "SMS from " + msg 
      by_sms = 1
      sms_list = sensor.sms_recipients.split(",")
    if sensor.telegram_alert and sensor.telegram_recipients != '':
      alert_telegram = "Telegram from " + msg
      by_telegram = 1
      telegram_list = sensor.telegram_recipients.split(",")
    if sensor.mqtt_alert and sensor.mqtt_recipients != '':
      if sensor.mqtt_command:
        alert_mqtt = sensor.mqtt_command
      else:  
        alert_mqtt = "MQTT from " + msg
      by_mqtt = 1
      mqtt_list = sensor.mqtt_recipients.split(",")
    if sensor.email_alert and sensor.email_recipients != '':
      if start:
        subject = "Alert from " + sensor.name
      else:
        subject = "Finished Alert from " + sensor.name
      alert_email = "From " + msg
      by_email = 1
      email_list = sensor.email_recipients.split(",")
    ## Write Data for new Alert
    alert_json = {
      "variable": variable,
      "value": value,
      "from_time": datadate.strftime(DATETIME_FORMAT),
      "to_time": None,
      "by_sms": by_sms,
      "by_telegram": by_telegram,
      "by_mqtt": by_mqtt,
      "by_email": by_email
    }
    if alert_log:
      ##if len(alert_log) > 0:
      last_alert = alert_log.alert_item[len(alert_log.alert_item)-1]
      if alert_log.date.strftime(DATE_FORMAT) == datadate.strftime(DATE_FORMAT):
        ## Code for update child item in doc
        if not last_alert.to_time and not start:
          last_alert.to_time = datadate.strftime(DATETIME_FORMAT)
          alert_log.save()
          frappe.msgprint(_("[INFO] Alert Finished"))
        elif last_alert.to_time and start:
          alert_log.append("alert_item", alert_json)
          alert_log.save()
          frappe.msgprint(_("[INFO] New Alert open"))
        elif not last_alert.to_time and start:
          doSend = False
          frappe.msgprint(_("[INFO] Alert already open"))
    else:
      if start:
        ## Code for creating new doc
        alert_log = frappe.new_doc('Alert Log')
        alert_log.sensor = sensor.name
        alert_log.date = datadate.strftime(DATETIME_FORMAT)
        alert_log.variable = variable
        ## Adds log to array  
        alert_log.append("alert_item", alert_json)
        alert_log.save()
        frappe.msgprint(_("[INFO] Created New Log"))
    ## Sending messages to recipients
    if len(sms_list) > 0 and doSend:
      send_sms(sms_list, cstr(alert_sms))
    if len(telegram_list) > 0 and doSend:
      send_telegram(telegram_list, cstr(alert_telegram))
    if len(mqtt_list) > 0 and doSend:
      send_mqtt(mqtt_list, cstr(alert_mqtt))
    if len(email_list) > 0 and doSend:
      frappe.sendmail(recipients=email_list, subject=subject, message=cstr(alert_email))

def ping_devices_via_mqtt():
  sensors = frappe.get_list(
    doctype = "Sensor",
    fields = ['*'],
    filters = [['docstatus', '<', 2], ['disabled', '=', 0]]
  )
  if sensors:
    command = "is_alive"
    strboot = "boot"
    for device in sensors:
      hostname = []
      hostname.append(device.hostname + "/mqtt")
      lastseen = device.lastseen
      now = datetime.datetime.now()
      pos = device.sensor_shortcut.find("-")
      strcmd = "start_" + device.sensor_shortcut[:pos]
      cmd = "take_" + device.sensor_shortcut[:pos]
      
      if lastseen:
        time_minutes = (now - lastseen).total_seconds()/60
      else:
        time_minutes = 12
        
      if time_minutes <= 5:
        ## Check active last_seen alerts to close
        (active_alert, start) = get_alert("last_seen", device.name)
        if start == False:
          mng_alert(device, 'last_seen', 1, start, active_alert)
      elif 15 >= time_minutes > 5:
        ## Order through MQTT to restart supervisor daemons
        if "cpu-" in device.sensor_shortcut:
          send_mqtt(hostname, cstr(command))
        else:
          send_mqtt(hostname, cstr(cmd))
      elif time_minutes > 15:
        ## Not receiving data from device
        ## Send alert last_seen 0 from_time
        send_mqtt(hostname, cstr(strcmd))
        (active_alert, start) = get_alert("last_seen", device.name)
        if start == True:
          mng_alert(device, 'last_seen', 0, start, active_alert)
      elif time_minutes > 30:
        send_mqtt(hostname, cstr(strboot))