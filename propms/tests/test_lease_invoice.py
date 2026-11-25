# Copyright (c) 2026, Aakvatech and Contributors
# See license.txt

import unittest
from datetime import date

from frappe import _dict

from propms.lease_invoice import get_group_skip_reason, group_schedule_rows


def make_row(name, parent, lease_item="Rent", paid_by="Tenant", day=1, group="1", currency="EUR"):
	return _dict(
		name=name,
		parent=parent,
		lease_item=lease_item,
		paid_by=paid_by,
		invoice_item_group=group,
		date_to_invoice=date(2026, 11, day),
		currency=currency,
	)


class TestGroupScheduleRows(unittest.TestCase):
	def test_rows_of_one_lease_and_date_share_an_invoice(self):
		rows = [make_row("LIS1", "MV-1"), make_row("LIS2", "MV-1", lease_item="Service Charge")]
		self.assertEqual([[r.name for r in g] for g in group_schedule_rows(rows)], [["LIS1", "LIS2"]])

	def test_each_key_field_starts_a_new_invoice(self):
		rows = [
			make_row("LIS1", "MV-1"),
			make_row("LIS2", "MV-1", paid_by="Other Tenant"),
			make_row("LIS3", "MV-1", paid_by="Other Tenant", group="2"),
			make_row("LIS4", "MV-1", paid_by="Other Tenant", group="2", day=15),
			make_row("LIS5", "MV-1", paid_by="Other Tenant", group="2", day=15, currency="USD"),
			make_row("LIS6", "MV-2", paid_by="Other Tenant", group="2", day=15, currency="USD"),
		]
		self.assertEqual(
			[[r.name for r in g] for g in group_schedule_rows(rows)],
			[["LIS1"], ["LIS2"], ["LIS3"], ["LIS4"], ["LIS5"], ["LIS6"]],
		)

	def test_no_rows_give_no_groups(self):
		self.assertEqual(group_schedule_rows([]), [])


class TestGroupSkipReason(unittest.TestCase):
	def test_complete_group_is_billed(self):
		rows = [make_row("LIS1", "MV-1"), make_row("LIS2", "MV-1")]
		self.assertIsNone(get_group_skip_reason(rows, {"MV-1"}))

	def test_row_without_lease_item_skips_the_whole_group(self):
		"""One row without item used to abort the run for every lease."""
		rows = [make_row("LIS1", "MV-1"), make_row("LIS2", "MV-1", lease_item=None)]
		reason = get_group_skip_reason(rows, {"MV-1"})
		self.assertIn("LIS2", reason)
		self.assertNotIn("LIS1", reason)

	def test_rows_of_a_missing_lease_are_skipped(self):
		"""Orphaned schedule rows, for example left behind by a renamed lease."""
		reason = get_group_skip_reason([make_row("LIS1", "E-1")], {"MV-1"})
		self.assertIn("E-1", reason)

	def test_bad_group_does_not_affect_other_groups(self):
		rows = [make_row("LIS1", "E-1", lease_item=None), make_row("LIS2", "MV-1")]
		reasons = [get_group_skip_reason(g, {"MV-1"}) for g in group_schedule_rows(rows)]
		self.assertIsNotNone(reasons[0])
		self.assertIsNone(reasons[1])
