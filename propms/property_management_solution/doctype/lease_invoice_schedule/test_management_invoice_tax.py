import unittest
from unittest.mock import patch

import frappe
from frappe import _dict

from propms.management_invoice_tax import (
    clear_management_invoice_taxes,
    is_management_lease,
    validate_management_invoice_taxes,
)


class TestManagementInvoiceTax(unittest.TestCase):
    @patch("frappe.db.exists", return_value=True)
    @patch("frappe.db.get_value")
    def test_management_detected_by_component_or_department(self, get_value, exists):
        for value in (
            {"custom_lease_component": "Management", "custom_department": ""},
            {"custom_lease_component": "", "custom_department": "Management"},
        ):
            get_value.return_value = _dict(value)
            self.assertTrue(is_management_lease("LEASE-1"))
        get_value.return_value = _dict(
            custom_lease_component="Financial", custom_department="Financial"
        )
        self.assertFalse(is_management_lease("LEASE-1"))

    @patch("propms.management_invoice_tax.is_management_lease", return_value=True)
    def test_generator_removes_header_and_item_taxes(self, is_management):
        doc = frappe.get_doc({
            "doctype": "Sales Invoice",
            "lease": "LEASE-1",
            "taxes_and_charges": "Standard VAT",
            "taxes": [{"charge_type": "On Net Total", "account_head": "VAT"}],
            "items": [{"item_code": "RENT", "qty": 1, "rate": 100,
                       "item_tax_template": "VAT", "item_tax_rate": '{"VAT": 18}'}],
        })
        clear_management_invoice_taxes(doc)
        self.assertFalse(doc.taxes_and_charges)
        self.assertEqual(doc.get("taxes"), [])
        self.assertFalse(doc.items[0].item_tax_template)
        self.assertFalse(doc.items[0].item_tax_rate)

    @patch("propms.management_invoice_tax.is_management_lease", return_value=True)
    def test_validator_rejects_any_tax_row_even_zero(self, is_management):
        doc = _dict(doctype="Sales Invoice", name="TEST", lease="LEASE-1",
                    taxes_and_charges=None, taxes=[_dict(tax_amount=0)],
                    items=[], total_taxes_and_charges=0)
        with self.assertRaises(frappe.ValidationError):
            validate_management_invoice_taxes(doc)

    @patch("propms.management_invoice_tax.is_management_lease", return_value=True)
    def test_validator_accepts_zero_tax_management(self, is_management):
        doc = _dict(doctype="Sales Invoice", name="TEST", lease="LEASE-1",
                    taxes_and_charges=None, taxes=[], items=[_dict()],
                    total_taxes_and_charges=0)
        validate_management_invoice_taxes(doc)

    @patch("propms.management_invoice_tax.is_management_lease", return_value=False)
    def test_financial_invoice_is_unchanged(self, is_management):
        doc = _dict(doctype="Sales Invoice", name="TEST", lease="LEASE-1",
                    taxes_and_charges="Standard VAT", taxes=[_dict(tax_amount=18)],
                    items=[], total_taxes_and_charges=18)
        validate_management_invoice_taxes(doc)
