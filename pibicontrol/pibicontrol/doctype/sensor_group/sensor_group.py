# -*- coding: utf-8 -*-
# Copyright (c) 2020, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.website_generator import WebsiteGenerator

import datetime, json, requests

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S.%f"
CHART_FORMAT = "%H:%M"
DATETIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT

class SensorGroup(WebsiteGenerator):
  def get_context(self, context):
    if self.name == 'PibiGeneral':
      if frappe.session.user == 'Administrator':
        customer = None
        ## Get all CPU
        context.sensor_doc = frappe.db.sql("""
		    SELECT * FROM `tabSensor` WHERE sensor_group=%s AND docstatus<2""", self.name, True)
      else:
        customer = frappe.db.sql("""
        SELECT * FROM `tabClient` WHERE user=%s AND docstatus<2 AND enabled=1""", frappe.session.user, True)
        context.customer = customer
        ## Get CPUs assigned to Client Logged In
        context.sensor_doc = frappe.db.sql("""
        SELECT * FROM `tabSensor` WHERE sensor_group=%s AND docstatus<2 AND client=%s""", (self.name, frappe.session.user), True)
      ## Recover Last Data Log and Active Alerts for sensors assigned to Client or All (for Administrator)
      logs = []
      alerts = []
      if context.sensor_doc:
        for item in context.sensor_doc:
          ## Recover last Data Log
          log = frappe.db.sql("""
          SELECT * FROM `tabSensor Log` WHERE sensor=%s AND docstatus<2 ORDER BY creation DESC LIMIT 1""", item.sensor_shortcut, True)
          if log:
            sensor_log = frappe.get_doc("Sensor Log", log[0].name)
            logs.append(sensor_log)
          ## Recover Alerts (for 5 variables + lastseen)
          sdate = datetime.datetime.now().strftime(DATE_FORMAT)
          alert = frappe.db.sql("""
          SELECT * FROM `tabAlert Log` WHERE sensor=%s AND docstatus<2 and date=%s""", (item.sensor_shortcut, sdate), True)
          if alert:
            for val in alert:
              alert_log = frappe.get_doc("Alert Log", val.name)
              alerts.append(alert_log)
          
        context.sensor_logs = logs
        context.alert_logs = alerts
      ## Get Location and Weather for Client Logged In
      if customer:
        weather_set = frappe.get_doc("Weather Settings", "Weather Settings")
        ## json.loads(customer[0].location).features[0].geometry.coordinates
        strloc = json.loads(customer[0].location)
        jsonloc = json.dumps(strloc['features'][0], indent = 4)
        location = json.loads(jsonloc)['geometry']['coordinates']
        lat = str(location[1])
        lon = str(location[0])
        url = weather_set.weather_url
        apikey = weather_set.api_key
        base_url = url + "?lat=" + lat + "&lon=" + lon + "&units=metric&appid=" + apikey + "&exclude=minutely,hourly&mode=json"
        req = requests.get(base_url)
        if not req.content:
          context.weather = {}
        else:  
          # We only want the data associated with the "response" key
          context.weather = json.loads(req.content.decode('utf-8'))