# -*- coding: utf-8 -*-
# Copyright (c) 2020, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
import json

class SensorLog(Document):
  def before_save(self):
    self.points = len(self.log_item)
    values = []
    for data in self.log_item:
      values.append(data.value)
    self.min = min(values)
    self.max = max(values)
    self.average = sum(values)/len(values)
    
    value = self.log_item[len(self.log_item)-1].value
    mainread = self.log_item[len(self.log_item)-1].main_reading
    doc = frappe.get_doc("Sensor", self.sensor)
    stock = frappe.get_doc("Stock Item", doc.stock_item)
    payload = json.loads(self.log_item[len(self.log_item)-1].payload)
    for ts in doc.threshold_item:
      if ts.active:
        ## Primary Common Reading
        if ts.variable == mainread:
          if float(value) >= float(ts.upper_value):
            frappe.msgprint(_("High value in " + str(mainread)))
        ## Specific Readings taken in payload depending on sensor type
        if stock.sensor_type == "cpu":
          ## Secondary Reading    
          if ts.variable == "mem_pct":
            if float(payload['payload']['mem']['mem_pct']) >= float(ts.upper_value):
              frappe.msgprint(_("High Memory Usage"))
          ## Third Reading    
          elif ts.variable == "disk_pct":
            if float(payload['payload']['disk']['disk_pct']) >= float(ts.upper_value):
              frappe.msgprint(_("High Disk Usage"))  