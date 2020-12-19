import frappe
import json

@frappe.whitelist()
def get_data(filters):
  filters = json.loads(filters)
  labels = _get_labels()
  datasets = _get_datasets(filters)
  return {
    'labels': labels,
    'datasets': datasets,
  }

def _get_labels():
  return ['CPU T']

def _get_datasets(filters):
  logs = _get_logs(filters)
  return [
    {
      'name': 'CPU T',
      'values': [
        logs,
      ]
    }
  ]

def _get_logs(filters):
  logs = frappe.db.sql(
    """
      SELECT sl.value
      FROM `tabSensor Log` sl
      WHERE sl.docstatus < 2
    """.format(''
    ),
    filters,
    as_dict=1
  )
  return logs