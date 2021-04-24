# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "pibicontrol"
app_title = "Pibicontrol"
app_publisher = "PibiCo"
app_description = "IoT Control on Frappe"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "pibico.sl@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/pibicontrol/css/pibicontrol.css"
# app_include_js = "/assets/pibicontrol/js/pibicontrol.js"

# include js, css files in header of web template
# web_include_css = []
# web_include_js = "/assets/pibicontrol/js/pibicontrol.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "pibicontrol.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "pibicontrol.install.before_install"
# after_install = "pibicontrol.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "pibicontrol.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

jenv = {
  "methods": [
    "timestamp_to_date:pibicontrol.jinja_filters.timestamp_to_date"
  ]
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
 	"cron": {
    "*/9 * * * *": [
 		  "pibicontrol.pibicontrol.api.ping_devices_via_mqtt"
 	  ],
    "*/15 * * * *": [
 		  "pibicontrol.pibicontrol.api.check_web_services"
 	  ],  
    "15 0 * * *": [
      "pibicontrol.pibicontrol.api.create_xls_report"
    ]  
  }
# 	"daily": [
# 		"pibicontrol.tasks.daily"
# 	],
# 	"hourly": [
# 		"pibicontrol.tasks.hourly"
# 	],
# 	"weekly": [
# 		"pibicontrol.tasks.weekly"
# 	]
# 	"monthly": [
# 		"pibicontrol.tasks.monthly"
# 	]
 }

# Testing
# -------

# before_tests = "pibicontrol.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "pibicontrol.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "pibicontrol.task.get_dashboard_data"
# }

default_mail_footer = """
    <div>
        Sent via <a href="http://assistant.pibico.es:8080" target="_blank">Assistant</a>
    </div>
"""

fixtures = ['Report', 'Role Profile', 'Role', 'Custom Field', 'Custom Script', 'Property Setter', 'Workflow', 'Workflow State', 'Workflow Action', 'Translation']