"""Backfill URL-only attachment links from predecessor leases to existing renewals."""

import frappe

from propms.property_management_solution.doctype.lease.lease import copy_renewal_attachment_links


def execute():
    renewals = frappe.get_all(
        "Lease",
        filters={"renewed_from": ["is", "set"]},
        fields=["name", "renewed_from", "company", "lease_customer"],
    )
    for renewal in renewals:
        if not renewal.renewed_from or not frappe.db.exists("Lease", renewal.renewed_from):
            continue
        source = frappe.db.get_value(
            "Lease", renewal.renewed_from, ["company", "lease_customer"], as_dict=True
        )
        if not source or source.company != renewal.company or source.lease_customer != renewal.lease_customer:
            continue
        copy_renewal_attachment_links(renewal.renewed_from, renewal.name)
