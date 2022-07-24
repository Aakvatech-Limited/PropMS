from __future__ import unicode_literals
import frappe


@frappe.whitelist()
def get_pos_data(cost_center):
    property = frappe.get_list("Property", filters={"cost_center": cost_center})
    lease = None
    one_lease = None
    if property:
        lease = frappe.get_all(
            "Lease",
            filters={"property": property[0].name},
            fields=["*"],
            order_by="end_date desc",
        )
    if lease:
        one_lease = frappe.get_doc("Lease", lease[0].name)
    return one_lease
