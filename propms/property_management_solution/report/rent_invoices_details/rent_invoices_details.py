# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from time import strptime
import calendar
from datetime import date, timedelta, datetime
from collections import OrderedDict
from frappe.utils import getdate, date_diff, month_diff, get_last_day, get_first_day, add_months, floor
from erpnext import get_company_currency, get_default_company
# from csf_tz.custom_api import print_out


def execute(filters=None):
    data = get_data(filters)
    columns = get_columns(filters)
    return columns, data


def get_data(filters):
    rows = []
    _from_date = "'{from_date}'".format(from_date=filters['from_date'])
    _to_date = "'{to_date}'".format(to_date=filters['to_date'])
    _company = "'{company}'".format(company=filters['company'])
    _items_grupe = filters.get('type_name')
    
    
    query = """ 
            SELECT
                name as invoice_id, 
                customer, 
                base_net_total as total, 
                net_total as foreign_total,
                currency, 
                conversion_rate as exchange_rate, 
                posting_date as date, 
                lease, 
                from_date, 
                to_date
            FROM
                `tabSales Invoice`
            WHERE
                docstatus = 1 
                AND company = {company} 
                AND DATE(posting_date) BETWEEN {start} AND {end} 
                AND lease != ""
                AND from_date != ""
                AND to_date != ""
            ORDER BY lease DESC, posting_date DESC
            """.format(start=_from_date,end=_to_date,company=_company)

    sales_invoices = frappe.db.sql(query,as_dict=True)

    for invoice in sales_invoices:
        _items_rwos = []
        append = False
        property_name = frappe.db.get_value("Lease",invoice['lease'],"property")
        invoice['property_name'] = property_name
        if invoice.total == invoice.foreign_total:
            invoice.foreign_total,invoice.exchange_rate = "", ""
        if filters.get("foreign_currency") and get_company_currency(filters.company) != filters.foreign_currency:
            months_obj = calculate_monthly_ammount(invoice.foreign_total,invoice.from_date,invoice.to_date)
        else:
            months_obj = calculate_monthly_ammount(invoice.total,invoice.from_date,invoice.to_date)
        if months_obj:
            for key,value in months_obj.items():
                invoice[key] = value

        
        invoice_id = "'{invoice_id}'".format(invoice_id=invoice['invoice_id'])

        query_items = """ 
            SELECT
                item_code, 
                base_net_amount as item_total, 
                net_amount as item_foreign_total,
                service_start_date as from_date, 
                service_end_date as to_date, 
                qty as quantity, 
                net_rate
            FROM
                `tabSales Invoice Item`
            WHERE
                parent = {invoice_id}
            """.format(invoice_id=invoice_id)

        items = frappe.db.sql(query_items,as_dict=True)
        for item in items:
            item_group = frappe.db.get_value("Item",item['item_code'],"item_group")
            item["item_group"] = item_group
            if filters.get("foreign_currency"):
                item.item_total = item.item_foreign_total
            months_obj = calculate_monthly_ammount(item.item_total,item.from_date,item.to_date)
            if months_obj:
                for key,value in months_obj.items():
                    item[key] = value
            if _items_grupe== "All":
                _items_rwos.append(item)
                append = True
            elif _items_grupe== item_group:
                _items_rwos.append(item)
                append = True
        if append and (filters.foreign_currency == invoice.currency or not filters.foreign_currency):
            rows.append(invoice)
            for item in _items_rwos:
                rows.append(item)
            rows.append({})

    return rows



