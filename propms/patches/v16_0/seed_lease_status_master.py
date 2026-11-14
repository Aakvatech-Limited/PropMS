"""Seed legacy lease statuses after Lease Status DocType has been synced."""

import frappe


STATUSES = {
	"Draft": (0, 0),
	"Upcoming": (0, 1),
	"Active": (1, 1),
	"Expired": (0, 0),
	"Closed": (0, 0),
	"Not Materialized": (0, 0),
	"Renewal to Previous Lease": (1, 1),
	"Adendum to Previous Lease": (1, 1),
	"Vacating": (1, 1),
	"Terminated": (0, 0),
}


def execute():
	for name, (active, blocks_overlap) in STATUSES.items():
		if not frappe.db.exists("Lease Status", name):
			frappe.get_doc({
				"doctype": "Lease Status",
				"status_name": name,
				"is_active_lease": active,
				"blocks_overlapping_leases": blocks_overlap,
			}).insert(ignore_permissions=True)
