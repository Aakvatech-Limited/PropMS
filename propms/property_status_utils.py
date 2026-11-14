"""Property classification and lease-aware occupancy reconciliation.

The Property Status master describes operational state, while a qualifying Lease
is the authority for rental occupancy.  Facility-management properties can
count as occupied without implying tenancy or lease billing.
"""

import frappe
from frappe import _
from frappe.utils import add_months, getdate, nowdate

from propms.lease_status_utils import get_active_leases_for_property


def status_info(status):
	if not status:
		return {}
	rows = frappe.get_all(
		"Property Status",
		filters={"name": status},
		fields=["status_category", "is_system_controlled", "blocks_new_leases", "is_terminal"],
		limit=1,
	)
	return rows[0] if rows else {}


def get_statuses_for_category(category):
	return frappe.get_all("Property Status", filters={"status_category": category}, pluck="name")


def get_available_property_statuses():
	categories = frappe.get_all("Property Status Category", filters={"counts_as_available": 1}, pluck="name")
	if not categories:
		return []
	return frappe.get_all("Property Status", filters={"status_category": ["in", categories], "blocks_new_leases": 0, "is_terminal": 0}, pluck="name")


def category_counts_as_occupied(category):
	return bool(category and frappe.db.get_value("Property Status Category", category, "counts_as_occupied"))


def is_occupied_property_status(status):
	return category_counts_as_occupied(status_info(status).get("status_category"))


def is_property_available_for_lease(property_name):
	"""Available in the operational master and not under a currently effective lease."""
	if not property_name:
		return False
	prop = frappe.db.get_value("Property", property_name, ["status", "is_group"], as_dict=True)
	if not prop or prop.is_group:
		return False
	meta = status_info(prop.status)
	return (
		bool(meta.get("status_category") and frappe.db.get_value("Property Status Category", meta["status_category"], "counts_as_available"))
		and not meta.get("blocks_new_leases")
		and not meta.get("is_terminal")
		and not get_active_leases_for_property(property_name)
	)


def get_effective_property_occupancy(property_name):
	"""Occupancy includes facility management, but only actual leases qualify for billing."""
	if not property_name:
		return False
	status = frappe.db.get_value("Property", property_name, "status")
	return bool(is_occupied_property_status(status) or get_active_leases_for_property(property_name))


def desired_system_property_status(property_name, as_on=None):
	"""Return a system-controlled status or None when the current status must be preserved."""
	if not property_name:
		return None
	as_on = getdate(as_on or nowdate())
	current = frappe.db.get_value("Property", property_name, "status")
	info = status_info(current)
	if not info or not info.get("is_system_controlled") or info.get("is_terminal"):
		return None

	leases = get_active_leases_for_property(property_name, as_on)
	if not leases:
		return "Available" if current != "Available" else None

	# Warn only if every effective lease has a finite end date in the warning window.
	# One ongoing/renewed/open-ended lease keeps the property On Lease.
	limit = add_months(as_on, 3)
	expiring = all(
		not lease.skip_end_date and lease.end_date
		and as_on <= getdate(lease.end_date) <= limit
		for lease in leases
	)
	target = "Off Lease in 3 Months" if expiring else "On Lease"
	return target if current != target else None


def reconcile_property_status(property_name, as_on=None):
	"""Safe to run in lease hooks and scheduled jobs; preserves manual status states."""
	target = desired_system_property_status(property_name, as_on)
	if not target:
		return None
	frappe.db.set_value("Property", property_name, "status", target)
	return target


@frappe.whitelist()
def get_current_property_lease(property_name):
	"""Resolve tenant from effective active lease, never merely from the Property status."""
	if not property_name:
		return None
	leases = get_active_leases_for_property(property_name)
	if not leases:
		return None
	# Multiple active leases can be permitted, so do not arbitrarily assign a tenant.
	if len(leases) != 1:
		frappe.throw(_("Property {0} has multiple active leases; select the tenant explicitly.").format(property_name))
	return frappe.db.get_value("Lease", leases[0].name, ["name", "customer"], as_dict=True)


@frappe.whitelist()
def available_properties_kpi():
	Property = frappe.qb.DocType("Property")
	statuses = get_available_property_statuses()
	if not statuses:
		return {"value": 0, "fieldtype": "Int"}
	rows = (
		frappe.qb.from_(Property)
		.select(Property.name)
		.where(Property.is_group == 0)
		.where(Property.status.isin(statuses))
	).run(as_dict=True)
	return {"value": sum(1 for row in rows if is_property_available_for_lease(row.name)), "fieldtype": "Int"}


@frappe.whitelist()
def occupied_properties_kpi():
	Property = frappe.qb.DocType("Property")
	rows = (
		frappe.qb.from_(Property)
		.select(Property.name)
		.where(Property.is_group == 0)
	).run(as_dict=True)
	return {"value": sum(1 for row in rows if get_effective_property_occupancy(row.name)), "fieldtype": "Int"}
