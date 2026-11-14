"""Regression tests for Property Status classification and lease-safe transitions."""

import unittest
from unittest.mock import patch

from frappe import _dict

from propms.property_status_utils import (
	category_counts_as_occupied,
	desired_system_property_status,
	get_effective_property_occupancy,
	is_property_available_for_lease,
)


class TestPropertyStatus(unittest.TestCase):
	@patch("propms.property_status_utils.frappe.db.get_value", return_value=1)
	def test_facility_management_category_counts_as_occupied(self, get_value):
		self.assertTrue(category_counts_as_occupied("Occupied"))
		get_value.assert_called_with("Property Status Category", "Occupied", "counts_as_occupied")

	@patch("propms.property_status_utils.get_active_leases_for_property", return_value=[])
	@patch("propms.property_status_utils.frappe.db.get_value", return_value="Managed for Customer")
	@patch("propms.property_status_utils.is_occupied_property_status", return_value=True)
	def test_facility_management_without_lease_remains_occupied(self, check, get_value, leases):
		self.assertTrue(get_effective_property_occupancy("P-001"))
		leases.assert_not_called()

	@patch("propms.property_status_utils.status_info", return_value={"status_category": "Occupied", "is_system_controlled": 0})
	@patch("propms.property_status_utils.frappe.db.get_value", return_value="Managed for Customer")
	def test_facility_management_not_automatically_changed(self, get_value, info):
		self.assertIsNone(desired_system_property_status("P-001"))

	@patch("propms.property_status_utils.status_info", return_value={"status_category": "Maintenance", "is_system_controlled": 0})
	@patch("propms.property_status_utils.frappe.db.get_value", return_value="In Renovation")
	def test_renovation_status_not_overwritten(self, get_value, info):
		self.assertIsNone(desired_system_property_status("P-001"))

	@patch("propms.property_status_utils.status_info", return_value={"status_category": "Inactive", "is_system_controlled": 0, "is_terminal": 1})
	@patch("propms.property_status_utils.frappe.db.get_value", return_value="Sold")
	def test_sold_property_not_automatically_made_available(self, get_value, info):
		self.assertIsNone(desired_system_property_status("P-001"))

	@patch("propms.property_status_utils.status_info", return_value={"status_category": "Occupied", "is_system_controlled": 1})
	@patch("propms.property_status_utils.frappe.db.get_value", return_value="On Lease")
	@patch("propms.property_status_utils.get_active_leases_for_property", return_value=[])
	def test_expired_lease_becomes_available(self, leases, get_value, info):
		self.assertEqual(desired_system_property_status("P-001"), "Available")

	@patch("propms.property_status_utils.status_info", return_value={"status_category": "Occupied", "is_system_controlled": 1})
	@patch("propms.property_status_utils.frappe.db.get_value", return_value="On Lease")
	@patch("propms.property_status_utils.get_active_leases_for_property", return_value=[_dict(end_date=None, skip_end_date=1)])
	def test_open_ended_lease_remains_on_lease(self, leases, get_value, info):
		self.assertIsNone(desired_system_property_status("P-001"))

	@patch("propms.property_status_utils.status_info", return_value={"status_category": "Occupied", "is_system_controlled": 1})
	@patch("propms.property_status_utils.frappe.db.get_value", return_value="On Lease")
	@patch("propms.property_status_utils.get_active_leases_for_property", return_value=[_dict(end_date="2026-11-30", skip_end_date=0), _dict(end_date=None, skip_end_date=1)])
	def test_multiple_leases_prevent_vacancy_or_expiry_warning(self, leases, get_value, info):
		self.assertIsNone(desired_system_property_status("P-001", "2026-11-14"))

	@patch("propms.property_status_utils.status_info", return_value={"status_category": "Available", "is_system_controlled": 1, "blocks_new_leases": 0, "is_terminal": 0})
	@patch("propms.property_status_utils.frappe.db.get_value", return_value=_dict(status="Available", is_group=0))
	@patch("propms.property_status_utils.get_active_leases_for_property", return_value=[_dict(name="LEASE-1")])
	def test_active_lease_blocks_available_reporting(self, leases, get_value, info):
		self.assertFalse(is_property_available_for_lease("P-001"))

	@patch("propms.property_status_utils.status_info", return_value={"status_category": "Reserved", "is_system_controlled": 0})
	@patch("propms.property_status_utils.frappe.db.get_value", return_value="Booked")
	def test_booked_property_not_overwritten(self, get_value, info):
		self.assertIsNone(desired_system_property_status("P-001"))
