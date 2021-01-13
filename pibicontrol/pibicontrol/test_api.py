# -*- coding: utf-8 -*-
# Copyright (c) 2020, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

from frappe import _, msgprint
import json, datetime

from frappe.utils import time_diff_in_seconds
from pibicontrol.pibicontrol.api import get_alert, mng_alert

## Formats for Frappe Client
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S.%f"
DATETIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT

def test(sensor):    ## Get data parameters from Sensor
    doc = frappe.get_doc("Sensor", sensor)
    ## Check if sensor is enabled
    if not doc.disabled:
      ## Initialize
      for ts in doc.threshold_item:
        ## Check threshold data from active variables and if not in Off Schedule
        if ts.active:
          ahora = datetime.datetime.now().time().strftime(TIME_FORMAT)
          ahora = datetime.datetime(2020, 1, 11, 1, 13).strftime(TIME_FORMAT)
          from_time = time_diff_in_seconds(ahora, str(ts.off_from_time))
          to_time = time_diff_in_seconds(ahora, str(ts.off_to_time))
          
          if from_time > 0 and to_time < 0:
            print("In Schedule", from_time/60, to_time/60)
          else:
            print("Out of Schedule", from_time/60, to_time/60)  