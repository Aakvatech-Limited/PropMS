import json
import traceback

import frappe
import frappe.permissions
import frappe.share
from erpnext.accounts.party import get_due_date
from erpnext.controllers.accounts_controller import get_taxes_and_charges
from frappe import _
from frappe.utils import add_days, add_months, getdate, today


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
		if doc.doctype != "Sales Order":
			doc.insert()
		if doc.taxes_and_charges:
			getTax(doc)
		doc.calculate_taxes_and_totals()
		if doc.doctype == "Sales Order":
			doc.insert()
			return doc
		doc.save()

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
	except Exception as e:
		app_error_log(frappe.session.user, str(e))


@frappe.whitelist()
def getTax(sales_invoice):
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


@frappe.whitelist()
def leaseInvoiceAutoCreate():
	"""Prepare data to create sales invoice from lease invoice schedule. This is called from form button as well as daily schedule"""
	try:
		# frappe.msgprint("Started")
		invoice_start_date = frappe.db.get_single_value("Property Management Settings", "invoice_start_date")
		lease_invoice = frappe.get_all(
			"Lease Invoice Schedule",
			filters={
				"date_to_invoice": ["between", (invoice_start_date, today())],
				"invoice_number": "",
				"sales_order_number": "",
			},
			fields=[
				"name",
				"date_to_invoice",
				"invoice_number",
				"sales_order_number",
				"parent",
				"parent",
				"invoice_item_group",
				"lease_item",
				"paid_by",
				"currency",
			],
			order_by="parent, paid_by, invoice_item_group, date_to_invoice, currency, lease_item",
		)
		if not lease_invoice:
			return
		# frappe.msgprint("Lease being generated for " + str(lease_invoice))
		row_num = 1  # to identify the 1st line of the list
		prev_parent = ""
		prev_customer = ""
		prev_invoice_item_group = ""
		prev_date_to_invoice = ""
		lease_invoice_schedule_name = ""
		prev_currency = ""
		invoice_item = None  # previous row, used to flush a completed group
		lease_invoice_schedule_list = []
		item_dict = []
		item_json = {}
		# frappe.msgprint(str(lease_invoice))
		for row in lease_invoice:
			# frappe.msgprint(str(invoice_item.name) + " " + str(invoice_item.lease_item))
			# Check if same lease, customer, invoice_item_group and date_to_invoice.
			# Also should not be 1st row of the list
			# frappe.msgprint(row.parent + " -- " + prev_parent + " -- " + row.paid_by + " -- " + prev_customer + " -- " + row.invoice_item_group + " -- " + prev_invoice_item_group + " -- " + str(row.date_to_invoice) + " -- " + str(prev_date_to_invoice) + " -- " + row.currency + " -- " + prev_currency)
			if (
				not (
					row.parent == prev_parent
					and row.paid_by == prev_customer
					and row.invoice_item_group == prev_invoice_item_group
					and row.date_to_invoice == prev_date_to_invoice
					and row.currency == prev_currency
				)
				and row_num != 1
			):
				# frappe.msgprint("Creating invoice for: " + str(item_dict))
				res = makeInvoice(
					invoice_item.date_to_invoice,
					invoice_item.paid_by,
					json.dumps(item_dict),
					invoice_item.currency,
					invoice_item.parent,
					invoice_item.lease_item,
					invoice_item.qty,
					invoice_item.schedule_start_date,
					doctype=invoice_item.document_type,
				)
				# frappe.msgprint("Result: " + str(res))
				if res:
					# Loop through all list invoice names that were created and update them with same invoice number
					for lease_invoice_schedule_name in lease_invoice_schedule_list:
						# frappe.msgprint("---")
						# frappe.msgprint("The lease invoice schedule " + str(lease_invoice_schedule_name) + " would be updated with invoice number " + str(res.name) )
						frappe.db.set_value(
							"Lease Invoice Schedule",
							lease_invoice_schedule_name,
							"invoice_number" if res.doctype == "Sales Invoice" else "sales_order_number",
							res.name,
						)
					frappe.db.commit()  # commit the changes to the database
					frappe.msgprint(_("Lease Invoice generated with number: {0}").format(res.name))
				item_dict = []
				lease_invoice_schedule_list = []  # reset the list of names of lease_invoice_schedule
				item_json = {}
			# Now that the invoice would be created if required, load the record for preparing item_dict
			invoice_item = frappe.get_doc("Lease Invoice Schedule", row.name)
			if not (invoice_item.schedule_start_date):
				invoice_item.schedule_start_date = invoice_item.date_to_invoice
			lease_end_date = frappe.get_value("Lease", invoice_item.parent, "end_date")
			item_json["item_code"] = invoice_item.lease_item
			item_json["qty"] = invoice_item.qty
			item_json["rate"] = invoice_item.rate
			item_json["cost_center"] = getCostCenter(invoice_item.parent)
			item_json["withholding_tax_rate"] = invoice_item.tax

			# Fetch deferred revenue configuration from Item Master and Item Defaults / Company
			item_doc = frappe.get_cached_doc("Item", invoice_item.lease_item)
			if item_doc.enable_deferred_revenue:
				item_json["enable_deferred_revenue"] = 1
				company = frappe.get_value("Lease", invoice_item.parent, "company")
				deferred_account = frappe.get_cached_value(
					"Item Default",
					{"parent": invoice_item.lease_item, "company": company},
					"deferred_revenue_account",
				) or frappe.get_cached_value("Company", company, "default_deferred_revenue_account")
				if deferred_account:
					item_json["deferred_revenue_account"] = deferred_account
			else:
				item_json["enable_deferred_revenue"] = 0

			item_json["service_start_date"] = str(invoice_item.schedule_start_date)
			if invoice_item.qty != int(invoice_item.qty):
				# it means the last invoice for the lease that may have fraction of months
				subs_end_date = lease_end_date
			else:
				# month qty is not fractional
				subs_end_date = add_days(add_months(invoice_item.schedule_start_date, invoice_item.qty), -1)
			item_json["service_end_date"] = str(subs_end_date)
			# Append to the dictionary as a dict() so that the values for the new row can be set
			item_dict.append(dict(item_json))
			lease_invoice_schedule_list.append(invoice_item.name)

			# Remember the values for the next round
			prev_parent = invoice_item.parent
			prev_customer = invoice_item.paid_by
			prev_invoice_item_group = invoice_item.invoice_item_group
			prev_date_to_invoice = invoice_item.date_to_invoice
			prev_currency = invoice_item.currency
			row_num += 1  # increment by 1
		# Create the last invoice
		res = makeInvoice(
			invoice_item.date_to_invoice,
			invoice_item.paid_by,
			json.dumps(item_dict),
			invoice_item.currency,
			invoice_item.parent,
			invoice_item.lease_item,
			invoice_item.qty,
			invoice_item.schedule_start_date,
			doctype=invoice_item.document_type,
		)
		if res:
			# Loop through all list invoice names that were created and update them with same invoice number
			for lease_invoice_schedule_name in lease_invoice_schedule_list:
				# frappe.msgprint("The lease invoice schedule " + str(lease_invoice_schedule_name) + " would be updated with invoice number " + str(res.name))
				frappe.db.set_value(
					"Lease Invoice Schedule",
					lease_invoice_schedule_name,
					"invoice_number" if res.doctype == "Sales Invoice" else "sales_order_number",
					res.name,
				)
			frappe.db.commit()  # commit the changes to the database
			frappe.msgprint(_("Lease Invoice generated with number: {0}").format(res.name))

	except Exception as e:
		app_error_log(frappe.session.user, str(e))


@frappe.whitelist()
def enqueue_lease_invoice_auto_create():
	"""Enqueue leaseInvoiceAutoCreate as a background job on the 'long' queue."""
	frappe.enqueue("propms.lease_invoice.leaseInvoiceAutoCreate", queue="long", now=False)
	return "Lease invoice auto creation has been queued. You will be notified once done."