def get_columns(filters):
    if filters.get("company"):
        currency = get_company_currency(filters["company"])
    else:
        company = get_default_company()
        currency = get_company_currency(company)

    if filters.get("foreign_currency"):
        _foreign_currency = filters["foreign_currency"]
    else:
        _foreign_currency = currency

    if _foreign_currency == currency:
        foreign_currency = "Foreign"
    else:
        foreign_currency = filters["foreign_currency"]
        
    columns = [
        {
        "label": "Property",
        "fieldname": "property_name",
        "fieldtype": "Link",
        "options": 'Property',
        "width": 100,
        },
        {
        "label": "Customer",
        "fieldname": "customer",
        "fieldtype": "Link",
        "options": 'Customer',
        "width": 100,
        },
        {
        "label": "Lease",
        "fieldname": "lease",
        "fieldtype": "Link",
        "options": 'Lease',
        "width": 100,
        },
        {
        "label": "Invoice",
        "fieldname": "invoice_id",
        "fieldtype": "Link",
        "options": 'Sales Invoice',
        "width": 150,
        },
        {
        "label": "Date",
        "fieldname": "date",
        "fieldtype": "date",
        "width": 100,
        },
        {
        "label": "Total {0}".format(currency),
        "fieldname": "total",
        "fieldtype": "Float",
        "width": 100,
        },
        {
        "label": "Exchange Rate",
        "fieldname": "exchange_rate",
        "fieldtype": "Float",
        "width": 100,
        },
        {
        "label": "Total {0}".format(foreign_currency or "Foreign"),
        "fieldname": "foreign_total",
        "fieldtype": "Float",
        "width": 100,
        },
        {
        "label": "Item",
        "fieldname": "item_code",
        "fieldtype": "Link",
        "options": 'Item',
        "width": 100,
        },
        {
        "label": "Quantity",
        "fieldname": "quantity",
        "width": 75,
        },
        {
        "label": "Item Total {0}".format(_foreign_currency),
        "fieldname": "item_total",
        "fieldtype": "Float",
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
 
    months_list = get_months(filters['from_date'],filters['to_date'])

    for month in months_list:
        columns.append({
            "label": "{0} {1}".format(month,_foreign_currency),
            "fieldname": month.lower(),
            "fieldtype": "Float",
            "width": 100,
        })
    return columns


def get_months(from_date,to_date):
    months_list = []
    dates = [from_date, to_date]
    start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
    months_obj = OrderedDict(((start + timedelta(_)).strftime(r"%b-%y"), None) for _ in range((end - start).days))
    for key, value in months_obj.items():
        months_list.append(key)
    return months_list


def check_full_month(from_date,to_date):
    month_start_day = get_first_day(from_date)
    month_end_day = get_last_day(from_date)
    if from_date == month_start_day and to_date == month_end_day:
        return True
    else:
        return False



def calculate_monthly_ammount(ammount,from_date,to_date):
    if ammount and from_date and to_date:
        monthly_ammount_obj = {}
        days = 0
        date = from_date
        end_date = to_date
        field_list = []
        first_last = 0
        sub_ammount = 0
        # days_list= []
 
        while date <= end_date:
            start_month = getdate(date).month
            end_month = getdate(to_date).month

            if start_month == end_month:
                last_day = end_date
                days_diff = date_diff(last_day,date)+1
                if check_full_month(date,last_day):
                    days_diff= 30
                days += days_diff
                # days_list.append(days_diff)
                month_filed= (get_months(str(date),str(last_day))[0]).lower()
                month_len = date_diff(get_last_day(date),get_first_day(date))
                field_list.append({
                    "days_diff" : days_diff,
                    "month_filed": month_filed,
                    "month_len": month_len
                })
                date = get_first_day(add_months(date,1))

            else:
                last_day = get_last_day(date)
                days_diff = date_diff(last_day,date)+1
                if check_full_month(date,last_day):
                    days_diff= 30
                days += days_diff
                # days_list.append(days_diff)
                month_filed= (get_months(str(date),str(last_day))[0]).lower()
                month_len = date_diff(get_last_day(date),get_first_day(date))
                field_list.append({
                    "days_diff" : days_diff,
                    "month_filed" :month_filed,
                    "month_len": month_len
                })
                date = get_first_day(add_months(date,1))

        if floor(days/30) != (days/30):
            days += 1 
        daily_ammount = ammount/(days)
        
        m = 1
        for i in field_list:
            if m ==1 and i["days_diff"] < 30:
                first_last += i["days_diff"]
            elif m == len(field_list) and i["days_diff"] < 30:
                first_last += i["days_diff"]
            else:
                sub_ammount += i["days_diff"] * daily_ammount
        
        n = 1
        for i in field_list:
            if n ==1 and i["days_diff"] < 30:
                monthly_ammount_obj[i["month_filed"]] = i["days_diff"] * ((ammount - sub_ammount)/first_last)
            elif n == len(field_list) and i["days_diff"] < 30:
                monthly_ammount_obj[i["month_filed"]] = i["days_diff"] * ((ammount - sub_ammount)/first_last)
            else:
                monthly_ammount_obj[i["month_filed"]] = i["days_diff"] * daily_ammount
            n += 1
        return monthly_ammount_obj