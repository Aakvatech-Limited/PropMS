import os

import frappe
from frappe.tests import IntegrationTestCase

from propms import hooks


def as_list(value):
	return value if isinstance(value, list) else [value]


class TestHooks(IntegrationTestCase):
	"""hooks.py must point at code and files that exist on version 16."""

	def test_doc_event_targets_resolve(self):
		for doctype, events in hooks.doc_events.items():
			self.assertTrue(frappe.db.exists("DocType", doctype), f"unknown DocType in doc_events: {doctype}")
			for event, handlers in events.items():
				for handler in as_list(handlers):
					self.assertTrue(
						callable(frappe.get_attr(handler)),
						f"{doctype}.{event} -> {handler} is not callable",
					)

	def test_scheduler_event_targets_resolve(self):
		for key, value in hooks.scheduler_events.items():
			handlers = []
			if isinstance(value, dict):
				for cron_handlers in value.values():
					handlers.extend(cron_handlers)
			else:
				handlers.extend(value)
			for handler in handlers:
				self.assertTrue(callable(frappe.get_attr(handler)), f"{key} -> {handler} is not callable")

	def test_scheduler_cron_key_is_lowercase(self):
		self.assertIn("cron", hooks.scheduler_events)
		self.assertNotIn("Cron", hooks.scheduler_events)

	def test_install_and_migrate_hooks_resolve(self):
		for handler in list(hooks.after_install) + list(hooks.after_migrate):
			self.assertTrue(callable(frappe.get_attr(handler)), f"{handler} is not callable")

	def test_before_tests_hook_resolves(self):
		self.assertTrue(callable(frappe.get_attr(hooks.before_tests)))

	def test_doctype_js_files_exist(self):
		for doctype, path in hooks.doctype_js.items():
			self.assertTrue(frappe.db.exists("DocType", doctype), f"unknown DocType in doctype_js: {doctype}")
			self.assertTrue(
				os.path.isfile(frappe.get_app_path("propms", path)), f"missing doctype_js asset: {path}"
			)

	def test_page_js_files_exist(self):
		for page, path in hooks.page_js.items():
			self.assertTrue(
				os.path.isfile(frappe.get_app_path("propms", path)),
				f"missing page_js asset for {page}: {path}",
			)

	def test_page_js_targets_existing_pages(self):
		"""The legacy offline `pos` page was removed from ERPNext before version 16."""
		for page in hooks.page_js:
			self.assertTrue(
				frappe.db.exists("Page", page), f"page_js targets a page that does not exist: {page}"
			)
