import frappe
from frappe.tests import IntegrationTestCase

from propms.utils.create_custom_fields import execute as create_custom_fields
from propms.utils.create_custom_fields import export_custom_fields
from propms.utils.create_property_setter import execute as create_property_setters

APP_CUSTOM_FIELDS = [
	("Issue", "property_name"),
	("Issue", "materials_billed"),
	("Issue", "materials_required"),
	("Sales Invoice", "lease"),
	("Sales Invoice", "lease_item"),
	("Sales Invoice", "job_card"),
	("Company", "default_maintenance_tax_template"),
	("Company", "security_account_code"),
	("Material Request", "sales_invoice"),
	("Property", "territory"),
]


class TestInstallHooks(IntegrationTestCase):
	"""after_install and after_migrate both run these two builders."""

	def test_every_declared_custom_field_exists(self):
		missing = [
			f"{doctype}.{fieldname}"
			for doctype, fieldname in APP_CUSTOM_FIELDS
			if not frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": fieldname})
		]
		self.assertEqual(missing, [], f"custom fields missing after install: {missing}")

	def test_custom_field_builder_is_idempotent(self):
		before = frappe.db.count("Custom Field")
		create_custom_fields()
		self.assertEqual(before, frappe.db.count("Custom Field"))

	def test_property_setter_builder_is_idempotent(self):
		before = frappe.db.count("Property Setter")
		create_property_setters()
		self.assertEqual(before, frappe.db.count("Property Setter"))

	def test_export_custom_fields_round_trips(self):
		name = frappe.db.get_value("Custom Field", {"dt": "Issue", "fieldname": "property_name"}, "name")
		exported = export_custom_fields(frappe.as_json([name]))
		self.assertIn("property_name", exported)
