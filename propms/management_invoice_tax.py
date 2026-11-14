"""Tax policy for Sales Invoices raised against Management Leases.

A Management Lease is a tax-free internal billing component; never infer taxes
from the Company, Customer, Item, or a Sales Taxes and Charges Template.
"""

import frappe
from frappe import _


def is_management_lease(lease_name):
    if not lease_name:
        return False
    if not frappe.db.exists("Lease", lease_name):
        return False
    values = frappe.db.get_value(
        "Lease", lease_name, ["custom_lease_component", "custom_department"], as_dict=True
    )
    return bool(
        values
        and (
            values.get("custom_lease_component") == "Management"
            or values.get("custom_department") == "Management"
        )
    )


def clear_management_invoice_taxes(invoice):
    """Enforce tax-free payload after ERPNext's default-resolution methods.

    Intended for the lease invoice generator before insertion only. For saved
    invoices, use validate_management_invoice_taxes to reject tax rows instead.
    """
    if invoice.doctype != "Sales Invoice" or not is_management_lease(invoice.get("lease")):
        return
    invoice.taxes_and_charges = None
    invoice.set("taxes", [])
    # Item Tax Templates can silently repopulate taxes during ERPNext validation.
    for row in invoice.get("items") or []:
        row.item_tax_template = None
        row.item_tax_rate = None


def validate_management_invoice_taxes(doc, method=None):
    """Reject any tax configuration on a Management lease Sales Invoice.

    Validate AND before_submit are hooked so ordinary form/API entry and later
    edits are covered, without modifying submitted historical records.
    """
    if doc.doctype != "Sales Invoice" or not is_management_lease(doc.get("lease")):
        return
    if doc.get("taxes_and_charges"):
        frappe.throw(
            _("Management Lease invoice {0} cannot have a Sales Taxes and Charges Template").format(
                doc.name or "(new)"
            )
        )
    if doc.get("taxes"):
        frappe.throw(
            _("Management Lease invoice {0} cannot contain Sales Taxes and Charges rows").format(
                doc.name or "(new)"
            )
        )
    for row in doc.get("items") or []:
        if row.get("item_tax_template") or row.get("item_tax_rate"):
            frappe.throw(
                _("Management Lease invoice {0} cannot have item-level taxes").format(
                    doc.name or "(new)"
                )
            )
    if abs(frappe.utils.flt(doc.get("total_taxes_and_charges"))) > 0.005:
        frappe.throw(
            _("Management Lease invoice {0} must have zero taxes").format(
                doc.name or "(new)"
            )
        )
