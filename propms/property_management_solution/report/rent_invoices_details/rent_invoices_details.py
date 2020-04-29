# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from time import strptime
import calendar
from datetime import date, timedelta, datetime
from collections import OrderedDict
from csf_tz.custom_api import print_out


def execute(filters=None):
    data = get_data(filters)
    columns = get_columns(filters)
    # print_out(filters)
    # get_data(filters)
    return columns, data

months = []

def get_data(filters):
    _from_date = "'{from_date}'".format(from_date=filters['from_date'])
    _to_date = "'{to_date}'".format(to_date=filters['to_date'])
    _company = "'{company}'".format(company=filters['company'])
    _items_grupe = filters['Type']
    
    # query = """ 
    #         SELECT
    #             si.*,
    #             si_item.*
    #         FROM
    #             `tabSales Invoice` si,
    #             `tabSales Invoice Item` si_item 
    #         WHERE
    #             si.name = si_item.parent 
    #             AND si.docstatus = 1 
    #             AND si.company = {company} 
    #             AND DATE(si.posting_date) BETWEEN {start} AND {end} 
    #             AND si.lease != ""
    #         ORDER BY si.posting_date DESC, si.name DESC
    #         """.format(start=_from_date,end=_to_date,company=_company)

    query = """ 
            SELECT
                name as invoice_id,customer,net_total as total,posting_date as date,lease,from_date,to_date
            FROM
                `tabSales Invoice`
            WHERE
                docstatus = 1 
                AND company = {company} 
                AND DATE(posting_date) BETWEEN {start} AND {end} 
                AND lease != ""
            ORDER BY posting_date DESC, name DESC
            """.format(start=_from_date,end=_to_date,company=_company)

    sales_invoices = frappe.db.sql(query,as_dict=True)
    # month = int(filters['from_date'].split('-')[1])
    # print_out(calendar.month_name[month])
    
    rows = []
    for invoice in sales_invoices:
        property_name = frappe.db.get_value("Lease",invoice['lease'],"property")
        # print_out(property_name)
        invoice['property_name'] = property_name
        # print_out(invoice)

    return sales_invoices




def get_columns(filters):
    columns = [
        {
        "label": "Property",
        "fieldname": "property_name",
        "fieldtype": "Data",
        "width": 100,
        },
        {
        "label": "Customer",
        "fieldname": "customer",
        "fieldtype": "link",
        "width": 100,
        },
        {
        "label": "Lease",
        "fieldname": "lease",
        "fieldtype": "Data",
        "width": 100,
        },
        {
        "label": "Invoice",
        "fieldname": "invoice_id",
        "fieldtype": "Data",
        "width": 100,
        },
        {
        "label": "Date",
        "fieldname": "date",
        "fieldtype": "date",
        "width": 100,
        },
        {
        "label": "Item",
        "fieldname": "item",
        "fieldtype": "link",
        "width": 100,
        },
        {
        "label": "Total",
        "fieldname": "total",
        "fieldtype": "Currency",
        "width": 100,
        },
        {
        "label": "From Date",
        "fieldname": "from_date",
        "fieldtype": "date",
        "width": 100,
        },
        {
        "label": "To Date",
        "fieldname": "to_date",
        "fieldtype": "date",
        "width": 100,
        },
    ]
    # month_int_from = int(filters['from_date'].split('-')[1])
    # month_int_to = int(filters['to_date'].split('-')[1])

    dates = [filters['from_date'], filters['to_date']]
    start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
    months_obj = OrderedDict(((start + timedelta(_)).strftime(r"%b-%y"), None) for _ in range((end - start).days))
    # print_out(months_list)

    for key, value in months_obj.items():
        print_out(key)
        columns.append({
            "label": key,
            "fieldname": key.lower(),
            "fieldtype": "Currency",
            "width": 100,
        })
    # columns.append({
    #     "label": "Total",
    #     "fieldname": "total",
    #     "fieldtype": "Currency",
    #     "width": 180,
    # })
    return columns


# def get_sales_invoice1(filters,data,from_other=None, months=None):
#     # print_out(data)
#     total = {}
#     lease_item = "'" + filters.get("rental") + "' "
#     # print(lease_item)
#     if filters.get("maintenance"):
#         lease_item = "'Service Charge - " + filters.get("rental").split()[0] + "'"

