import frappe, calendar
from frappe import _
from datetime import *
def get_residential_columns(year):
    columns = [
        {"fieldname": "apartment_no", "label": _("Apartment No."), "fieldtype": "Data", "width": 150},
        {"fieldname": "client", "label": _("Client"), "fieldtype": "Data", "width": 150},
        {"fieldname": "advance_prev_year", "label": _("Advance RECD in 2019"), "fieldtype": "Data", "width": 150},
        {"fieldname": "invoice_no", "label": _("Invoice No."), "fieldtype": "Link","options":"Sales Invoice", "width": 150},
        {"fieldname": "from", "label": _("From"), "fieldtype": "Data", "width": 150},
        {"fieldname": "to", "label": _("To"), "fieldtype": "Data", "width": 150},
        {"fieldname": "invoice_amount", "label": _("Invoice Amount"), "fieldtype": "Data", "width": 150},
    ]
    months = months_array()
    for i in months:
        columns.append({"fieldname": i.lower(), "label": i + " " + str(year), "fieldtype": "Data", "width": 150})

    return columns


def get_sales_invoice(filters,data):
    lease_item = "and lease_item= '" + filters.get("rental") + "' "
    if filters.get("maintenance"):
        lease_item = "and (lease_item = 'Service Charge' or lease_item = 'Utility Charges') "
    query = """ SELECT * FROM `tabSales Invoice` 
                WHERE docstatus=%s {0} 
                ORDER by customer,from_date ASC""".format(lease_item) % (1)
    sales_invoices = frappe.db.sql(query,as_dict=True)
    previuos_customer = ""
    for i in sales_invoices:
        lease = frappe.get_value("Lease", i.lease, "property")
        obj = {
            "apartment_no":lease,
            "client": i.customer,
            "advance_prev_year": "",
            "invoice_no": i.name,
            "from": i.from_date if i.from_date else i.posting_date,
            "to":i.to_date - timedelta(days=1) if i.to_date else i.posting_date,
            "invoice_amount": i.total,
        }
        set_monthly_amount(i.from_date,i.to_date - timedelta(days=1) if i.to_date else "", obj,filters)
        if previuos_customer != i.customer:
            data.append({})
        previuos_customer = i.customer
        data.append(obj)

def set_monthly_amount(start_date, end_date, obj,filters):
    rate = get_rate(obj['invoice_no'],filters)
    if end_date and rate:
        check_dates(start_date,end_date,rate,obj)

def get_sales_invoice_maintenance(filters):
    pass

def check_dates(start_date,end_date,rate,obj):
    start = start_date
    no_minus = 0
    while start < end_date:
        month_string = start.strftime("%b")
        month_no_of_days = calendar.monthrange(start.year, start.month)[1]
        last_date = datetime(start.year, start.month, month_no_of_days).date()
        if (last_date - start).days >= 29 or (month_string == "Feb" and (last_date - start).days >= 27):
            if start.year == start_date.year:
                obj[month_string.lower()] = round(rate, 2)

        else:
            if start.year == start_date.year:
                obj[month_string.lower()] = round(round(rate / month_no_of_days,2) * (month_no_of_days - int(start.day)), 2)

        no_minus = month_no_of_days
        start += timedelta(days=month_no_of_days)


    start_last = start - timedelta(days=no_minus)

    if (end_date - start_last).days > 0:
        if start_last.year == start_date.year:
            month_string = end_date.strftime("%b")
            month_no_of_days = calendar.monthrange(end_date.year, end_date.month)[1]
            if int(end_date.day) >= 29 or (month_string == "Feb" and (end_date - start_last).days >= 27):
                obj[month_string.lower()] = round(rate, 2)
            else:
                obj[month_string.lower()] = round(round(rate / month_no_of_days,2) * (int(end_date.day)), 2)

def months_array():
    return ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def get_rate(invoice_name,filters):
    print("GET RATE")
    print(invoice_name)
    filters_value = " and item_code= '" + filters.get("rental") + "' "
    if filters.get("maintenance"):
        filters_value = "and (item_code = 'Service Charge' or item_code = 'Utility Charges')"
    query = """ SELECT rate FROM `tabSales Invoice Item` WHERE {0} {1}""".format( "parent = '" + invoice_name + "' ", filters_value)
    print(query)

    return frappe.db.sql(query, as_dict=True)[0].rate if len(frappe.db.sql(query, as_dict=True)) > 0 else ""