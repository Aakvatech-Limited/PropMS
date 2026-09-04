import json
import os

import frappe
from frappe.tests import IntegrationTestCase

LINK_FIELDTYPES = {"Link", "Table", "Table MultiSelect", "Tree Select"}


def app_doctype_files() -> list:
	root = frappe.get_app_path("propms", "property_management_solution", "doctype")
	paths = []
	for folder in sorted(os.listdir(root)):
		path = os.path.join(root, folder, f"{folder}.json")
		if os.path.isfile(path):
			paths.append(path)
	return paths


def load_doctypes() -> list:
	doctypes = []
	for path in app_doctype_files():
		with open(path) as handle:
			doctypes.append(json.load(handle))
	return doctypes


class TestDocTypeSchema(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.doctypes = load_doctypes()

	def test_every_doctype_is_installed(self):
		missing = [d["name"] for d in self.doctypes if not frappe.db.exists("DocType", d["name"])]
		self.assertEqual(missing, [], f"DocTypes not installed on the site: {missing}")

	def test_link_targets_exist(self):
		"""A Link or Table field pointing at a missing DocType aborts the whole test run."""
		broken = []
		for doctype in self.doctypes:
			for field in doctype.get("fields", []):
				options = (field.get("options") or "").strip()
				if field.get("fieldtype") in LINK_FIELDTYPES and options:
					if not frappe.db.exists("DocType", options):
						broken.append(f"{doctype['name']}.{field.get('fieldname')} -> {options}")
		self.assertEqual(broken, [], f"link fields target missing DocTypes: {broken}")

	def test_no_myisam_tables(self):
		"""MyISAM has no transactions, so its rows survive every test rollback."""
		myisam = [d["name"] for d in self.doctypes if d.get("engine") == "MyISAM"]
		self.assertEqual(myisam, [], f"DocTypes still on MyISAM: {myisam}")

	def test_naming_series_fields_have_options(self):
		broken = []
		for doctype in self.doctypes:
			if not str(doctype.get("autoname") or "").startswith("naming_series:"):
				continue
			field = next(
				(f for f in doctype.get("fields", []) if f.get("fieldname") == "naming_series"), None
			)
			if not field or not (field.get("options") or "").strip():
				broken.append(doctype["name"])
		self.assertEqual(broken, [], f"autoname=naming_series: without a series option: {broken}")

	def test_every_doctype_can_be_described(self):
		"""frappe.get_meta() resolves fetch_from, links and permissions."""
		for doctype in self.doctypes:
			meta = frappe.get_meta(doctype["name"])
			self.assertEqual(meta.name, doctype["name"])
