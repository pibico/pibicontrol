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
    datasets = []
    if context.sensor_doc:
      for item in context.sensor_doc:
        ## Recover last Data Log
        log = frappe.db.sql("""
        SELECT * FROM `tabSensor Log` WHERE sensor=%s AND docstatus<2 ORDER BY creation DESC LIMIT 1""", item.sensor_shortcut, True)
        if log:
          sensor_log = frappe.get_doc("Sensor Log", log[0].name)
          logs.append(sensor_log)
          label = []
          main_read = []
          second_read = []
          third_read = []
          for row in sensor_log.log_item:
            label.append(row.datadate.strftime(CHART_FORMAT))
            main_read.append(row.value)
            var1 = row.main_reading
            uom1 = row.uom
            if "cpu-" in item.sensor_shortcut:
              second_read.append(json.loads(row.payload)['payload']['mem']['mem_pct'])
              third_read.append(json.loads(row.payload)['payload']['disk']['disk_pct'])
              var2 = 'mem_pct'
              uom2 = '%'
              var3 = 'disk_pct'
              uom3 = '%'
            elif "th-" in item.sensor_shortcut:
              second_read.append(json.loads(row.payload)['payload']['reading']['val_humid'])
              var2 = 'env_humid'
              uom2 = '%'
          
          """ We construct for charts the following dict
          chart = [
            {
              "sensor": "sensor_shortcut",
              "points": "points",
              "average": "average",
              "min": "min",
              "max": "max",
              "label": [],
              "dataset": [
                [{ "name": "main_read", "values": [] }],
                [{ "name": "second_read","values": [] }],
                [{ "name": "third_read","values": [] }],   
              ]
            }
          ]"""
          
          main = {}
          dataset = []
          main['main_read'] = var1
          main['uom'] = uom1
          main['values'] = main_read
          dataset.append(main)
          if len(second_read) > 0:
            second = {}
            second['second_read'] = var2
            second['uom'] = uom2
            second['values'] = second_read
            dataset.append(second)
          if len(third_read) > 0:
            third = {}
            third['third_read'] = var3
            third['uom'] = uom3
            third['values'] = third_read
            dataset.append(third)
          chart = {} 
          chart['sensor'] = log[0].sensor
          chart['points'] = log[0].points
          chart['average'] = log[0].average
          chart['min'] = log[0]['min']
          chart['max'] = log[0]['max'] 
          chart['label'] = label
          chart['dataset'] = dataset
          datasets.append(chart)
          
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
      context.datasets = datasets
      
    ## Get Location and Weather for Client Logged In
    weather_set = frappe.get_doc("Weather Settings", "Weather Settings")
    if customer:
      ## json.loads(customer[0].location).features[0].geometry.coordinates
      strloc = json.loads(customer[0].location)
      jsonloc = json.dumps(strloc['features'][0], indent = 4)
      location = json.loads(jsonloc)['geometry']['coordinates']
      lat = str(location[1])
      lon = str(location[0])
    else:
      lat = '43.53507'
      lon = '-5.65995'
    url = weather_set.weather_url
    apikey = weather_set.api_key
    base_url = url + "?lat=" + lat + "&lon=" + lon + "&units=metric&appid=" + apikey + "&exclude=minutely,hourly&mode=json"
    req = requests.get(base_url)
    if not req.content:
      context.weather = {}
    else:  
      # We only want the data associated with the "response" key
      context.weather = json.loads(req.content.decode('utf-8'))    