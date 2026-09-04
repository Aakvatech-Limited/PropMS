import re

import frappe
from frappe.tests import IntegrationTestCase

from propms.property_management_solution.doctype.property.property import add_node, get_children
from propms.tests import TEST_COMPANY
from propms.tests.utils import create_lease, create_property, get_cost_center


class TestProperty(IntegrationTestCase):
	def test_property_insert(self):
		name = create_property("_Test Basic Property")
		self.assertEqual(frappe.db.get_value("Property", name, "status"), "Available")

	def test_nested_set_parent_child(self):
		parent = create_property("_Test Parent Property", is_group=1)
		child = create_property("_Test Child Property", parent_property=parent)
		lft, rgt = frappe.db.get_value("Property", parent, ["lft", "rgt"])
		child_lft = frappe.db.get_value("Property", child, "lft")
		self.assertTrue(lft < child_lft < rgt)

	def test_get_children_root(self):
		create_property("_Test Tree Root")
		rows = get_children("Property", parent="", company=TEST_COMPANY, is_root=True)
		self.assertTrue(any(row["value"] == "_Test Tree Root" for row in rows))

	def test_get_children_of_parent(self):
		parent = create_property("_Test Tree Parent", is_group=1)
		create_property("_Test Tree Child", parent_property=parent)
		rows = get_children("Property", parent=parent, company=TEST_COMPANY)
		self.assertTrue(any(row["value"] == "_Test Tree Child" for row in rows))

	def test_add_node_uses_the_field_the_tree_view_sends(self):
		"""The tree dialog field name must match the DocType's autoname field."""
		tree_js = frappe.get_app_path(
			"propms", "property_management_solution/doctype/property/property_tree.js"
		)
		with open(tree_js) as handle:
			source = handle.read()
		name_field = re.search(r'fieldname:\s*"([^"]+)",\s*label:\s*__\("New Property Name"\)', source)
		self.assertIsNotNone(name_field, "the tree view no longer defines a new-property name field")

		frappe.form_dict.update(
			{
				"doctype": "Property",
				name_field.group(1): "_Test Node Property",
				"is_root": "true",
				"company": TEST_COMPANY,
				"cost_center": get_cost_center(),
			}
		)
		try:
			add_node()
		finally:
			frappe.form_dict.clear()
		self.assertTrue(frappe.db.exists("Property", "_Test Node Property"))

	def test_status_change_blocked_while_lease_is_active(self):
		name = create_property("_Test Locked Property")
		create_lease(name)
		doc = frappe.get_doc("Property", name)
		doc.status = "Available"
		with self.assertRaises(frappe.ValidationError):
			doc.save()

	def test_get_active_leases_returns_current_lease(self):
		name = create_property("_Test Active Lease Property")
		lease = create_lease(name)
		doc = frappe.get_doc("Property", name)
		self.assertIn(lease.name, [row.name for row in doc.get_active_leases()])
