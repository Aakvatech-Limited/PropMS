"""Bootstrap and factories shared by the propms test suite."""

import frappe
from frappe.utils import add_months, now_datetime, nowdate

from propms.tests import TEST_ABBR, TEST_COMPANY


def before_tests():
	"""Run once by the test runner before the propms suite."""
	frappe.clear_cache()
	setup_company()
	enable_all_roles()
	frappe.db.commit()  # nosemgrep


def setup_company():
	from frappe.desk.page.setup_wizard.setup_wizard import setup_complete

	if frappe.db.exists("Company", TEST_COMPANY):
		return

	year = now_datetime().year
	setup_complete(
		{
			"currency": "TZS",
			"full_name": "Test User",
			"company_name": TEST_COMPANY,
			"company_abbr": TEST_ABBR,
			"timezone": "Africa/Dar_es_Salaam",
			"industry": "Service",
			"country": "Tanzania",
			"fy_start_date": f"{year}-01-01",
			"fy_end_date": f"{year}-12-31",
			"language": "english",
			"company_tagline": "Testing",
			"email": "test@propms.local",
			"password": "test",
			"chart_of_accounts": "Standard",
		}
	)


def enable_all_roles():
	from erpnext.setup.utils import enable_all_roles_and_domains

	enable_all_roles_and_domains()


def get_or_create(doctype: str, name: str, values: dict) -> str:
	if frappe.db.exists(doctype, name):
		return name
	doc = frappe.get_doc({"doctype": doctype, **values})
	doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
	return doc.name


def get_customer_group() -> str:
	return frappe.db.get_value("Customer Group", {"is_group": 0}, "name")


def get_territory() -> str:
	return frappe.db.get_value("Territory", {"is_group": 0}, "name")


def create_customer(name: str = "_Test Tenant") -> str:
	return get_or_create(
		"Customer",
		name,
		{
			"customer_name": name,
			"customer_type": "Company",
			"customer_group": get_customer_group(),
			"territory": get_territory(),
		},
	)


def create_uom(name: str = "_Test Month") -> str:
	"""Lease quantities are fractional months, so the UOM must allow fractions."""
	return get_or_create("UOM", name, {"uom_name": name, "must_be_whole_number": 0})


def create_item(code: str = "_Test Rent Item", is_stock_item: int = 0) -> str:
	return get_or_create(
		"Item",
		code,
		{
			"item_code": code,
			"item_name": code,
			"item_group": "All Item Groups",
			"stock_uom": create_uom(),
			"is_stock_item": is_stock_item,
		},
	)


def get_cost_center(company: str | None = None) -> str:
	company = company or TEST_COMPANY
	return frappe.db.get_value("Cost Center", {"company": company, "is_group": 0}, "name")


def create_property(name: str = "_Test Property", **kwargs) -> str:
	company = kwargs.pop("company", TEST_COMPANY)
	values = {
		"name1": name,
		"company": company,
		"cost_center": get_cost_center(company),
		"status": "Available",
	}
	values.update(kwargs)
	return get_or_create("Property", name, values)


def create_lease(property_name: str | None = None, **kwargs):
	"""Insert a Lease with one monthly item. Returns the document."""
	property_name = create_property(property_name) if property_name else create_property()
	customer = kwargs.pop("customer", None) or create_customer()
	item = kwargs.pop("item", None) or create_item()
	start_date = kwargs.pop("start_date", nowdate())
	end_date = kwargs.pop("end_date", add_months(nowdate(), 12))
	currency = frappe.db.get_value("Company", TEST_COMPANY, "default_currency")
	lease_items = kwargs.pop(
		"lease_item",
		[
			{
				"lease_item": item,
				"frequency": "Monthly",
				"amount": 1000,
				"currency_code": currency,
				"paid_by": customer,
				"document_type": "Sales Invoice",
			}
		],
	)
	doc = frappe.get_doc(
		{
			"doctype": "Lease",
			"property": property_name,
			"lease_date": start_date,
			"lease_customer": customer,
			"customer": customer,
			"start_date": start_date,
			"end_date": end_date,
			"notice_period": 30,
			"security_deposit_currency": currency,
			"lease_item": lease_items,
			**kwargs,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc


def set_settings(**values):
	settings = frappe.get_single("Property Management Settings")
	for key, value in values.items():
		settings.set(key, value)
	settings.save(ignore_permissions=True)
	return settings
