from __future__ import unicode_literals
from frappe import _

def get_data():
  return [
    {
      "label": _("PibiControl Movements"),
      "icon": "fa fa-star",
      "items": [
        {
          "type": "doctype",
          "name": "Sensor Log",
          "description": _("Sensor Log"),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "Alert Log",
          "description": _("Alert Log"),
          "onboard": 1,
        }
      ]
    },
    {
      "label": _("PibiControl Settings"),
      "icon": "fa fa-star",
      "items": [
        {
          "type": "doctype",
          "name": "Client",
          "description": _("Client"),
          "onboard": 1,
        },  
        {
          "type": "doctype",
          "name": "Sensor",
          "description": _("Sensor"),
          "onboard": 1,
        },    
        {
          "type": "doctype",
          "name": "Sensor Group",
          "description": _("Sensor Group"),
          "onboard": 1,
        },       
        {
          "type": "doctype",
          "name": "Stock Item",
          "description": _("Stock Item"),
          "onboard": 1,
        },    
        {
          "type": "doctype",
          "name": "Sensor Type",
          "description": _("Sensor Type"),
          "onboard": 1,
        },    
        {
          "type": "doctype",
          "name": "Variable",
          "description": _("Measuring Variable"),
          "onboard": 1,
        }
      ]
    },
    {
      "label": _("Alerts Setup"),
      "icon": "fa fa-star",
      "items": [
        {
          "type": "doctype",
          "name": "Weather Settings",
          "description": _("Weather Settings"),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "SMS Settings",
          "description": _("SMS Settings"),
          "onboard": 1,
        },    
        {
          "type": "doctype",
          "name": "Telegram Settings",
          "description": _("Telegram Settings"),
          "onboard": 1,
        },       
        {
          "type": "doctype",
          "name": "MQTT Settings",
          "description": _("MQTT Settings"),
          "onboard": 1,
        },    
        {
          "type": "doctype",
          "name": "Email Account",
          "description": _("Email Account"),
          "onboard": 1,
        }
      ]
    }        
  ]