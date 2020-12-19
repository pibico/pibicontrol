frappe.provide('frappe.dashboards.chart_sources');

frappe.dashboards.chart_sources['CPU Log'] = {
    method: 'pibicontrol.pibicontrol.dashboard_chart_source.cpu_log.cpu_log.get_data'
}