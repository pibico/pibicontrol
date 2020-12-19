frappe.pages['sensor'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Sensor'),
		icon: "fa fa-anchor",
		single_column: true
	});
	
  frappe.breadcrumbs.add("Pibicontrol")
  
  page.add_menu_item('Sensors', () => frappe.set_route('List', 'Sensor'))
  page.add_menu_item('Logs', () => frappe.set_route('List', 'Sensor Log'))
  
}