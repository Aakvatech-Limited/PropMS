# -*- coding: utf-8 -*-
# Copyright (c) 2025, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class LeaseGroup(Document):
    def validate(self):
        # Prevent cancellation of individual leases in the group
        for lease in self.leases:
            lease_doc = frappe.get_doc("Lease", lease.lease)
            if lease_doc.docstatus == 2:
                frappe.throw("Individual leases in a group cannot be cancelled. Manage cancellation from the Lease Group.")

    def on_submit(self):
        # Optionally, create a single invoice for the group
        pass

    def on_cancel(self):
        # Cancel all child leases
        for lease in self.leases:
            lease_doc = frappe.get_doc("Lease", lease.lease)
            if lease_doc.docstatus == 1:
                lease_doc.cancel()


# Scheduler to collect leases suitable for Lease Group creation
def collect_leases_for_group():
    # Example criteria: leases with same customer and overlapping dates
    leases = frappe.get_all("Lease", fields=["name", "lease_customer", "property", "start_date", "end_date", "lease_group"])
    grouped = {}
    for lease in leases:
        if lease["lease_group"]:
            continue  # Already grouped
        key = lease["lease_customer"]
        grouped.setdefault(key, []).append(lease)
    for customer, lease_list in grouped.items():
        if len(lease_list) > 1:
            lease_group_doc = frappe.new_doc("Lease Group")
            lease_group_doc.customer = customer
            lease_group_doc.lease_group_name = f"Group-{customer}-{frappe.utils.nowdate()}"
            lease_group_doc.leases = []
            for lease in lease_list:
                lease_group_doc.append("leases", {
                    "lease": lease["name"],
                    "propery": lease["property"],
                    "lease_date": lease["start_date"],
                    "lease_customer": lease["lease_customer"]
                })
                frappe.db.set_value("Lease", lease["name"], "lease_group", lease_group_doc.lease_group_name)
            lease_group_doc.insert(ignore_permissions=True)
            frappe.db.commit()
