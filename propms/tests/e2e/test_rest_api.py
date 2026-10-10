"""End-to-end checks over HTTP against a running propms site.

Skipped unless PROPMS_E2E_BASE_URL is set, for example::

    PROPMS_E2E_BASE_URL=http://propms-test.localhost:8003 \
    PROPMS_E2E_PASSWORD=admin \
    env/bin/python -m unittest discover -s propms/tests/e2e -t .
"""

import json
import os
import unittest

import requests

BASE_URL = os.environ.get("PROPMS_E2E_BASE_URL")
USER = os.environ.get("PROPMS_E2E_USER", "Administrator")
PASSWORD = os.environ.get("PROPMS_E2E_PASSWORD", "admin")


@unittest.skipUnless(BASE_URL, "PROPMS_E2E_BASE_URL is not set")
class TestPropmsRestApi(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.session = requests.Session()
		response = cls.session.post(
			f"{BASE_URL}/api/method/login", data={"usr": USER, "pwd": PASSWORD}, timeout=30
		)
		response.raise_for_status()

	def call(self, method: str, **params):
		response = self.session.get(f"{BASE_URL}/api/method/{method}", params=params, timeout=60)
		self.assertEqual(response.status_code, 200, response.text[:400])
		return response.json().get("message")

	def resource(self, doctype: str, **params):
		response = self.session.get(f"{BASE_URL}/api/resource/{doctype}", params=params, timeout=60)
		self.assertEqual(response.status_code, 200, response.text[:400])
		return response.json()["data"]

	def test_lease_resource_lists(self):
		self.assertIsInstance(self.resource("Lease", limit_page_length=5), list)

	def test_property_resource_lists(self):
		self.assertIsInstance(self.resource("Property", limit_page_length=5), list)

	def test_property_management_settings_is_readable(self):
		response = self.session.get(
			f"{BASE_URL}/api/resource/Property Management Settings/Property Management Settings", timeout=30
		)
		self.assertEqual(response.status_code, 200, response.text[:400])

	def test_maintenance_item_groups_endpoint(self):
		self.assertIsInstance(self.call("propms.issue_hook.get_items_group"), list)

	def test_stock_availability_endpoint(self):
		value = self.call(
			"propms.issue_hook.get_stock_availability",
			item_code="_Test Maintenance Item",
			company="_Test Property Company",
			is_pos=0,
		)
		self.assertIsNotNone(value)

	def test_date_helper_endpoints(self):
		self.assertEqual(
			self.call("propms.auto_custom.getMonthADD", date="2026-01-31", month=1), "2026-02-28"
		)
		self.assertEqual(
			self.call("propms.auto_custom.getDateDiff", date1="2026-01-10", date2="2026-01-01"), 9
		)
		self.assertEqual(self.call("propms.auto_custom.getNumberOfDays", date="2026-02-05"), 28)

	def test_latest_active_lease_endpoint(self):
		self.assertIsNotNone(
			self.call("propms.auto_custom.get_latest_active_lease", property_id="_Test POS Property")
		)

	def test_property_tree_children_endpoint(self):
		rows = self.call(
			"propms.property_management_solution.doctype.property.property.get_children",
			doctype="Property",
			parent="",
			company="_Test Property Company",
			is_root=1,
		)
		self.assertIsInstance(rows, list)

	def test_query_report_runs_over_http(self):
		response = self.session.get(
			f"{BASE_URL}/api/method/frappe.desk.query_report.run",
			params={
				"report_name": "Property Status",
				"filters": json.dumps({"property_type": "%", "owner_type": "%"}),
				"ignore_prepared_report": "1",
			},
			timeout=120,
		)
		self.assertEqual(response.status_code, 200, response.text[:400])
		self.assertIn("columns", response.json()["message"])

	def test_desk_workspace_is_served(self):
		response = self.session.get(f"{BASE_URL}/desk/property-management-solution", timeout=60)
		self.assertEqual(response.status_code, 200)

	def test_logout_requires_post(self):
		"""v16 made logout POST-only."""
		response = self.session.get(f"{BASE_URL}/api/method/logout", timeout=30)
		self.assertIn(response.status_code, (403, 404, 405), response.text[:200])
