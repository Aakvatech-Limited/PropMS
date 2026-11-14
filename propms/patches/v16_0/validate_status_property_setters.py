"""Fail v16 migration before DocType sync if status fields have site Property Setters.

No Property Setter is modified or removed automatically. Administrators must
review and remove conflicting site overrides explicitly before upgrading.
"""

import frappe
from frappe import _


STATUS_FIELDS = (("Lease", "lease_status"), ("Property", "status"))


def execute():
	conflicts = []
	for doctype, fieldname in STATUS_FIELDS:
		rows = frappe.get_all(
			"Property Setter",
			filters={"doc_type": doctype, "field_name": fieldname},
			fields=["name", "property", "value"],
			order_by="name",
		)
		for row in rows:
			conflicts.append(f"{row.name} ({doctype}.{fieldname}, {row.property}={row.value})")

	if conflicts:
		frappe.throw(
			_(
				"PropMS v16 migration blocked: Property Setters override Lease.lease_status "
				"or Property.status. Review and remove these site overrides manually "
				"before running migrate again: {0}"
			).format("; ".join(conflicts)),
			title=_("Conflicting Property Setters"),
		)
