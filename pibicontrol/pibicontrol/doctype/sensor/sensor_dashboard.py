from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'heatmap': True,
		'heatmap_message': _('This is based on Alerts received from this Sensor'),
		'fieldname': 'sensor',
		'transactions': [
			{
				'label': _('Sensor Readings'),
				'items': ['Sensor Log']
			},
      {
				'label': _('Alerts Received'),
				'items': ['Alert Log']
			}
		]
	}
