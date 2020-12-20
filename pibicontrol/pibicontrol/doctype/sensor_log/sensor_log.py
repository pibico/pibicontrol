# -*- coding: utf-8 -*-
# Copyright (c) 2020, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

from frappe import _, msgprint
import json
from datetime import datetime

from frappe.utils import cstr
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from pibicontrol.pibicontrol.doctype.telegram_settings.telegram_settings import send_telegram
from pibicontrol.pibicontrol.doctype.mqtt_settings.mqtt_settings import send_mqtt

## Formats for Frappe Client
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S.%f"
DATETIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT

class SensorLog(Document):
  def before_save(self):
    ## Get data parameters from Sensor
    doc = frappe.get_doc("Sensor", self.sensor)
    ## Check if sensor is enabled
    if not doc.disabled:
      ## Initialize
      values = []
      ## Get sensor type from Sensor
      stock = frappe.get_doc("Stock Item", doc.stock_item)
      ## Complete the read only attributes based on taken measures
      self.points = len(self.log_item)
      for data in self.log_item:
        values.append(data.value)
      self.min = min(values)
      self.max = max(values)
      self.average = sum(values)/len(values)
      ## Select the last recorded value, variable and payload coming from outside
      value = self.log_item[len(self.log_item)-1].value
      mainread = self.log_item[len(self.log_item)-1].main_reading
      payload = json.loads(self.log_item[len(self.log_item)-1].payload)
      ## Search in threshold alerts
      for ts in doc.threshold_item:
        ## Check threshold data from active variables
        if ts.active:
          ## Primary Common Reading to all sensors
          if ts.variable == mainread:
            (active_alert, start) = get_alert(ts.variable, doc.name)         
            if ts.upper_value or ts.lower_value:
              if (float(value) > float(ts.upper_value)) or (float(value) < float(ts.lower_value)) and start == True:
                start = True
              elif (float(value) <= float(ts.upper_value)) or (float(value) >= float(ts.lower_value))  and start == False:
                start = False
              mng_alert(self, doc, ts.variable, float(value), start, active_alert)    
          ## Specific Readings taken in payload depending on sensor type
          ## Sensor CPU
          if stock.sensor_type == "cpu":
            ## Secondary CPU Reading    
            if ts.variable == "mem_pct":
              (active_alert, start) = get_alert(ts.variable, doc.name)
              mem_pct = float(payload['payload']['mem']['mem_pct'])
              if ts.upper_value or ts.lower_value:
                if (mem_pct > float(ts.upper_value)) or (mem_pct < float(ts.lower_value)) and start == True:
                  start = True
                elif (mem_pct <= float(ts.upper_value)) or (mem_pct >= float(ts.lower_value)) and start == False:
                  start = False
                mng_alert(self, doc, ts.variable, mem_pct, start, active_alert) 
            ## Third CPU Reading    
            elif ts.variable == "disk_pct":
              (active_alert, start) = get_alert(ts.variable, doc.name)
              disk_pct = float(payload['payload']['disk']['disk_pct'])
              if ts.upper_value or ts.lower_value:
                if  (disk_pct > float(ts.upper_value)) or (disk_pct < float(ts.lower_value)) and start == True:
                  start = True
                elif (disk_pct <= float(ts.upper_value)) or (disk_pct >= float(ts.lower_value)) and start == False:
                  start = False
                mng_alert(self, doc, ts.variable, disk_pct, start, active_alert) 
          ## Sensor other type  

def get_alert(variable, name):
  start = True
  ## Get active alerts for the Sensor based on not having to_time value in record
  last_log = frappe.get_list(
    doctype = "Alert Log",
    fields = ['*'],
    filters = [['date', '=', datetime.now().strftime(DATE_FORMAT)],['docstatus', '<', 2], ['sensor', '=', name], ['variable','=', variable]],
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

def mng_alert(log, sensor, variable, value, start, alert_log):
  if not sensor.disabled and sensor.alerts_active:
    ## Prepare message to send
    if start:
      msg = log.sensor + " Detected AbNormal Value " + str(value) + " in " + variable + ". Please Check!"
    else:
      msg = log.sensor + " Recovered Normal Value " + str(value) + " in " + variable + ". Rest Easy!"
       
    ## Check Active Channels and prepare a thread to alert
    ## Fill main parameters
    doSend = True
    datadate = datetime.now()
    by_sms = by_telegram = by_mqtt = by_email = 0
    sms_list = []
    telegram_list = []
    mqtt_list = []
    email_list = []
    if sensor.sms_alert and sensor.sms_recipients != '':
      alert_sms = "SMS from " + msg 
      #frappe.msgprint(_(alert, sensor.sms_recipients))
      by_sms = 1
      sms_list = sensor.sms_recipients.split(",")
    if sensor.telegram_alert and sensor.telegram_recipients != '':
      alert_telegram = "Telegram from " + msg
      #frappe.msgprint(_(alert, sensor.telegram_recipients))
      by_telegram = 1
      telegram_list = sensor.telegram_recipients.split(",")
    if sensor.mqtt_alert and sensor.mqtt_recipients != '':
      alert_mqtt = "MQTT from " + msg
      #frappe.msgprint(_(alert), sensor.mqtt_recipients)
      by_mqtt = 1
      mqtt_list = sensor.mqtt_recipients.split(",")
    if sensor.email_alert and sensor.email_recipients != '':
      if start:
        subject = "Alert from " + log.sensor
      else:
        subject = "Finished Alert from " + log.sensor  
      alert_email = msg
      #frappe.msgprint(_(alert, sensor.email_recipients))      
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
        if not last_alert.to_time and not start:
          ## Code for update child item in doc
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
        alert_log.sensor = log.sensor
        alert_log.date = datadate.strftime(DATETIME_FORMAT)
        alert_log.variable = variable
        ## Adds log to array  
        alert_log.append("alert_item", alert_json)
        alert_log.save()
        frappe.msgprint(_("[INFO] Created New Log"))
    ## Sending messages to recipients
    if len(sms_list) > 0 and doSend:
      #frappe.msgprint(_("[INFO] Send SMS to " + str(sms_list)))
      send_sms(sms_list, cstr(alert_sms))
    if len(telegram_list) > 0 and doSend:
      #frappe.msgprint(_("[INFO] Send Telegram to " + str(telegram_list)))
      send_telegram(telegram_list, cstr(alert_telegram))
    if len(mqtt_list) > 0 and doSend:
      #frappe.msgprint(_("[INFO] Send MQTT to " + str(mqtt_list)))
      send_mqtt(mqtt_list, cstr(alert_mqtt))
    if len(email_list) > 0 and doSend:
      #frappe.msgprint(_("[INFO] Send Email to " + str(email_list)))
      frappe.sendmail(recipients=email_list, subject=subject, message=cstr(alert_email))
