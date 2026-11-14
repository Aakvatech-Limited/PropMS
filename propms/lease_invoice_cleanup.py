"""Controlled deletion of Sales Invoices linked to selected Lease Invoice Schedule rows."""

import frappe
from frappe import _


@frappe.whitelist()
def delete_selected_schedule_invoices(lease_name, schedule_rows):
    """Unlink, cancel if necessary, then delete invoices referenced by selected rows.

    Only rows of the specified Lease can be selected. An invoice referenced by any
    unselected schedule row is refused rather than silently altering that row.
    Each distinct invoice is processed in its own database savepoint.
    """
    if isinstance(schedule_rows, str):
        schedule_rows = frappe.parse_json(schedule_rows)

    if not isinstance(schedule_rows, list) or not schedule_rows or len(schedule_rows) > 200:
        frappe.throw(_("Select between 1 and 200 Lease Invoice Schedule rows."))

    if any(not isinstance(name, str) or not name for name in schedule_rows):
        frappe.throw(_("Invalid schedule row selection."))

    selected = set(schedule_rows)
    if len(selected) != len(schedule_rows):
        frappe.throw(_("Duplicate schedule rows were selected."))

    lease = frappe.get_doc("Lease", lease_name)
    lease.check_permission("write")
    if lease.docstatus == 2:
        frappe.throw(_("Cannot modify the schedule of a cancelled Lease."))

    actual_rows = {row.name: row for row in lease.lease_invoice_schedule}
    if not selected.issubset(actual_rows):
        frappe.throw(_("Some selected schedule rows do not belong to this Lease. Reload and retry."))

    invoice_to_rows = {}
    skipped = []
    for name in schedule_rows:
        invoice_name = actual_rows[name].invoice_number
        if invoice_name:
            invoice_to_rows.setdefault(invoice_name, []).append(name)
        else:
            skipped.append({"row": name, "reason": _("No Sales Invoice linked")})

    results = []
    for invoice_name, row_names in invoice_to_rows.items():
        # Use one savepoint per invoice; failure of an invoice does not leave
        # an unlinked lease schedule or undo previously successful deletions.
        frappe.db.savepoint("lease_invoice_cleanup")
        try:
            linked_rows = frappe.get_all(
                "Lease Invoice Schedule",
                filters={"invoice_number": invoice_name},
                fields=["name", "parent", "parenttype", "parentfield"],
                limit_page_length=0,
            )
            if not linked_rows or any(
                row.name not in selected
                or row.parent != lease_name
                or row.parenttype != "Lease"
                or row.parentfield != "lease_invoice_schedule"
                for row in linked_rows
            ):
                frappe.throw(
                    _("Invoice {0} is linked to an unselected or different Lease schedule row. Select all of its rows on this Lease first.").format(invoice_name)
                )

            invoice = frappe.get_doc("Sales Invoice", invoice_name)
            invoice.check_permission("delete")
            if invoice.docstatus == 1:
                invoice.check_permission("cancel")
            # Never use force, ignore_links, ignore_permissions, or direct SQL
            # deletion. ERPNext must enforce payment and accounting dependencies.
            for row in linked_rows:
                frappe.db.set_value(
                    "Lease Invoice Schedule", row.name, "invoice_number", None,
                    update_modified=False,
                )

            if invoice.docstatus == 1:
                invoice.cancel()
            frappe.delete_doc("Sales Invoice", invoice_name)

            lease.add_comment(
                "Info",
                _("Deleted Sales Invoice {0} from Lease Invoice Schedule rows: {1}").format(
                    frappe.utils.escape_html(invoice_name),
                    ", ".join(frappe.utils.escape_html(r.name) for r in linked_rows),
                ),
            )
            results.append({"invoice": invoice_name, "status": "deleted", "rows": row_names})
        except Exception as exc:
            frappe.db.rollback(save_point="lease_invoice_cleanup")
            results.append({
                "invoice": invoice_name,
                "status": "failed",
                "rows": row_names,
                "reason": str(exc),
            })

    return {"results": results, "skipped": skipped}