#     query = """ SELECT * FROM `tabSales Invoice` AS SI WHERE EXISTS (SELECT * FROM `tabSales Invoice Item` AS SIT WHERE SIT.item_code = {0} and SIT.parent = SI.name )
#                 and SI.docstatus=%s
#                 ORDER by SI.customer,SI.from_date ASC""".format(lease_item) % (1)

#     sales_invoices = frappe.db.sql(query,as_dict=True)
#     previuos_customer = ""
#     for i in sales_invoices:
#         lease = frappe.get_value("Lease", i.lease, "property")
#         obj = {
#             "apartment_no":lease or "",
#             "client": i.customer,
#             "advance_prev_year": "",
#             "invoice_no": i.name,
#             "from": i.from_date if i.from_date else i.posting_date,
#             "to":i.to_date - timedelta(days=1) if i.to_date else i.posting_date,
#             "invoice_amount": i.total,
#         }
#         set_monthly_amount(i.from_date,i.to_date - timedelta(days=1) if i.to_date else "", obj,filters,total,months)
#         if previuos_customer != i.customer:
#             data.append({})
#         previuos_customer = i.customer
#         data.append(obj)
#         if from_other:
#             data.append(total)
    # print_out(data)



# def get_utility_sales_invoice(data, from_other=None, months=None):
#     total = {}
#     lease_item = "'Utility Charges' "
#     query = """ SELECT * FROM `tabSales Invoice` AS SI WHERE EXISTS (SELECT * FROM `tabSales Invoice Item` AS SIT WHERE SIT.item_code = {0} and SIT.parent = SI.name )
#                 and SI.docstatus=%s
#                 ORDER by SI.customer,SI.from_date ASC""".format(lease_item) % (1)

#     sales_invoices = frappe.db.sql(query,as_dict=True)
#     previuos_customer = ""
#     for i in sales_invoices:
#         lease = frappe.get_value("Lease", i.lease, "property")
#         obj = {
#             "apartment_no":lease,
#             "client": i.customer,
#             "advance_prev_year": "",
#             "invoice_no": i.name,
#             "from": i.from_date if i.from_date else i.posting_date,
#             "to":i.to_date - timedelta(days=1) if i.to_date else i.posting_date,
#             "invoice_amount": i.total,
#         }
#         set_monthly_amount(i.from_date,i.to_date - timedelta(days=1) if i.to_date else "", obj,total,months)
#         if previuos_customer != i.customer:
#             data.append({})
#         previuos_customer = i.customer
#         data.append(obj)
#         if from_other:
#             data.append(total)


# def set_monthly_amount(start_date, end_date, obj,total,months):
#     rate = get_rate(obj['invoice_no'])
#     if end_date and rate:
#         check_dates(start_date,end_date,rate,obj,total,months)


# def check_dates(start_date,end_date,rate,obj,total,months):
#     start = start_date
#     no_minus = 0
#     while start < end_date:
#         month_string = start.strftime("%b")
#         month_no_of_days = calendar.monthrange(start.year, start.month)[1]
#         last_date = date(start.year, start.month, month_no_of_days)
#         if (last_date - start).days >= 29 or (month_string == "Feb" and (last_date - start).days >= 27):
#             if start.year == start_date.year:
#                 obj[month_string.lower()] = round(rate, 2)
#                 if months and month_string.lower() in months:
#                     total[month_string.lower()] = round(rate, 2) + round(total[month_string.lower()],2) if month_string.lower() in total else round(rate, 2)
#         else:
#             if start.year == start_date.year:
#                 obj[month_string.lower()] = round(round(rate / month_no_of_days,2) * (month_no_of_days - int(start.day)), 2)
#                 if months and month_string.lower() in months:
#                     total[month_string.lower()] = round(
#                         round(rate / month_no_of_days, 2) * (month_no_of_days - int(start.day)), 2) + round(total[
#                                                                                                                 month_string.lower()],
#                                                                                                             2) if month_string.lower() in total else round(
#                         round(rate / month_no_of_days, 2) * (month_no_of_days - int(start.day)), 2)
#         no_minus = month_no_of_days
#         start += timedelta(days=month_no_of_days)


#     start_last = start - timedelta(days=no_minus)


# def get_rate(invoice_name):
#     filters_value = "and item_code = 'Utility Charges'"
#     query = """ SELECT rate FROM `tabSales Invoice Item` WHERE {0} {1}""".format( "parent = '" + invoice_name + "' ", filters_value)
#     print(query)