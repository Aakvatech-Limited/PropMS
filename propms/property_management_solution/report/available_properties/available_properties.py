"""Available properties based on master classification and effective lease occupancy."""

import frappe

from propms.property_status_utils import is_property_available_for_lease


def execute(filters=None):
	columns = [
		{"label": "Property", "fieldname": "name", "fieldtype": "Link", "options": "Property", "width": 220},
		{"label": "Status", "fieldname": "status", "fieldtype": "Link", "options": "Property Status", "width": 180},
		{"label": "Property Type", "fieldname": "type", "fieldtype": "Data", "width": 160},
	]
	filters = filters or {}
	rows = frappe.get_all("Property", filters={"is_group": 0}, fields=["name", "status", "type"])
	return columns, [row for row in rows if is_property_available_for_lease(row.name)
		and (not filters.get("property") or row.name == filters.get("property"))]
