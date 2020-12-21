# -*- coding: utf-8 -*-
# Copyright (c) 2020, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

from frappe import _, msgprint
import json

from pibicontrol.pibicontrol.api import get_alert, mng_alert

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
            if ts.upper_value:
              if float(value) > float(ts.upper_value) and start == True:
                mng_alert(doc, ts.variable, float(value), start, active_alert)
              elif float(value) <= float(ts.upper_value) and start == False:
                mng_alert(doc, ts.variable, float(value), start, active_alert)   
            if ts.lower_value:
              if float(value) < float(ts.lower_value) and start == True:
                mng_alert(doc, ts.variable, float(value), start, active_alert)
              elif float(value) >= float(ts.lower_value) and start == False:
                mng_alert(doc, ts.variable, float(value), start, active_alert)     
          
		  ## Specific Readings taken in payload depending on sensor type
          ## Sensor CPU
          if stock.sensor_type == "cpu":
            ## Secondary CPU Reading    
            if ts.variable == "mem_pct":
              (active_alert, start) = get_alert(ts.variable, doc.name)
              mem_pct = float(payload['payload']['mem']['mem_pct'])
              if ts.upper_value:
                if mem_pct > float(ts.upper_value) and start == True:
                  mng_alert(doc, ts.variable, mem_pct, start, active_alert) 
                elif mem_pct <= float(ts.upper_value) and start == False:
                  mng_alert(doc, ts.variable, mem_pct, start, active_alert) 
              if ts.lower_value:
                if mem_pct < float(ts.lower_value) and start == True:
                  mng_alert(doc, ts.variable, mem_pct, start, active_alert) 
                elif mem_pct >= float(ts.lower_value) and start == False:
                  mng_alert(doc, ts.variable, mem_pct, start, active_alert)
            ## Third CPU Reading    
            elif ts.variable == "disk_pct":
              (active_alert, start) = get_alert(ts.variable, doc.name)
              disk_pct = float(payload['payload']['disk']['disk_pct'])
              if ts.upper_value:
                if disk_pct > float(ts.upper_value) and start == True:
                  mng_alert(doc, ts.variable, disk_pct, start, active_alert)
                elif disk_pct <= float(ts.upper_value) and start == False:
                  mng_alert(doc, ts.variable, disk_pct, start, active_alert)
              if ts.lower_value:
                if  disk_pct < float(ts.lower_value) and start == True:
                  mng_alert(doc, ts.variable, disk_pct, start, active_alert)
                elif disk_pct >= float(ts.lower_value) and start == False:
                  mng_alert(doc, ts.variable, disk_pct, start, active_alert)
          ## Sensor other type  