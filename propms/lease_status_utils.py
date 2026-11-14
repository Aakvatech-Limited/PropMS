"""Central status classifications for operational lease queries."""

import frappe
from frappe.utils import getdate, nowdate


def get_active_lease_statuses():
	return frappe.get_all("Lease Status", filters={"is_active_lease": 1}, pluck="name")


def get_overlap_blocking_statuses():
	return frappe.get_all("Lease Status", filters={"blocks_overlapping_leases": 1}, pluck="name")


def is_active_lease_status(status):
	return bool(status and frappe.db.get_value("Lease Status", status, "is_active_lease"))


def get_active_leases_for_property(property_name, as_on=None):
	"""Effective, non-cancelled active leases on a specified date."""
	statuses = get_active_lease_statuses()
	if not property_name or not statuses:
		return []
	as_on = getdate(as_on or nowdate())
	Lease = frappe.qb.DocType("Lease")
	return (
		frappe.qb.from_(Lease)
		.select(Lease.name, Lease.start_date, Lease.end_date, Lease.skip_end_date)
		.where(Lease.property == property_name)
		.where(Lease.lease_status.isin(statuses))
		.where(Lease.docstatus < 2)
		.where((Lease.start_date <= as_on) | Lease.start_date.isnull())
		.where((Lease.end_date >= as_on) | Lease.end_date.isnull() | (Lease.skip_end_date == 1))
	).run(as_dict=True)


def get_latest_active_lease(property_name, as_on=None):
	leases = get_active_leases_for_property(property_name, as_on)
	if not leases:
		return None
	return max(leases, key=lambda lease: str(lease.start_date or "")).name
