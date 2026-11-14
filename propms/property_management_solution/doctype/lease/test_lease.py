# Copyright (c) 2018, Aakvatech and Contributors
# See license.txt

import unittest
from unittest.mock import patch

from frappe import _dict

from propms.lease_status_utils import get_active_lease_statuses, get_overlap_blocking_statuses, is_active_lease_status
from propms.property_management_solution.doctype.lease.lease import (
	is_lease_period_overlapping,
)


def make_lease(start_date, end_date=None, skip_end_date=0):
	return _dict(start_date=start_date, end_date=end_date, skip_end_date=skip_end_date)


class TestLeasePeriodOverlap(unittest.TestCase):
	def test_successor_starting_before_end_overlaps(self):
		"""MV-206-001-02 vs. MV-206-001-03: successor starts inside the running lease."""
		lease = make_lease("2024-12-01", "2026-11-30")
		self.assertTrue(is_lease_period_overlapping(lease, make_lease("2026-11-01")))

	def test_successor_starting_after_end_does_not_overlap(self):
		lease = make_lease("2024-12-01", "2026-11-30")
		self.assertFalse(is_lease_period_overlapping(lease, make_lease("2026-12-01", "2028-11-30")))

	def test_predecessor_ending_before_start_does_not_overlap(self):
		lease = make_lease("2024-12-01", "2026-11-30")
		self.assertFalse(is_lease_period_overlapping(lease, make_lease("2022-12-01", "2024-11-30")))

	def test_shared_boundary_day_overlaps(self):
		lease = make_lease("2024-12-01", "2026-11-30")
		self.assertTrue(is_lease_period_overlapping(lease, make_lease("2026-11-30", "2027-11-30")))

	def test_open_ended_lease_overlaps_later_lease(self):
		lease = make_lease("2024-12-01")
		self.assertTrue(is_lease_period_overlapping(lease, make_lease("2030-01-01", "2031-01-01")))

	def test_skipped_end_date_counts_as_open_ended(self):
		lease = make_lease("2024-12-01", "2025-11-30", skip_end_date=1)
		self.assertTrue(is_lease_period_overlapping(lease, make_lease("2026-01-01", "2026-12-31")))
		other = make_lease("2020-01-01", "2020-12-31", skip_end_date=1)
		self.assertTrue(is_lease_period_overlapping(make_lease("2024-12-01", "2025-11-30"), other))


class TestLeaseStatusClassification(unittest.TestCase):
	@patch("propms.lease_status_utils.frappe.get_all")
	def test_active_statuses_are_read_from_master(self, get_all):
		get_all.return_value = ["Active", "Adendum to Previous Lease", "Vacating"]
		self.assertIn("Adendum to Previous Lease", get_active_lease_statuses())
		get_all.assert_called_once_with("Lease Status", filters={"is_active_lease": 1}, pluck="name")

	@patch("propms.lease_status_utils.frappe.get_all")
	def test_overlap_statuses_are_independent(self, get_all):
		get_all.return_value = ["Upcoming", "Active"]
		self.assertIn("Upcoming", get_overlap_blocking_statuses())
		get_all.assert_called_once_with("Lease Status", filters={"blocks_overlapping_leases": 1}, pluck="name")

	@patch("propms.lease_status_utils.frappe.db.get_value")
	def test_lease_status_flag(self, get_value):
		get_value.return_value = 1
		self.assertTrue(is_active_lease_status("Adendum to Previous Lease"))
		get_value.assert_called_once_with("Lease Status", "Adendum to Previous Lease", "is_active_lease")
		self.assertFalse(is_active_lease_status(None))
