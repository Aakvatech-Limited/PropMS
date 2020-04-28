# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from time import strptime
import calendar
from datetime import date, timedelta
from csf_tz.custom_api import print_out


def execute(filters=None):
	columns, data = [], []
	return columns, data


def get_sales_invoice(filters,data,from_other=None, months=None):
    # print_out(data)
    total = {}
    lease_item = "'" + filters.get("rental") + "' "
    # print(lease_item)
    if filters.get("maintenance"):
        lease_item = "'Service Charge - " + filters.get("rental").split()[0] + "'"

    query = """ SELECT * FROM `tabSales Invoice` AS SI WHERE EXISTS (SELECT * FROM `tabSales Invoice Item` AS SIT WHERE SIT.item_code = {0} and SIT.parent = SI.name )
                and SI.docstatus=%s
                ORDER by SI.customer,SI.from_date ASC""".format(lease_item) % (1)

    sales_invoices = frappe.db.sql(query,as_dict=True)
    previuos_customer = ""
    for i in sales_invoices:
        lease = frappe.get_value("Lease", i.lease, "property")
        obj = {
            "apartment_no":lease or "",
            "client": i.customer,
            "advance_prev_year": "",
            "invoice_no": i.name,
            "from": i.from_date if i.from_date else i.posting_date,
            "to":i.to_date - timedelta(days=1) if i.to_date else i.posting_date,
            "invoice_amount": i.total,
        }
        set_monthly_amount(i.from_date,i.to_date - timedelta(days=1) if i.to_date else "", obj,filters,total,months)
        if previuos_customer != i.customer:
            data.append({})
        previuos_customer = i.customer
        data.append(obj)
        if from_other:
            data.append(total)
    # print_out(data)



def get_utility_sales_invoice(data, from_other=None, months=None):
    total = {}
    lease_item = "'Utility Charges' "
    query = """ SELECT * FROM `tabSales Invoice` AS SI WHERE EXISTS (SELECT * FROM `tabSales Invoice Item` AS SIT WHERE SIT.item_code = {0} and SIT.parent = SI.name )
                and SI.docstatus=%s
                ORDER by SI.customer,SI.from_date ASC""".format(lease_item) % (1)

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
        set_monthly_amount(i.from_date,i.to_date - timedelta(days=1) if i.to_date else "", obj,total,months)
        if previuos_customer != i.customer:
            data.append({})
        previuos_customer = i.customer
        data.append(obj)
        if from_other:
            data.append(total)


def set_monthly_amount(start_date, end_date, obj,total,months):
    rate = get_rate(obj['invoice_no'])
    if end_date and rate:
        check_dates(start_date,end_date,rate,obj,total,months)


def check_dates(start_date,end_date,rate,obj,total,months):
    start = start_date
    no_minus = 0
    while start < end_date:
        month_string = start.strftime("%b")
        month_no_of_days = calendar.monthrange(start.year, start.month)[1]
        last_date = date(start.year, start.month, month_no_of_days)
        if (last_date - start).days >= 29 or (month_string == "Feb" and (last_date - start).days >= 27):
            if start.year == start_date.year:
                obj[month_string.lower()] = round(rate, 2)
                if months and month_string.lower() in months:
                    total[month_string.lower()] = round(rate, 2) + round(total[month_string.lower()],2) if month_string.lower() in total else round(rate, 2)
        else:
            if start.year == start_date.year:
                obj[month_string.lower()] = round(round(rate / month_no_of_days,2) * (month_no_of_days - int(start.day)), 2)
                if months and month_string.lower() in months:
                    total[month_string.lower()] = round(
                        round(rate / month_no_of_days, 2) * (month_no_of_days - int(start.day)), 2) + round(total[
                                                                                                                month_string.lower()],
                                                                                                            2) if month_string.lower() in total else round(
                        round(rate / month_no_of_days, 2) * (month_no_of_days - int(start.day)), 2)
        no_minus = month_no_of_days
        start += timedelta(days=month_no_of_days)


    start_last = start - timedelta(days=no_minus)


def get_rate(invoice_name):
    filters_value = "and item_code = 'Utility Charges'"
    query = """ SELECT rate FROM `tabSales Invoice Item` WHERE {0} {1}""".format( "parent = '" + invoice_name + "' ", filters_value)
    print(query)