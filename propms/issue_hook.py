import frappe
from erpnext.controllers.accounts_controller import get_taxes_and_charges
from erpnext.stock.get_item_details import get_pos_profile
from erpnext.utilities.product import get_price
from frappe import _
from frappe.utils import today

from propms.auto_custom import get_latest_active_lease


def make_transaction(doc, for_self_consumption=False):
	is_grouped = frappe.db.get_single_value("Property Management Settings", "group_maintenance_job_items")
	if not is_grouped:
		is_grouped = 0
	is_grouped = int(is_grouped)
	company = doc.company
	if not company:
		company = frappe.db.get_single_value("Global Defaults", "default_company")
	cost_center = frappe.db.get_value("Property", doc.property_name, "cost_center")
	submit_maintenance_stock_entry = frappe.db.get_single_value(
		"Property Management Settings", "submit_maintenance_stock_entry"
	)
	submit_maintenance_invoice = frappe.db.get_single_value(
		"Property Management Settings", "submit_maintenance_invoice"
	)
	# TODO: Remove this after stability of Stock Entry
	self_consumption_customer = frappe.db.get_single_value(
		"Property Management Settings", "self_consumption_customer"
	)
	if not submit_maintenance_stock_entry:
		submit_maintenance_stock_entry = 0
	submit_maintenance_stock_entry = int(submit_maintenance_stock_entry)
	user_remarks = f"Transaction for Maintenance Job Card {doc.name}"
	lease = get_latest_active_lease(doc.property_name)

	def make_stock_entry(items_list=None, pos=None):
		if not items_list:
			return

		# Create a stock entry for purpose material issue
		stock_entry_doc = frappe.get_doc(
			{
				"doctype": "Stock Entry",
				"stock_entry_type": "Material Issue",
				"purpose": "Material Issue",
				"posting_date": today(),
				"remarks": user_remarks,
				"company": doc.company,
				"items": items_list,
				"from_warehouse": frappe.db.get_single_value("Stock Settings", "default_warehouse"),
			}
		)
		if stock_entry_doc:
			stock_entry_doc.insert(ignore_permissions=True)
			stock_entry_url = frappe.utils.get_url_to_form(stock_entry_doc.doctype, stock_entry_doc.name)
			frappe.flags.ignore_account_permission = True
			if submit_maintenance_stock_entry == 1 and not pos:
				stock_entry_doc.submit()
			if pos:
				frappe.throw(_("POS Stock Entry cannot be created for Self Consumption items"))
			frappe.msgprint(
				_("Stock Entry Created {0}").format(f"<a href='{stock_entry_url}'>{stock_entry_doc.name}</a>")
			)
			for item_row in doc.materials_billed:
				if (
					item_row.item
					and item_row.quantity
					and item_row.material_status == "Self Consumption"
					and not item_row.stock_entry
				):
					item_row.stock_entry = stock_entry_doc.name
					frappe.db.set_value(
						"Issue Materials Billed",
						item_row.name,
						"stock_entry",
						stock_entry_doc.name,
					)
					frappe.db.commit()

	def make_sales_invoice(items_list=None, pos=None, self_customer=None):
		if not items_list or not doc.customer:
			return
		default_tax_template = frappe.db.get_value("Company", company, "default_maintenance_tax_template")
		if not default_tax_template:
			url = frappe.utils.get_url_to_form("Company", company)
			frappe.throw(
				_("Please Setup Default Maintenance Tax Template in {0}").format(
					f"<a href='{url}'>{company}</a>"
				)
			)
		if self_customer:
			invoice_customer = self_consumption_customer
		else:
			invoice_customer = doc.customer
		is_pos = 0
		pos_profile = ""
		naming_series = ""
		if pos:
			user_pos_profile = get_pos_profile(company)
			is_pos = 1
			pos_profile = user_pos_profile.name
			naming_series = user_pos_profile.naming_series
			default_tax_template = user_pos_profile.taxes_and_charges or default_tax_template
		invoice_doc = frappe.get_doc(
			dict(
				is_pos=is_pos,
				pos_profile=pos_profile,
				naming_series=naming_series,
				doctype="Sales Invoice",
				customer=invoice_customer,
				company=company,
				posting_date=today(),
				due_date=today(),
				ignore_pricing_rule=1,
				items=items_list,
				update_stock=1,
				remarks=user_remarks,
				cost_center=cost_center,
				lease=lease,
				taxes_and_charges=default_tax_template,
				job_card=doc.name,
			)
		).insert(ignore_permissions=True)
		invoice_doc.reload()
		if invoice_doc.taxes_and_charges and not pos:
			getTax(invoice_doc)
		invoice_doc.calculate_taxes_and_totals()
		invoice_doc.run_method("set_missing_values")
		invoice_doc.run_method("calculate_taxes_and_totals")
		invoice_doc.save()
		if invoice_doc:
			invoice_url = frappe.utils.get_url_to_form(invoice_doc.doctype, invoice_doc.name)
			invoice_link = f"<a href='{invoice_url}'>{invoice_doc.name}</a>"
			frappe.flags.ignore_account_permission = True
			if submit_maintenance_invoice == 1 and not pos:
				invoice_doc.submit()
			if pos:
				make_sales_pos_payment(invoice_doc, user_pos_profile.name)
				frappe.msgprint(_("POS Sales invoice Created {0}").format(invoice_link))
			else:
				frappe.msgprint(_("Sales invoice Created {0}").format(invoice_link))
			for item_row in doc.materials_billed:
				if (
					item_row.item
					and item_row.quantity
					and item_row.invoiced == 1
					and not item_row.sales_invoice
				):
					item_row.sales_invoice = invoice_doc.name
					frappe.db.set_value(
						"Issue Materials Billed",
						item_row.name,
						"sales_invoice",
						invoice_doc.name,
					)
					frappe.db.commit()

	def getTax(sales_invoice):
		taxes = get_taxes_and_charges("Sales Taxes and Charges Template", sales_invoice.taxes_and_charges)
		for tax in taxes:
			sales_invoice.append("taxes", tax)

	def make_sales_pos_payment(invoice_doc, pos_profile_name):
		default_mode_of_payment = frappe.db.get_value(
			"Sales Invoice Payment",
			{"parent": invoice_doc.name, "default": 1},
			["mode_of_payment", "type", "account"],
			as_dict=1,
		)
		payment_row = invoice_doc.append("payments", {})
		payment_row.mode_of_payment = default_mode_of_payment.mode_of_payment
		payment_row.amount = invoice_doc.grand_total
		payment_row.base_amount = invoice_doc.grand_total
		payment_row.account = default_mode_of_payment.account
		invoice_doc.submit()

	if is_grouped == 1:
		# Make grouped Sales Invoice for POS items
		items = []
		for item_row in doc.materials_billed:
			if (
				item_row.item
				and item_row.quantity
				and item_row.material_status == "Bill"
				and not item_row.sales_invoice
				and item_row.is_pos
			):
				item_dict = dict(
					item_code=item_row.item,
					qty=item_row.quantity,
					rate=item_row.rate,
					cost_center=cost_center,
					item_tax_template=get_taxes_template(item_row.item),
				)
				items.append(item_dict)
				item_row.invoiced = 1
		make_sales_invoice(items, pos=True)

		# Make grouped items Sales Invoice for non-POS items
		items = []
		for item_row in doc.materials_billed:
			if (
				item_row.item
				and item_row.quantity
				and item_row.material_status == "Bill"
				and not item_row.sales_invoice
				and not item_row.is_pos
			):
				item_dict = dict(
					item_code=item_row.item,
					qty=item_row.quantity,
					rate=item_row.rate,
					cost_center=cost_center,
					item_tax_template=get_taxes_template(item_row.item),
				)
				items.append(item_dict)
				item_row.invoiced = 1
		make_sales_invoice(items, pos=False)

	else:  # Not grouped
		# Make Sales Invoice for non-grouped items
		for item_row in doc.materials_billed:
			items = []
			if (
				item_row.item
				and item_row.quantity
				and item_row.material_status == "Bill"
				and not item_row.sales_invoice
			):
				item_dict = dict(
					item_code=item_row.item,
					qty=item_row.quantity,
					rate=item_row.rate,
					cost_center=cost_center,
					item_tax_template=get_taxes_template(item_row.item),
				)
				items.append(item_dict)
				item_row.invoiced = 1
				if item_row.is_pos:
					pos = True
				else:
					pos = False
				make_sales_invoice(items, pos)

	# Make Stock Entry for Self Consumption items
	if for_self_consumption and doc.status == "Closed":
		items = []
		for item_row in doc.materials_billed:
			if (
				item_row.item
				and item_row.quantity
				and item_row.material_status == "Self Consumption"
				and not item_row.stock_entry
			):
				item_dict = dict(
					item_code=item_row.item,
					qty=item_row.quantity,
					rate=item_row.rate,
					cost_center=cost_center,
				)
				items.append(item_dict)
		make_stock_entry(items, False)


