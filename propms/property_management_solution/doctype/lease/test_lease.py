# Copyright (c) 2018, Aakvatech and Contributors
# See license.txt

import unittest

from frappe import _dict

from propms.property_management_solution.doctype.lease.lease import (
	LIVE_LEASE_STATUSES,
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

	def test_only_live_statuses_count(self):
		for status in ("Draft", "Not Materialized", "Terminated", "Expired", "Closed"):
			self.assertNotIn(status, LIVE_LEASE_STATUSES)
