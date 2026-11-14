# Copyright (c) 2018, Aakvatech and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils.nestedset import NestedSet

from propms.lease_status_utils import get_active_leases_for_property


class Property(NestedSet):
	nsm_parent_field = "parent_property"

	def validate(self):
		self.validate_status_with_active_leases()

	def validate_status_with_active_leases(self):
		"""Prevent property status updates when active leases exist"""
		if not self.name or self.is_new():
			return

		# Check if status is changing
		old_doc = self.get_doc_before_save()
		if old_doc and old_doc.status == self.status:
			return  # Status not changing

		# If property has active leases, prevent status change
		active_leases = self.get_active_leases()
		if active_leases:
			lease_names = [lease.name for lease in active_leases]
			frappe.throw(
				_("Cannot change property status. Active leases exist: {0}").format(", ".join(lease_names))
			)

	def get_active_leases(self):
		"""Get current effective active leases for this property."""
		return get_active_leases_for_property(self.name)

	def on_trash(self, allow_root_deletion=True):
		super().on_trash(allow_root_deletion)


@frappe.whitelist()
def add_node():
	from frappe.desk.treeview import make_tree_args

	args = frappe.form_dict
	args = make_tree_args(**frappe.form_dict)

	if args["is_root"]:
		args["parent_property"] = None

	doc = frappe.get_doc(args)

	doc.save()


@frappe.whitelist()
def get_children(doctype, parent=None, company=None, is_root=False):
	"""Tree view children. v16 rejects raw SQL expressions in filters."""
	if is_root:
		parent = ""

	filters = [["company", "in", (company, None, "")]]
	if parent:
		filters.append(["parent_property", "=", parent])
	else:
		filters.append(["parent_property", "is", "not set"])

	return frappe.get_list(
		doctype,
		fields=["name as value", "is_group as expandable"],
		filters=filters,
		order_by="name",
	)