@frappe.whitelist()
def get_item_rate(item, customer):
	price_list = frappe.db.get_single_value("Selling Settings", "selling_price_list")
	price_list = price_list or frappe.db.get_value("Customer", customer, "default_price_list")
	customer_group = frappe.db.get_value("Customer", customer, "customer_group")
	company = frappe.db.get_single_value("Global Defaults", "default_company")
	rate = get_price(item, price_list, customer_group, company)
	if rate:
		return rate["price_list_rate"]


@frappe.whitelist()
def get_items_group():
	property_doc = frappe.get_doc("Property Management Settings")
	items_group_list = []
	for items_group in property_doc.maintenance_item_group:
		items_group_list.append(items_group.item_group)
	return items_group_list


def validate_materials_required(doc):
	have_items = 0
	for item in doc.materials_required:
		if item.material_status != "Self Consumption":
			have_items += 1
	if have_items > 0 and doc.status == "Closed":
		frappe.throw(
			_(
				"The materials required has items and so the job card cannot be closed. Please confirm billing status fo the materials required."
			)
		)


def validate(doc, method):
	validate_materials_required(doc)
	make_transaction(doc, for_self_consumption=False)
	if doc.status == "Closed":
		make_transaction(doc, for_self_consumption=True)


def get_taxes_template(item_code):
	item_tax_template = get_taxes_and_charges("Item", item_code)
	if len(item_tax_template) > 0:
		return item_tax_template[0]["item_tax_template"]
	else:
		return ""


@frappe.whitelist()
def get_stock_availability(item_code, company, is_pos):
	warehouse = ""
	if int(is_pos) == 1:
		user_pos_profile = get_pos_profile(company)
		warehouse = user_pos_profile.warehouse
	if not warehouse:
		warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
	latest_sle = frappe.db.sql(
		"""select sum(actual_qty) as  actual_qty
        from `tabStock Ledger Entry`
        where item_code = %s and warehouse = %s
        limit 1""",
		(item_code, warehouse),
		as_dict=1,
	)

	sle_qty = latest_sle[0].actual_qty or 0 if latest_sle else 0
	return sle_qty
