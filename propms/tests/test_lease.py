from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase, UnitTestCase
from frappe.utils import add_days, add_months, nowdate

from propms.property_management_solution.doctype.lease.lease import (
	get_status_for_lease,
	get_system_controlled_statuses,
	initiate_lease_renewal,
	update_lease_statuses,
)
from propms.tests.utils import create_lease, create_property, set_settings


class TestLeaseStatusRules(UnitTestCase):
	"""get_status_for_lease() is pure date arithmetic."""

	def status(self, **lease):
		return get_status_for_lease(frappe._dict(lease), getdate_today())

	def test_future_start_date_is_upcoming(self):
		self.assertEqual(
			self.status(start_date=add_days(nowdate(), 5), end_date=add_months(nowdate(), 6)), "Upcoming"
		)

	def test_current_lease_is_active(self):
		self.assertEqual(
			self.status(start_date=add_days(nowdate(), -5), end_date=add_months(nowdate(), 6)), "Active"
		)

	def test_past_end_date_is_expired(self):
		self.assertEqual(
			self.status(start_date=add_months(nowdate(), -6), end_date=add_days(nowdate(), -1)), "Expired"
		)

	def test_end_date_today_stays_active(self):
		self.assertEqual(self.status(start_date=add_months(nowdate(), -6), end_date=nowdate()), "Active")

	def test_skip_end_date_never_expires(self):
		self.assertEqual(
			self.status(
				start_date=add_months(nowdate(), -6), end_date=add_days(nowdate(), -1), skip_end_date=1
			),
			"Active",
		)

	def test_missing_start_date_returns_none(self):
		self.assertIsNone(self.status(start_date=None, end_date=None))

	def test_system_controlled_statuses(self):
		self.assertEqual(get_system_controlled_statuses(), {"Upcoming", "Active", "Expired"})


def getdate_today():
	from frappe.utils import getdate

	return getdate(nowdate())


class TestLease(IntegrationTestCase):
	def test_lease_insert_sets_status(self):
		lease = create_lease("_Test Lease Property")
		self.assertEqual(lease.lease_status, "Active")

	def test_upcoming_lease_status(self):
		lease = create_lease(
			"_Test Upcoming Property",
			start_date=add_days(nowdate(), 10),
			end_date=add_months(nowdate(), 12),
		)
		self.assertEqual(lease.lease_status, "Upcoming")

	def test_manual_status_is_not_overwritten(self):
		lease = create_lease("_Test Manual Property")
		lease.lease_status = "Terminated"
		lease.save()
		self.assertEqual(lease.lease_status, "Terminated")

	def test_max_active_leases_blocks_second_active_lease(self):
		property_name = create_property("_Test Capped Property", max_active_leases=1)
		create_lease(property_name)
		with self.assertRaises(frappe.ValidationError):
			create_lease(property_name, customer="_Test Tenant")

	def test_property_level_limit_overrides_settings(self):
		set_settings(max_active_leases=1)
		property_name = create_property("_Test Two Lease Property", max_active_leases=2)
		create_lease(property_name)
		second = create_lease(property_name)
		self.assertTrue(second.name)

	def test_update_lease_statuses_expires_finished_lease(self):
		lease = create_lease(
			"_Test Expiring Property",
			start_date=add_months(nowdate(), -12),
			end_date=add_months(nowdate(), 6),
		)
		frappe.db.set_value("Lease", lease.name, "end_date", add_days(nowdate(), -1))
		# The scheduler commits; that would leak this test's rows into the site.
		with patch.object(frappe.db, "commit"):
			update_lease_statuses()
		self.assertEqual(frappe.db.get_value("Lease", lease.name, "lease_status"), "Expired")

	def test_renewal_creates_draft_with_shifted_dates(self):
		lease = create_lease("_Test Renewal Property")
		new_name = initiate_lease_renewal(lease.name)
		new_lease = frappe.get_doc("Lease", new_name)
		self.assertEqual(new_lease.renewed_from, lease.name)
		self.assertEqual(new_lease.lease_status, "Renewal to Previous Lease")
		self.assertEqual(str(new_lease.start_date), add_days(lease.end_date, 1))

	def test_renewal_rejects_duplicate(self):
		lease = create_lease("_Test Single Renewal Property")
		initiate_lease_renewal(lease.name)
		with self.assertRaises(frappe.ValidationError):
			initiate_lease_renewal(lease.name)

	def test_renewal_rejects_ineligible_status(self):
		lease = create_lease("_Test Draft Renewal Property")
		frappe.db.set_value("Lease", lease.name, "lease_status", "Terminated")
		with self.assertRaises(frappe.ValidationError):
			initiate_lease_renewal(lease.name)

	def test_renewal_comment_uses_desk_route(self):
		lease = create_lease("_Test Route Property")
		initiate_lease_renewal(lease.name)
		comment = frappe.get_all(
			"Comment",
			filters={"reference_doctype": "Lease", "reference_name": lease.name},
			pluck="content",
			order_by="creation desc",
			limit=1,
		)[0]
		self.assertNotIn("/app/", comment)
		self.assertIn("/desk/", comment)
