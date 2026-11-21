"""Company-aware, optional lease taxation helpers.

Explicit Lease and Lease Item selections are checked. Blank selections preserve
the installed ERPNext tax resolution and Company defaults.
"""

import frappe
from frappe import _
from frappe.utils import getdate
from erpnext.stock.get_item_details import get_item_tax_template


def validate_company_tax_template(doctype, template_name, company):
	"""Refuse a selected template that cannot be used for this company."""
	if not template_name:
		return
	if not company:
		frappe.throw(_("Set the Lease Company before selecting a tax template"))
	values = frappe.db.get_value(doctype, template_name, ["company", "disabled"], as_dict=True)
	if not values:
		frappe.throw(_("{0} {1} does not exist").format(doctype, template_name))
	if values.company != company:
		frappe.throw(
			_("{0} {1} belongs to company {2}, not Lease company {3}").format(
				doctype, template_name, values.company, company
			)
		)
	if values.disabled:
		frappe.throw(_("{0} {1} is disabled").format(doctype, template_name))


def resolve_item_tax_template(item_code, company, transaction_date, explicit=None, tax_category=None):
	"""Resolve native ERPNext item/group taxes; preserve legacy blanks.

	Explicit overrides are validated but native item/group rules retain their
	date- and tax-category-aware authority when no override was selected.
	"""
	if explicit:
		validate_company_tax_template("Item Tax Template", explicit, company)
		return explicit
	if not item_code or not company:
		return None
	ctx = frappe._dict(
		item_code=item_code,
		company=company,
		posting_date=getdate(transaction_date),
		transaction_date=getdate(transaction_date),
		tax_category=tax_category,
	)
	resolved = get_item_tax_template(ctx)
	if resolved:
		validate_company_tax_template("Item Tax Template", resolved, company)
	return resolved
