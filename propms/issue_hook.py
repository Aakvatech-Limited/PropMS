from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import today

def make_sales_invoice(doc, method):
    is_grouped = frappe.db.get_value("DSR Settings", None, "group_maintenance_job_items")
    if not is_grouped:
        is_grouped =0
    is_grouped =int(is_grouped)
    user_remarks= "Sales invoice for Maintenance Job Card {0}".format(doc.name)
    
    def _make_sales_invoice(items_list = None): 
        if not len(items) > 0 or not doc.customer:
            return      
        invoice_doc = frappe.get_doc(dict(
            doctype = "Sales Invoice",
            customer = doc.customer,
            company = frappe.db.get_single_value('Global Defaults', 'default_company'),
            posting_date = today(),
            due_date = today(),
            ignore_pricing_rule = 1,
            items = items_list,
            update_stock = 1,
            remarks = user_remarks,
            )).insert(ignore_permissions=True)
        if invoice_doc:
            frappe.flags.ignore_account_permission = True
            invoice_doc.submit()
            frappe.msgprint(str("Sales invoice Created {0}".format(invoice_doc.name)))
            for item_row in doc.materials_required:
                if item_row.item and item_row.quantity and item_row.material_status =="Invoiced"and not item_row.sales_invoice:
                    item_row.sales_invoice = invoice_doc.name
                    item_row.material_status = "Invoiced"

    if is_grouped == 1:
        items = []
        for item_row in doc.materials_required:
            if item_row.item and item_row.quantity and item_row.material_status =="Fulfilled"and not item_row.sales_invoice:
                item_dict = dict(
                    item_code = item_row.item,
                    qty = item_row.quantity,
                    rate = item_row.rate,
                )
                items.append(item_dict)
                item_row.material_status = "Invoiced"
        _make_sales_invoice(items)

    else :
        for item_row in doc.materials_required:
            if item_row.item and item_row.quantity and item_row.material_status =="Fulfilled"and not item_row.sales_invoice:
                items = []
                item_dict = dict(
                    item_code = item_row.item,
                    qty = item_row.quantity,
                    rate = item_row.rate,
                )
                items.append(item_dict)
                item_row.material_status = "Invoiced"
                _make_sales_invoice(items)   

