import frappe
from frappe.tests import IntegrationTestCase, UnitTestCase
from frappe.utils import add_months, get_first_day, nowdate

from propms.auto_custom import getDateMonthDiff, makeInvoiceSchedule
from propms.lease_invoice_schedule import get_aligned_invoice_date, make_lease_invoice_schedule
from propms.property_management_solution.doctype.lease.lease import (
	make_lease_invoice_schedule as build_schedule_for_lease,
)
from propms.tests.utils import create_customer, create_item, create_lease, set_settings


class TestScheduleMath(UnitTestCase):
	def test_whole_month_span(self):
		self.assertEqual(getDateMonthDiff("2026-01-01", "2026-03-31", 1), 3)

	def test_partial_month_span_is_fractional(self):
		value = getDateMonthDiff("2026-01-01", "2026-02-14", 1)
		self.assertGreater(value, 1)
		self.assertLess(value, 2)

	def test_single_day_span(self):
		self.assertGreater(getDateMonthDiff("2026-01-01", "2026-01-01", 1), 0)

	def test_aligned_invoice_date_is_month_start(self):
		self.assertEqual(str(get_aligned_invoice_date("2026-05-17")), "2026-05-01")


class TestLeaseInvoiceSchedule(IntegrationTestCase):
	def setUp(self):
		set_settings(invoice_start_date=add_months(nowdate(), -1))

	def test_build_schedule_creates_rows(self):
		lease = create_lease("_Test Schedule Property", end_date=add_months(nowdate(), 6))
		build_schedule_for_lease(lease.name)
		rows = frappe.get_all("Lease Invoice Schedule", filters={"parent": lease.name}, pluck="name")
		self.assertGreater(len(rows), 0)

	def test_schedule_rows_link_back_to_the_lease(self):
		lease = create_lease("_Test Schedule Parent Property", end_date=add_months(nowdate(), 3))
		build_schedule_for_lease(lease.name)
		rows = frappe.get_all(
			"Lease Invoice Schedule",
			filters={"parent": lease.name},
			fields=["parenttype", "parentfield"],
		)
		self.assertTrue(rows)
		for row in rows:
			self.assertEqual(row.parenttype, "Lease")
			self.assertEqual(row.parentfield, "lease_invoice_schedule")

	def test_schedule_rows_appear_on_the_lease_document(self):
		lease = create_lease("_Test Schedule Child Property", end_date=add_months(nowdate(), 3))
		build_schedule_for_lease(lease.name)
		lease.reload()
		self.assertGreater(len(lease.lease_invoice_schedule), 0)

	def test_make_invoice_schedule_honours_advance_days(self):
		lease = create_lease("_Test Advance Property", days_to_invoice_in_advance=5)
		makeInvoiceSchedule(
			get_first_day(nowdate()),
			create_item(),
			create_customer(),
			create_item(),
			lease.name,
			1.0,
			1000,
			1,
			"TZS",
			0,
			5,
			None,
			"Sales Invoice",
		)
		row = frappe.get_all(
			"Lease Invoice Schedule",
			filters={"parent": lease.name},
			fields=["date_to_invoice", "schedule_start_date"],
			limit=1,
		)[0]
		self.assertEqual(
			frappe.utils.date_diff(row.schedule_start_date, row.date_to_invoice),
			5,
		)

	def test_monthly_scheduler_is_a_no_op_when_disabled(self):
		set_settings(make_invoice_schedule_up_to_tomorrow_only=0)
		before = frappe.db.count("Lease Invoice Schedule")
		make_lease_invoice_schedule()
		self.assertEqual(before, frappe.db.count("Lease Invoice Schedule"))

	def test_monthly_scheduler_creates_rows_for_active_leases(self):
		set_settings(
			make_invoice_schedule_up_to_tomorrow_only=1,
			invoice_start_date=get_first_day(nowdate()),
		)
		lease = create_lease("_Test Monthly Scheduler Property", end_date=add_months(nowdate(), 6))
		make_lease_invoice_schedule()
		rows = frappe.get_all("Lease Invoice Schedule", filters={"parent": lease.name}, pluck="name")
		self.assertGreater(len(rows), 0)
