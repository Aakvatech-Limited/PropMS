import frappe
from frappe.tests import IntegrationTestCase

from propms.issue_hook import (
	get_item_rate,
	get_items_group,
	get_stock_availability,
	get_taxes_template,
	validate,
	validate_materials_required,
)
from propms.tests import TEST_COMPANY
from propms.tests.utils import create_customer, create_item, create_lease, create_property, set_settings


def get_tax_template() -> str:
	name = frappe.db.get_value("Sales Taxes and Charges Template", {"company": TEST_COMPANY}, "name")
	if name:
		return name
	account = frappe.db.get_value(
		"Account", {"company": TEST_COMPANY, "account_type": "Tax", "is_group": 0}, "name"
	) or frappe.db.get_value("Account", {"company": TEST_COMPANY, "is_group": 0}, "name")
	doc = frappe.get_doc(
		{
			"doctype": "Sales Taxes and Charges Template",
			"title": "_Test Maintenance Tax",
			"company": TEST_COMPANY,
			"taxes": [
				{
					"charge_type": "On Net Total",
					"account_head": account,
					"description": "VAT",
					"rate": 18,
				}
			],
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


class TestMaintenanceJobCard(IntegrationTestCase):
	"""Issue.validate is the propms doc hook that bills maintenance work."""

	def setUp(self):
		# Job card billing commits through ERPNext, so leases from an earlier
		# test in this module survive into the next one.
		self.property_name = create_property("_Test Job Card Property", max_active_leases=99)
		self.customer = create_customer()
		self.item = create_item("_Test Maintenance Item", is_stock_item=0)
		create_lease(self.property_name, customer=self.customer)
		frappe.db.set_value("Company", TEST_COMPANY, "default_maintenance_tax_template", get_tax_template())
		set_settings(group_maintenance_job_items=0, submit_maintenance_invoice=0)

	def make_issue(self, **kwargs):
		doc = frappe.get_doc(
			{
				"doctype": "Issue",
				"subject": "_Test Job Card",
				"company": TEST_COMPANY,
				"property_name": self.property_name,
				"customer": self.customer,
				**kwargs,
			}
		)
		return doc

	def test_billing_creates_a_draft_sales_invoice(self):
		doc = self.make_issue(
			materials_billed=[
				{
					"item": self.item,
					"quantity": 2,
					"rate": 500,
					"amount": 1000,
					"material_status": "Bill",
				}
			]
		)
		before = frappe.db.count("Sales Invoice")
		validate(doc, "validate")
		self.assertEqual(
			frappe.db.count("Sales Invoice") - before,
			1,
			"no Sales Invoice was created for the billed material",
		)
		self.assertEqual(doc.materials_billed[0].invoiced, 1)

	def test_billing_runs_without_committing(self):
		"""v16 aborts any frappe.db.commit() reached from a document hook."""
		doc = self.make_issue(
			materials_billed=[{"item": self.item, "quantity": 1, "rate": 100, "material_status": "Bill"}]
		)
		validate(doc, "validate")

	def test_grouped_billing_makes_one_invoice(self):
		set_settings(group_maintenance_job_items=1)
		doc = self.make_issue(
			materials_billed=[
				{"item": self.item, "quantity": 1, "rate": 100, "material_status": "Bill"},
				{"item": self.item, "quantity": 2, "rate": 100, "material_status": "Bill"},
			]
		)
		before = frappe.db.count("Sales Invoice")
		validate(doc, "validate")
		self.assertEqual(frappe.db.count("Sales Invoice") - before, 1)

	def test_no_invoice_without_a_customer(self):
		doc = self.make_issue(
			customer=None,
			materials_billed=[{"item": self.item, "quantity": 1, "rate": 100, "material_status": "Bill"}],
		)
		before = frappe.db.count("Sales Invoice")
		validate(doc, "validate")
		self.assertEqual(frappe.db.count("Sales Invoice"), before)

	def test_open_materials_block_closing_the_job_card(self):
		doc = self.make_issue(
			status="Closed",
			materials_required=[{"item": self.item, "quantity": 1, "material_status": "Bill"}],
		)
		with self.assertRaises(frappe.ValidationError):
			validate_materials_required(doc)

	def test_self_consumption_materials_do_not_block_closing(self):
		doc = self.make_issue(
			status="Closed",
			materials_required=[{"item": self.item, "quantity": 1, "material_status": "Self Consumption"}],
		)
		validate_materials_required(doc)

	def test_missing_tax_template_is_reported(self):
		frappe.db.set_value("Company", TEST_COMPANY, "default_maintenance_tax_template", None)
		doc = self.make_issue(
			materials_billed=[{"item": self.item, "quantity": 1, "rate": 100, "material_status": "Bill"}]
		)
		with self.assertRaises(frappe.ValidationError):
			validate(doc, "validate")


class TestIssueHelpers(IntegrationTestCase):
	def test_items_group_reads_the_settings_table(self):
		settings = frappe.get_single("Property Management Settings")
		settings.set("maintenance_item_group", [])
		settings.append("maintenance_item_group", {"item_group": "All Item Groups"})
		settings.save(ignore_permissions=True)
		self.assertEqual(get_items_group(), ["All Item Groups"])

	def test_taxes_template_for_an_item_without_one(self):
		self.assertEqual(get_taxes_template(create_item("_Test Untaxed Item")), "")

	def test_stock_availability_of_an_unstocked_item(self):
		self.assertEqual(get_stock_availability(create_item("_Test No Stock Item"), TEST_COMPANY, 0), 0)

	def test_item_rate_without_a_price_list_entry(self):
		self.assertIsNone(get_item_rate(create_item("_Test Unpriced Item"), create_customer()))
