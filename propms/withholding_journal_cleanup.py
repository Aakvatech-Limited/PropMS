"""Remove csf_tz withholding-tax journals before deleting a Sales Invoice.

Journal discovery is grounded in Sales Invoice Item.withholding_tax_entry and
the Journal Entry Account.reference_type/reference_name link. Never delete
arbitrary journals merely because they refer to the invoice.
"""

import frappe
from frappe import _


def delete_withholding_journals_for_invoice(invoice):
    """Cancel and delete journals generated for this invoice's withholding tax.

    Must be called inside the caller's invoice-level transaction/savepoint.
    Raises on any dependency, permission, or inconsistent linkage, so no
    partially removed tax journals are committed.
    """
    item_meta = frappe.get_meta("Sales Invoice Item")
    has_entry_field = item_meta.has_field("withholding_tax_entry")
    has_flag_field = item_meta.has_field("csf_tz_wtax_jv_created")

    linked_names = set()
    for item in invoice.items:
        if has_entry_field and item.get("withholding_tax_entry"):
            linked_names.add(item.withholding_tax_entry)

    # Some older invoices may have lost the item-side reference. csf_tz
    # generates a JE line with an explicit Sales Invoice reference, and a
    # distinctive remark. Require BOTH to identify such historical journals.
    je_accounts = frappe.get_all(
        "Journal Entry Account",
        filters={
            "reference_type": "Sales Invoice",
            "reference_name": invoice.name,
            "parenttype": "Journal Entry",
        },
        fields=["parent"],
        distinct=True,
        limit_page_length=0,
    )
    for row in je_accounts:
        journal_header = frappe.db.get_value(
            "Journal Entry", row.parent, ["company", "user_remark"], as_dict=True
        )
        if (
            journal_header
            and journal_header.company == invoice.company
            and (journal_header.user_remark or "").startswith("Withholding Tax Receivable Against Item ")
            and (" Sales Invoice " + invoice.name + " ") in journal_header.user_remark
        ):
            linked_names.add(row.parent)

    if not linked_names:
        return []

    journals = []
    for name in sorted(linked_names):
        journal = frappe.get_doc("Journal Entry", name)
        journal.check_permission("delete")
        if journal.docstatus == 1:
            journal.check_permission("cancel")
        if journal.company != invoice.company:
            frappe.throw(
                _("Withholding journal {0} belongs to a different company.").format(name)
            )

        # A multi-invoice journal must never be removed by a single invoice's
        # cleanup, even if one item happens to carry that journal's name.
        references = {
            row.reference_name
            for row in journal.accounts
            if row.reference_type == "Sales Invoice" and row.reference_name
        }
        if references != {invoice.name}:
            frappe.throw(
                _("Journal {0} is not exclusively linked to Sales Invoice {1}; manual review required.").format(
                    name, invoice.name
                )
            )

        # Item-side references are authoritative for csf_tz-created journals.
        # Fallback candidates must have the same provenance in their remarks.
        directly_linked = any(
            has_entry_field and item.get("withholding_tax_entry") == name
            for item in invoice.items
        )
        if not directly_linked and not (
            (journal.user_remark or "").startswith("Withholding Tax Receivable Against Item ")
            and (" Sales Invoice " + invoice.name + " ") in (journal.user_remark or "")
        ):
            frappe.throw(_("Journal {0} cannot be verified as a withholding-tax journal.").format(name))

        journals.append(journal)

    # Clear the custom item references first, so standard link validation does
    # not prevent the corresponding Journal Entry from being deleted.
    for item in invoice.items:
        if has_entry_field and item.get("withholding_tax_entry") in linked_names:
            values = {"withholding_tax_entry": None}
            if has_flag_field:
                values["csf_tz_wtax_jv_created"] = 0
            frappe.db.set_value("Sales Invoice Item", item.name, values, update_modified=False)

    deleted = []
    for journal in journals:
        if journal.docstatus == 1:
            journal.cancel()
        # Standard Frappe deletion checks remain active, including linked
        # payments and bank reconciliations; no ignore_links/force flags.
        frappe.delete_doc("Journal Entry", journal.name)
        deleted.append(journal.name)

    return deleted
