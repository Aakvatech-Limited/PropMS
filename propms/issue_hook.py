from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import today
from erpnext.utilities.product import get_price
from erpnext.stock.get_item_details import get_pos_profile
from propms.auto_custom import get_latest_active_lease

def make_sales_invoice(doc, method):
    is_grouped = frappe.db.get_value("Property Management Settings", None, "group_maintenance_job_items")
    if not is_grouped:
        is_grouped =0
    is_grouped =int(is_grouped)
    company = frappe.db.get_value("Property Management Settings", None, "company")
    if not company:
        company = frappe.db.get_single_value('Global Defaults', 'default_company')
    cost_center = frappe.db.get_value("Property", doc.property_name, "cost_center")
    submit_maintenance_invoice = frappe.db.get_value("Property Management Settings", None, "submit_maintenance_invoice")
    if not submit_maintenance_invoice:
        submit_maintenance_invoice =0
    submit_maintenance_invoice =int(submit_maintenance_invoice)
    user_remarks= "Sales invoice for Maintenance Job Card {0}".format(doc.name)
    leas = get_latest_active_lease(doc.property_name)
    
    def _make_sales_invoice(items_list= None, pos= None): 
        if not len(items_list) > 0 or not doc.customer:
            return      
        invoice_doc = frappe.get_doc(dict(
            doctype = "Sales Invoice",
            customer = doc.customer,
            company = company,
            posting_date = today(),
            due_date = today(),
            ignore_pricing_rule = 1,
            items = items_list,
            update_stock = 1,
            remarks = user_remarks,
            cost_center = cost_center,
            lease = leas
            )).insert(ignore_permissions=True)
        if invoice_doc:
            frappe.flags.ignore_account_permission = True
            if submit_maintenance_invoice == 1 and not pos:
                invoice_doc.submit()
            if pos:
                make_sales_pos_payment(invoice_doc)
            frappe.msgprint(str("Sales invoice Created {0}".format(invoice_doc.name)))
            for item_row in doc.materials_required:
                if item_row.item and item_row.quantity and item_row.invoiced == 1 and not item_row.sales_invoice:
                    item_row.sales_invoice = invoice_doc.name
    

    def get_account_pyment_mode(mode_of_payment,company):
        mode_of_payment_doc = frappe.get_doc("Mode of Payment",mode_of_payment)
        if mode_of_payment_doc:
            for account_row in mode_of_payment_doc.accounts:
                if account_row.company == company:
                    return account_row.default_account
        else:
            frappe.throw(_("Default Account Not Defined In Mode of Payment"))
    


    def make_sales_pos_payment(invoice_doc):
        user_pos_profile = get_pos_profile(company)
        invoice_doc.is_pos = 1
        invoice_doc.pos_profile = user_pos_profile.name
        payment_row = invoice_doc.append("payments",{})
        payment_row.mode_of_payment = "Cash"
        payment_row.amount = invoice_doc.grand_total
        payment_row.base_amount = invoice_doc.grand_total
        payment_row.account = get_account_pyment_mode("Cash",invoice_doc.company)
        if submit_maintenance_invoice == 1:
            invoice_doc.submit()
        else :
            invoice_doc.save()

    def check_is_pos():
        for item_row in doc.materials_required:
            if item_row.item and item_row.quantity and item_row.material_status =="Fulfilled"and not item_row.sales_invoice and item_row.is_pos: 
                return True
        return False

    if is_grouped == 1 and not check_is_pos():
        items = []
        for item_row in doc.materials_required:
            if item_row.item and item_row.quantity and item_row.material_status =="Fulfilled"and not item_row.sales_invoice:
                item_dict = dict(
                    item_code = item_row.item,
                    qty = item_row.quantity,
                    rate = item_row.rate,
                    cost_center = cost_center,
                )
                items.append(item_dict)
                item_row.invoiced = 1
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
                item_row.invoiced = 1
                if item_row.is_pos:
                    pos =True
                else:
                    pos = False
                _make_sales_invoice(items,pos)   


@frappe.whitelist()
def get_item_rate(item,customer):
    price_list = frappe.db.get_value("Customer", customer, "default_price_list")
    customer_group = frappe.db.get_value("Customer", customer, "customer_group")
    company = frappe.db.get_single_value('Global Defaults', 'default_company')
    rate = get_price(item,price_list,customer_group,company)
    if rate:
        return rate["price_list_rate"]


@frappe.whitelist()
def get_items_group():
    property_doc = frappe.get_doc("Property Management Settings")
    items_group_list = []
    for items_group in property_doc.maintenance_item_group:
        items_group_list.append(items_group.item_group)
    return items_group_list