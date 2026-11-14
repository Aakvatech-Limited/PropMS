"""Tests for the pre-migration conflict guard.

Only setters directly targeting Lease.lease_status or Property.status block
migration. Other site customizations must be left untouched.
"""

import unittest
from unittest.mock import call, patch

import frappe

from propms.patches.v16_0.validate_status_property_setters import execute


class TestStatusPropertySetterGuard(unittest.TestCase):
	@patch("propms.patches.v16_0.validate_status_property_setters.frappe.get_all")
	def test_no_setters_allows_migration(self, get_all):
		get_all.return_value = []
		self.assertIsNone(execute())
		self.assertEqual(get_all.call_count, 2)

	@patch("propms.patches.v16_0.validate_status_property_setters.frappe.throw")
	@patch("propms.patches.v16_0.validate_status_property_setters.frappe.get_all")
	def test_property_status_setter_blocks_migration(self, get_all, throw):
		get_all.side_effect = [[], [{"name": "Property-status-options", "property": "options", "value": "Available"}]]
		execute()
		self.assertEqual(throw.call_count, 1)
		self.assertIn("Property.status", throw.call_args.args[0])
		self.assertIn("Property-status-options", throw.call_args.args[0])

	@patch("propms.patches.v16_0.validate_status_property_setters.frappe.throw")
	@patch("propms.patches.v16_0.validate_status_property_setters.frappe.get_all")
	def test_lease_status_setter_blocks_migration(self, get_all, throw):
		get_all.side_effect = [[{"name": "Lease-lease_status-options", "property": "options", "value": "Active"}], []]
		execute()
		self.assertEqual(throw.call_count, 1)
		self.assertIn("Lease.lease_status", throw.call_args.args[0])

	@patch("propms.patches.v16_0.validate_status_property_setters.frappe.throw")
	@patch("propms.patches.v16_0.validate_status_property_setters.frappe.get_all")
	def test_other_field_setters_are_not_removed_or_blocked(self, get_all, throw):
		get_all.return_value = []
		execute()
		throw.assert_not_called()
		for invocation in get_all.call_args_list:
			self.assertIn(invocation.kwargs["filters"]["field_name"], ("status", "lease_status"))
