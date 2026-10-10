import inspect
import re

import frappe
from frappe.tests import IntegrationTestCase, UnitTestCase

from propms import hooks
from propms.tests.utils import create_lease, create_property

COMMIT_PATTERN = re.compile(r"^\s*frappe\.db\.commit\(", re.MULTILINE)
LEGACY_DESK_ROUTE = re.compile(r"[\"'`]/app/")


def hook_handler_modules() -> set:
	modules = set()
	for events in hooks.doc_events.values():
		for handlers in events.values():
			for handler in handlers if isinstance(handlers, list) else [handlers]:
				modules.add(handler.rsplit(".", 1)[0])
	return modules


class TestVersion16Compatibility(UnitTestCase):
	"""Source-level guards for the version-16 breaking changes."""

	def test_no_commit_inside_document_hooks(self):
		"""v16 raises `Cannot commit database transaction from document hooks`."""
		offenders = []
		for module_name in hook_handler_modules():
			source = inspect.getsource(frappe.get_module(module_name))
			if COMMIT_PATTERN.search(source):
				offenders.append(module_name)
		self.assertEqual(offenders, [], f"frappe.db.commit() reached from a doc_event handler: {offenders}")

	def test_no_legacy_app_routes_in_python(self):
		"""/app was rerouted to /desk in version 16."""
		offenders = []
		for module_name in ("propms.property_management_solution.doctype.lease.lease",):
			source = inspect.getsource(frappe.get_module(module_name))
			for match in LEGACY_DESK_ROUTE.finditer(source):
				line = source.count("\n", 0, match.start()) + 1
				offenders.append(f"{module_name}:{line}")
		self.assertEqual(offenders, [], f"hard-coded /app desk route: {offenders}")

	def test_no_deprecated_test_flags(self):
		source = inspect.getsource(frappe.get_module("propms.tests"))
		for deprecated in ("skip_test_records", "flags.in_test", "test_dependencies", "test_ignore"):
			self.assertNotIn(deprecated, source, f"deprecated v15 test API still referenced: {deprecated}")

	def test_app_version_targets_v16(self):
		from propms import __version__

		self.assertTrue(
			__version__.startswith("16."),
			f"propms __version__ is {__version__}; the version-16 branch must report 16.x",
		)


class TestVersion16Runtime(IntegrationTestCase):
	"""Runtime behaviour that version 16 changed."""

	def test_get_all_string_expression_filters_still_work(self):
		"""Property treeview relies on an ifnull() expression filter."""
		from propms.property_management_solution.doctype.property.property import get_children

		create_property("_Test Root Property")
		children = get_children("Property", parent="", is_root=True)
		self.assertIsInstance(children, list)

	def test_get_all_default_order_is_creation(self):
		"""v16 changed the implicit order_by from `modified desc` to `creation desc`."""
		create_property("_Test Order Property A")
		create_property("_Test Order Property B")
		rows = frappe.get_all("Property", pluck="name", limit=2)
		ordered = frappe.get_all("Property", pluck="name", order_by="creation desc", limit=2)
		self.assertEqual(rows, ordered)

	def test_custom_error_log_uses_innodb(self):
		"""MyISAM tables cannot roll back, so they leak rows out of every test."""
		meta = frappe.get_meta("Custom Error Log")
		self.assertEqual((meta.engine or "InnoDB"), "InnoDB")

	def test_lease_document_saves_without_manual_commit(self):
		lease = create_lease("_Test Commit Property")
		lease.reload()
		self.assertTrue(lease.name)
