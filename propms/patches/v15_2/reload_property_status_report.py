import frappe


def execute():
    """Force re-import of Property Status Report to drop its orphan "Lease Manager" role row.

    Standard Report fixtures are only re-imported when the file's `modified`
    timestamp is newer than the database row, so a plain fixture edit never
    reaches sites that already have the report.
    """
    frappe.reload_doc(
        "property_management_solution",
        "report",
        "property_status_report",
        force=True,
    )
