# -*- coding: utf-8 -*-
# Copyright (c) 2020, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class Sensor(Document):
  pass
  
def get_timeline_data(doctype, name):
	'''Return timeline for messages'''
	return dict(frappe.db.sql('''select unix_timestamp(creation), count(*) from `tabAlert Log` where sensor=%s and creation > date_sub(curdate(), interval 1 year) and docstatus < 2 group by date(creation)''', name))
 
