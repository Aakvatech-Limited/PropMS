"""Current effective active leases based on the Lease Status master."""

import frappe
from frappe.utils import getdate, nowdate
from pypika import Order

from propms.lease_status_utils import get_active_lease_statuses


def execute(filters=None):
	filters = frappe._dict(filters or {})
	as_on = getdate(filters.get("as_on") or nowdate())
	columns = [
		{"label": "Lease", "fieldname": "name", "fieldtype": "Link", "options": "Lease", "width": 180},
		{"label": "Property", "fieldname": "property", "fieldtype": "Link", "options": "Property", "width": 200},
		{"label": "Lease Status", "fieldname": "lease_status", "fieldtype": "Link", "options": "Lease Status", "width": 190},
		{"label": "Start Date", "fieldname": "start_date", "fieldtype": "Date", "width": 110},
		{"label": "End Date", "fieldname": "end_date", "fieldtype": "Date", "width": 110},
	]
	statuses = get_active_lease_statuses()
	if not statuses:
		return columns, []
	Lease = frappe.qb.DocType("Lease")
	query = (
		frappe.qb.from_(Lease)
		.select(Lease.name, Lease.property, Lease.lease_status, Lease.start_date, Lease.end_date)
		.where(Lease.lease_status.isin(statuses))
		.where(Lease.docstatus < 2)
		.where((Lease.start_date <= as_on) | Lease.start_date.isnull())
		.where((Lease.end_date >= as_on) | Lease.end_date.isnull() | (Lease.skip_end_date == 1))
	)
	if filters.get("property"):
		query = query.where(Lease.property == filters.property)
	return columns, query.orderby(Lease.start_date, order=Order.desc).run(as_dict=True)
