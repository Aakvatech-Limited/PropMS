import json
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from propms import lease_invoice as billing


class TestLeaseInvoiceRetries(unittest.TestCase):
	def test_matching_draft_is_reused_before_insert(self):
		items = [{"item_code": "Rent", "qty": 1, "rate": 100}]
		existing = SimpleNamespace(name="EXISTING-DRAFT")
		with (
			patch.object(billing, "frappe") as frappe,
			patch.object(billing, "_lock_lease"),
			patch.object(billing, "_existing_invoice", return_value=existing),
			patch.object(billing, "add_months", return_value="2026-12-01"),
			patch.object(billing, "add_days", return_value="2026-11-30"),
		):
			frappe.parse_json.side_effect = json.loads
			result = billing.makeInvoice("2026-11-01", "Tenant", json.dumps(items), "TZS", "LEASE", "Rent", 1, "2026-11-01")
			self.assertIs(result, existing)
			frappe.get_doc.assert_not_called()

	def test_submit_failure_rolls_back_new_draft_and_propagates(self):
		doc = MagicMock()
		doc.doctype = "Sales Invoice"
		doc.taxes_and_charges = None
		doc.submit.side_effect = ValueError("tax configuration")
		with (
			patch.object(billing, "frappe") as frappe,
			patch.object(billing, "_lock_lease"),
			patch.object(billing, "_existing_invoice", return_value=None),
			patch.object(billing, "getDueDate"),
			patch.object(billing, "getCostCenter"),
			patch.object(billing, "add_months", return_value="2026-12-01"),
			patch.object(billing, "add_days", return_value="2026-11-30"),
			patch.object(billing, "today", return_value="2026-11-13"),
		):
			frappe.parse_json.side_effect = json.loads
			frappe.get_doc.return_value = doc
			frappe.db.get_single_value.return_value = 1
			with self.assertRaisesRegex(ValueError, "tax configuration"):
				billing.makeInvoice("2026-11-01", "Tenant", "[]", "TZS", "LEASE", "Rent", 1, "2026-11-01")
			doc.insert.assert_called_once()
			frappe.db.rollback.assert_called_once_with(save_point="lease_invoice_create")

	def test_existing_taxes_are_not_appended_again(self):
		doc = MagicMock()
		doc.get.return_value = [{"account_head": "VAT"}]
		with patch.object(billing, "get_taxes_and_charges") as get_taxes:
			billing.getTax(doc)
			get_taxes.assert_not_called()
			doc.append.assert_not_called()

	def test_failed_tenant_does_not_block_next_tenant(self):
		rows = [
			SimpleNamespace(name=name, parent=lease, paid_by="Tenant", invoice_item_group="1", date_to_invoice="2026-11-01", currency="TZS", document_type="Sales Invoice")
			for name, lease in [("S1", "L1"), ("S2", "L2")]
		]
		with (
			patch.object(billing, "frappe") as frappe,
			patch.object(billing, "_create_schedule_group", side_effect=[ValueError("tax"), SimpleNamespace(name="INV2")]) as create,
		):
			frappe.get_all.return_value = rows
			result = billing.leaseInvoiceAutoCreate()
			self.assertEqual(create.call_count, 2)
			self.assertEqual(result["generated"], ["INV2"])
			self.assertEqual(result["failed"], [{"lease": "L1", "schedules": ["S1"]}])
			frappe.db.rollback.assert_called_once_with(save_point="lease_invoice_group")

	def test_worker_rechecks_links_after_taking_lock(self):
		row = SimpleNamespace(invoice_number="ALREADY-LINKED", sales_order_number=None)
		with patch.object(billing, "frappe") as frappe, patch.object(billing, "_lock_lease") as lock, patch.object(billing, "makeInvoice") as make:
			frappe.get_doc.return_value = row
			self.assertIsNone(billing._create_schedule_group("LEASE", ["S1"]))
			lock.assert_called_once_with("LEASE")
			make.assert_not_called()

	def test_existing_invoice_match_uses_lines_and_ignores_cancelled(self):
		items = [{"item_code": "Rent", "qty": 1, "rate": 100, "service_start_date": "2026-11-01", "service_end_date": "2026-11-30"}]
		existing = SimpleNamespace(items=items)
		with patch.object(billing, "frappe") as frappe:
			frappe.get_all.return_value = ["OLD"]
			frappe.get_doc.return_value = existing
			self.assertIs(billing._existing_invoice("Sales Invoice", "L1", "Tenant", "TZS", "2026-11-01", "2026-11-30", items), existing)
			self.assertEqual(frappe.get_all.call_args.kwargs["filters"]["docstatus"], ["<", 2])
			self.assertIsNone(billing._existing_invoice("Sales Invoice", "L1", "Tenant", "TZS", "2026-11-01", "2026-11-30", [dict(items[0], rate=200)]))

	def test_document_types_form_separate_groups(self):
		rows = [SimpleNamespace(name=kind, parent="L", paid_by="T", invoice_item_group="1", date_to_invoice="2026-11-01", currency="TZS", document_type=kind) for kind in ("Sales Invoice", "Sales Order")]
		with patch.object(billing, "frappe") as frappe, patch.object(billing, "_create_schedule_group", return_value=None) as create:
			frappe.get_all.return_value = rows
			billing.leaseInvoiceAutoCreate()
			self.assertEqual(create.call_count, 2)
