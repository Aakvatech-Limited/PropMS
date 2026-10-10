import frappe
from frappe.utils.modules import is_module_visible


def has_app_permission():
	"""Apps-screen visibility only; document permissions remain framework-controlled."""
	return frappe.session.user != "Guest" and is_module_visible("Property Management Solution")
