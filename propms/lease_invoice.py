import json
import traceback

import frappe
import frappe.permissions
import frappe.share
from erpnext.accounts.party import get_due_date
from erpnext.controllers.accounts_controller import get_taxes_and_charges
from frappe import _
from frappe.utils import add_days, add_months, flt, getdate, today


def _item_signature(items):
	"""Compare billable lines, including repeated items and their service periods."""
	return sorted(
		(
			row.get("item_code"),
			flt(row.get("qty"), 6),
			flt(row.get("rate"), 6),
			str(row.get("service_start_date") or ""),
			str(row.get("service_end_date") or ""),
		)
		for row in items
	)


def _existing_invoice(doctype, lease, customer, currency, start_date, end_date, items):
	"""Recover an already saved draft or submitted document after an interrupted run."""
	candidates = frappe.get_all(
		doctype,
		filters={
			"lease": lease,
			"customer": customer,
			"currency": currency,
			"from_date": start_date,
			"to_date": end_date,
			"docstatus": ["<", 2],
		},
		pluck="name",
		order_by="creation asc, name asc",
	)
	for name in candidates:
		existing = frappe.get_doc(doctype, name)
		if _item_signature(existing.items) == _item_signature(items):
			return existing


def _lock_lease(lease):
	"""Serialize manual and scheduled generators until this transaction commits."""
	lease_table = frappe.qb.DocType("Lease")
	return (
		frappe.qb.from_(lease_table)
		.select(lease_table.name)
		.where(lease_table.name == lease)
		.for_update()
	).run()


@frappe.whitelist()
def app_error_log(title, error):
	d = frappe.get_doc(
		{
			"doctype": "Custom Error Log",
			"title": "User:" + str(title),
			"error": traceback.format_exc(),
		}
	)
	d = d.insert(ignore_permissions=True)
	return d


@frappe.whitelist()
def makeInvoice(
	date,
	customer,
	items,
	currency=None,
	lease=None,
	lease_item=None,
	qty=None,
	schedule_start_date=None,
	doctype="Sales Invoice",  # Allow to create Sales Invoice or Sales Order
):
	"""Create sales invoice from lease invoice schedule."""
	if not doctype:
		doctype = "Sales Invoice"
	if doctype not in ("Sales Invoice", "Sales Order"):
		frappe.throw(_("Only Sales Invoice or Sales Order can be generated from a lease"))
	frappe.db.savepoint("lease_invoice_create")
	try:
		if not customer:
			frappe.throw(_("Please select a Customer in Lease {0}").format(lease))
		company = frappe.get_value("Lease", lease, "company")
		default_tax_template = frappe.get_value("Company", company, "default_tax_template")
		if qty != int(qty):
			# it means the last invoice for the lease that may have fraction of months
			subs_end_date = frappe.get_value("Lease", lease, "end_date")
		else:
			# month qty is not fractional
			subs_end_date = add_days(add_months(schedule_start_date, qty), -1)
		items_data = frappe.parse_json(items)
		_lock_lease(lease)
		existing = _existing_invoice(
			doctype, lease, str(customer), currency, schedule_start_date, subs_end_date, items_data
		)
		if existing:
			return existing
		is_accrued = any(item.get("enable_deferred_revenue") for item in items_data)
		invoice_posting_date = date if (is_accrued and date) else today()
		doc = frappe.get_doc(
			dict(
				doctype=doctype,
				company=company,
				posting_date=invoice_posting_date,
				set_posting_time=1 if is_accrued else 0,
				items=items_data,
				customer=str(customer),
				due_date=getDueDate(invoice_posting_date, str(customer)),
				currency=currency,
				lease=lease,
				lease_item=lease_item,
				taxes_and_charges=default_tax_template,
				from_date=schedule_start_date,
				to_date=subs_end_date,
				cost_center=getCostCenter(lease),
			)
		)
		if doc.doctype == "Sales Order":
			sales_order_date = doc.from_date
			doc.transaction_date = sales_order_date
			doc.posting_date = sales_order_date
			doc.delivery_date = doc.to_date
			if not doc.due_date or getdate(doc.due_date) < getdate(sales_order_date):
				doc.due_date = sales_order_date
		doc.set_missing_values()
		if doc.taxes_and_charges:
			getTax(doc)
		doc.calculate_taxes_and_totals()
		doc.insert()

		if doctype == "Sales Order" and frappe.db.get_single_value(
			"Property Management Settings", "auto_submit_sales_order"
		):
			doc.submit()

		# Check if auto submit is enabled in Property Management Settings
		if doctype == "Sales Invoice" and frappe.db.get_single_value(
			"Property Management Settings", "auto_submit_sales_invoice"
		):
			doc.submit()

		return doc
	except Exception:
		# A failed submission must not leave a fresh draft for the next retry.
		frappe.db.rollback(save_point="lease_invoice_create")
		raise


