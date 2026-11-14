"""Seed v16 Property Status Category and Property Status masters without overwriting edits."""

import frappe


CATEGORIES = {
	"Available": (0, 1),
	"Reserved": (0, 0),
	"Occupied": (1, 0),
	"Excluded": (0, 0),
	"Sales": (0, 0),
	"Maintenance": (0, 0),
	"Inactive": (0, 0),
}

# (category, system controlled, blocks new leases, terminal)
STATUSES = {
	"Available": ("Available", 1, 0, 0),
	"Booked": ("Reserved", 0, 1, 0),
	"Common Area (Not for lease)": ("Excluded", 0, 1, 0),
	"Managed for Customer": ("Occupied", 0, 1, 0),
	"Off Lease in 3 Months": ("Occupied", 1, 1, 0),
	"On Lease": ("Occupied", 1, 1, 0),
	"On Sale": ("Sales", 0, 1, 0),
	"Removed": ("Inactive", 0, 1, 1),
	"Renewal": ("Occupied", 0, 1, 0),
	"Sold": ("Inactive", 0, 1, 1),
	"Vacating": ("Occupied", 0, 1, 0),
	"In Renovation": ("Maintenance", 0, 1, 0),
}


def execute():
	# Older sites may retain a Property Setter that forces Select options.
	# Remove only this obsolete setting; keep unrelated customizations intact.
	if frappe.db.exists("Property Setter", "Property-status-options"):
		frappe.delete_doc("Property Setter", "Property-status-options", ignore_permissions=True)
	frappe.clear_cache(doctype="Property")

	for name, (occupied, available) in CATEGORIES.items():
		if not frappe.db.exists("Property Status Category", name):
			frappe.get_doc({"doctype": "Property Status Category", "category_name": name,
				"counts_as_occupied": occupied, "counts_as_available": available}).insert(ignore_permissions=True)
	for name, (category, system, blocks, terminal) in STATUSES.items():
		if not frappe.db.exists("Property Status", name):
			frappe.get_doc({"doctype": "Property Status", "status_name": name,
				"status_category": category, "is_system_controlled": system,
				"blocks_new_leases": blocks, "is_terminal": terminal}).insert(ignore_permissions=True)

	# Retain custom legacy statuses rather than orphaning historical Property links.
	for row in frappe.get_all("Property", fields=["status"], distinct=True):
		name = row.status
		if name and not frappe.db.exists("Property Status", name):
			if not frappe.db.exists("Property Status Category", "Other"):
				frappe.get_doc({"doctype": "Property Status Category", "category_name": "Other"}).insert(ignore_permissions=True)
			frappe.get_doc({"doctype": "Property Status", "status_name": name,
				"status_category": "Other", "is_system_controlled": 0}).insert(ignore_permissions=True)
