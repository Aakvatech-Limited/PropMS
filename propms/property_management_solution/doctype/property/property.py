# -*- coding: utf-8 -*-
# Copyright (c) 2018, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.utils.nestedset import NestedSet
import frappe


class Property(NestedSet):
    nsm_parent_field = "parent_property"

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
