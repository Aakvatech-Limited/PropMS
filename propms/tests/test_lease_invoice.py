import json
from unittest import TestCase
from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_months, get_first_day, nowdate

from propms.lease_invoice import (
	getCostCenter,
	getDueDate,
	getTax,
	leaseInvoiceAutoCreate,
	makeInvoice,
)
from propms.property_management_solution.doctype.lease.lease import (
	make_lease_invoice_schedule as build_schedule_for_lease,
)
from propms.tests.utils import create_customer, create_item, create_lease, set_settings


class TestLeaseInvoiceTaxes(TestCase):
	def test_template_reload_does_not_duplicate_taxes(self):
		invoice = frappe.get_doc({"doctype": "Sales Invoice", "taxes_and_charges": "Standard"})
		tax = {"charge_type": "On Net Total", "account_head": "Output VAT", "rate": 18}
		invoice.append("taxes", tax.copy())
		with patch("propms.lease_invoice.get_taxes_and_charges", return_value=[tax]):
			getTax(invoice)
			getTax(invoice)
		self.assertEqual(len(invoice.taxes), 1)
		self.assertEqual(invoice.taxes[0].rate, 18)

	def test_template_reload_replaces_stale_taxes_and_preserves_template_rows(self):
		invoice = frappe.get_doc({"doctype": "Sales Invoice", "taxes_and_charges": "Replacement"})
		invoice.append("taxes", {"account_head": "Old VAT", "rate": 0})
		taxes = [
			{"charge_type": "On Net Total", "account_head": "Output VAT", "rate": 18},
			{"charge_type": "On Net Total", "account_head": "Levy", "rate": 1},
		]
		with patch("propms.lease_invoice.get_taxes_and_charges", return_value=taxes):
			getTax(invoice)
		self.assertEqual([row.account_head for row in invoice.taxes], ["Output VAT", "Levy"])
		self.assertEqual([row.idx for row in invoice.taxes], [1, 2])


class TestLeaseInvoice(IntegrationTestCase):
	def setUp(self):
		set_settings(
			invoice_start_date=add_months(nowdate(), -1),
			auto_submit_sales_invoice=0,
			auto_submit_sales_order=0,
		)

	def test_get_cost_center_from_lease(self):
		lease = create_lease("_Test Cost Centre Property")
		self.assertEqual(
			getCostCenter(lease.name),
			frappe.db.get_value("Property", lease.property, "cost_center"),
		)

	def test_get_due_date(self):
		self.assertTrue(getDueDate(nowdate(), create_customer()))

	def test_make_invoice_creates_draft_sales_invoice(self):
		lease = create_lease("_Test Invoice Property")
		items = json.dumps([{"item_code": create_item(), "qty": 1, "rate": 1000}])
		invoice = makeInvoice(
			nowdate(),
			lease.customer,
			items,
			frappe.db.get_value("Lease", lease.name, "security_deposit_currency"),
			lease.name,
			create_item(),
			1.0,
			get_first_day(nowdate()),
		)
		self.assertIsNotNone(invoice, "makeInvoice swallowed an exception and returned None")
		self.assertEqual(invoice.doctype, "Sales Invoice")
		self.assertEqual(invoice.docstatus, 0)

	def test_make_invoice_without_customer_is_reported(self):
		lease = create_lease("_Test No Customer Property")
		items = json.dumps([{"item_code": create_item(), "qty": 1, "rate": 1000}])
		with self.assertRaises(frappe.ValidationError):
			makeInvoice(nowdate(), None, items, "TZS", lease.name, create_item(), 1.0, nowdate())

	def test_auto_create_handles_empty_schedule(self):
		"""An empty schedule must not raise; the last-group flush has nothing to flush."""
		frappe.db.delete("Lease Invoice Schedule")
		leaseInvoiceAutoCreate()

	def test_auto_create_stamps_invoice_number_on_schedule(self):
		frappe.db.delete("Lease Invoice Schedule")
		lease = create_lease("_Test Auto Invoice Property", end_date=add_months(nowdate(), 3))
		build_schedule_for_lease(lease.name)
		frappe.db.set_value(
			"Lease Invoice Schedule",
			{"parent": lease.name},
			"date_to_invoice",
			nowdate(),
			update_modified=False,
		)
		leaseInvoiceAutoCreate()
		stamped = frappe.get_all(
			"Lease Invoice Schedule",
			filters={"parent": lease.name, "invoice_number": ("is", "set")},
			pluck="invoice_number",
		)
		self.assertTrue(stamped, "no Sales Invoice was linked back to the schedule")