@frappe.whitelist()
def getTax(sales_invoice):
	# set_missing_values/insert may already populate the template. Never append it twice.
	if sales_invoice.get("taxes"):
		return
	taxes = get_taxes_and_charges("Sales Taxes and Charges Template", sales_invoice.taxes_and_charges)
	for tax in taxes:
		sales_invoice.append("taxes", tax)


@frappe.whitelist()
def getDueDate(date, customer):
	return get_due_date(
		date,
		"Customer",
		str(customer),
		frappe.db.get_single_value("Global Defaults", "default_company"),
		date,
	)


@frappe.whitelist()
def getCostCenter(name):
	property_name = frappe.db.get_value("Lease", name, "property")
	return frappe.db.get_value("Property", property_name, "cost_center")


@frappe.whitelist(methods=["POST"])
def leaseInvoiceAutoCreate():
	"""Generate each due group independently; a failed tenant never blocks the rest."""
	invoice_start_date = frappe.db.get_single_value("Property Management Settings", "invoice_start_date")
	if not invoice_start_date:
		frappe.throw(_("Please set Invoice Start Date in Property Management Settings"))
	rows = frappe.get_all(
		"Lease Invoice Schedule",
		filters={
			"date_to_invoice": ["between", (invoice_start_date, today())],
			"invoice_number": ["is", "not set"],
			"sales_order_number": ["is", "not set"],
		},
		fields=[
			"name", "parent", "paid_by", "invoice_item_group",
			"date_to_invoice", "currency", "document_type",
		],
		order_by="parent, paid_by, invoice_item_group, date_to_invoice, currency, name",
	)
	groups = {}
	for row in rows:
		key = (
			row.parent, row.paid_by, row.invoice_item_group,
			str(row.date_to_invoice), row.currency, row.document_type or "Sales Invoice",
		)
		groups.setdefault(key, []).append(row.name)

	result = {"generated": [], "failed": []}
	for key, names in groups.items():
		frappe.db.savepoint("lease_invoice_group")
		try:
			invoice = _create_schedule_group(key[0], names)
			frappe.db.commit()
			if invoice:
				result["generated"].append(invoice.name)
		except Exception:
			# Undo both the document and schedule links before recording the error.
			frappe.db.rollback(save_point="lease_invoice_group")
			message = frappe.get_traceback()
			frappe.log_error(title="Lease Invoice Auto Create failed", message=message)
			result["failed"].append({"lease": key[0], "schedules": names})
			frappe.db.commit()
	return result


def _create_schedule_group(lease_name, schedule_names):
	_lock_lease(lease_name)
	# Re-read after the lock: another worker may already have processed these rows.
	schedules = [frappe.get_doc("Lease Invoice Schedule", name) for name in schedule_names]
	pending = [row for row in schedules if not row.invoice_number and not row.sales_order_number]
	if not pending:
		return
	if len(pending) != len(schedules):
		frappe.throw(_("Partially linked invoice group requires review for Lease {0}").format(lease_name))

	lease_end_date = frappe.get_value("Lease", lease_name, "end_date")
	company = frappe.get_value("Lease", lease_name, "company")
	items = []
	for row in pending:
		start_date = row.schedule_start_date or row.date_to_invoice
		end_date = (
			lease_end_date if row.qty != int(row.qty)
			else add_days(add_months(start_date, row.qty), -1)
		)
		item = {
			"item_code": row.lease_item,
			"qty": row.qty,
			"rate": row.rate,
			"cost_center": getCostCenter(lease_name),
			"withholding_tax_rate": row.tax,
			"service_start_date": str(start_date),
			"service_end_date": str(end_date),
		}
		item_doc = frappe.get_cached_doc("Item", row.lease_item)
		item["enable_deferred_revenue"] = int(bool(item_doc.enable_deferred_revenue))
		if item_doc.enable_deferred_revenue:
			account = frappe.get_cached_value(
				"Item Default", {"parent": row.lease_item, "company": company}, "deferred_revenue_account"
			) or frappe.get_cached_value("Company", company, "default_deferred_revenue_account")
			if account:
				item["deferred_revenue_account"] = account
		items.append(item)

	last = pending[-1]
	invoice = makeInvoice(
		last.date_to_invoice, last.paid_by, json.dumps(items), last.currency,
		lease_name, last.lease_item, last.qty,
		last.schedule_start_date or last.date_to_invoice,
		doctype=last.document_type or "Sales Invoice",
	)
	link_field = "invoice_number" if invoice.doctype == "Sales Invoice" else "sales_order_number"
	for row in pending:
		frappe.db.set_value("Lease Invoice Schedule", row.name, link_field, invoice.name)
	return invoice


@frappe.whitelist(methods=["POST"])
def enqueue_lease_invoice_auto_create():
	"""Enqueue leaseInvoiceAutoCreate as a background job on the 'long' queue."""
	frappe.enqueue("propms.lease_invoice.leaseInvoiceAutoCreate", queue="long", now=False)
	return "Lease invoice auto creation has been queued. You will be notified once done."

