import frappe
from frappe.tests import IntegrationTestCase

from propms.tests.test_doctype_schema import load_doctypes


class TestDocTypeControllers(IntegrationTestCase):
	"""Every shipped controller class must import and construct on version 16."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.doctypes = load_doctypes()

	def test_controller_modules_import(self):
		broken = []
		for doctype in self.doctypes:
			try:
				frappe.get_module(
					f"propms.property_management_solution.doctype."
					f"{frappe.scrub(doctype['name'])}.{frappe.scrub(doctype['name'])}"
				)
			except Exception as exc:  # noqa: BLE001
				broken.append(f"{doctype['name']}: {type(exc).__name__}: {exc}")
		self.assertEqual(broken, [], f"controller modules failed to import: {broken}")

	def test_controller_classes_resolve(self):
		from frappe.model.base_document import get_controller

		broken = []
		for doctype in self.doctypes:
			try:
				self.assertTrue(callable(get_controller(doctype["name"])))
			except Exception as exc:  # noqa: BLE001
				broken.append(f"{doctype['name']}: {type(exc).__name__}: {exc}")
		self.assertEqual(broken, [], f"controllers failed to resolve: {broken}")

	def test_new_documents_can_be_constructed(self):
		broken = []
		for doctype in self.doctypes:
			if doctype.get("issingle"):
				continue
			try:
				doc = frappe.new_doc(doctype["name"])
				self.assertEqual(doc.doctype, doctype["name"])
			except Exception as exc:  # noqa: BLE001
				broken.append(f"{doctype['name']}: {type(exc).__name__}: {exc}")
		self.assertEqual(broken, [], f"new_doc failed: {broken}")

	def test_singles_load(self):
		for doctype in self.doctypes:
			if not doctype.get("issingle"):
				continue
			self.assertEqual(frappe.get_single(doctype["name"]).doctype, doctype["name"])

	def test_list_views_load_for_every_doctype(self):
		"""v16 moved get_list onto the query builder; every DocType must still list."""
		broken = []
		for doctype in self.doctypes:
			if doctype.get("issingle") or doctype.get("istable"):
				continue
			try:
				frappe.get_list(doctype["name"], limit=1, ignore_permissions=True)
			except Exception as exc:  # noqa: BLE001
				broken.append(f"{doctype['name']}: {type(exc).__name__}: {exc}")
		self.assertEqual(broken, [], f"list view queries failed: {broken}")
