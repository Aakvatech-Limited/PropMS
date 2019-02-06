from __future__ import unicode_literals
from collections import defaultdict
from datetime import date
from datetime import datetime
from datetime import timedelta
from erpnext.accounts.utils import get_fiscal_year
from erpnext.controllers.accounts_controller import get_taxes_and_charges
from frappe import throw, msgprint, _
from frappe.client import delete
from frappe.desk.notifications import clear_notifications
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cint, get_gravatar, format_datetime, now_datetime,add_days,today,formatdate,date_diff,getdate,add_months
from frappe.utils.password import update_password as _update_password
from frappe.utils.user import get_system_managers
import collections
import frappe
import frappe.permissions
import frappe.share
import json
import logging
import math
import random
import re
import string
import time
import traceback
import urllib
from frappe.utils import flt, add_days
from frappe.utils import get_datetime_str, nowdate

@frappe.whitelist()
def app_error_log(title,error):
	d = frappe.get_doc({
			"doctype": "Custom Error Log",
			"title":str("User:")+str(title),
			"error":traceback.format_exc()
		})
	d = d.insert(ignore_permissions=True)
	return d	



@frappe.whitelist()
def makeLeaseInvoice(self,method):
	try:
		frappe.msgprint("2")
		if len(self.lease_item)>=1:
			item_arr=[]
			for item in self.lease_item:
				frappe.msgprint("1")
				item_json={}
				if item.frequency=="Quarterly":
					item_json["item_code"]=item.lease_item
					item_json["qty"]=3
					item_json["rate"]=item.amount
					item_arr.append(item_json)
					makeInvoice(self.start_date,item.paid_by,item_arr,item.currency_code)
					del item_arr[:]
				if item.frequency=="Monthly":
					item_json["item_code"]=item.lease_item
					item_json["qty"]=1
					item_json["rate"]=item.amount
					item_arr.append(item_json)
					makeInvoice(self.start_date,item.paid_by,item_arr,item.currency_code)
					del item_arr[:]
					
	except Exception as e:
		error_log=app_error_log(frappe.session.user,str(e))


@frappe.whitelist()
def makeInvoice(date,customer,items,currency=None):
	try:
		sales_invoice=frappe.get_doc(dict(
					doctype='Sales Invoice',
					posting_date=date,
					items=json.loads(items),
					customer=str(customer),
					due_date=date,
					currency=currency
		)).insert()
		return sales_invoice
	except Exception as e:
		error_log=app_error_log(frappe.session.user,str(e))


@frappe.whitelist()
def leaseInvoiceAutoCreate():
	try:
		lease_invoice=frappe.get_all("Lease Invoice Schedule",filters={"date_to_invoice":today()},fields=["name"])
		item_dict=[]
		for row in lease_invoice:
			invoice_item=frappe.get_doc("Lease Invoice Schedule",row.name)
			item_json={}
			item_json["item_code"]=invoice_item.lease_item
			item_json["qty"]=invoice_item.qty
			item_json["rate"]=invoice_item.rate
			item_dict.append(item_json)
			res=makeInvoice(invoice_item.date_to_invoice,invoice_item.paid_by,json.dumps(item_dict),invoice_item.currency)
			if res:
				frappe.db.set_value("Lease Invoice Schedule",invoice_item.name,"invoice_number",res.name)


	except Exception as e:
		error_log=app_error_log(frappe.session.user,str(e))




@frappe.whitelist()
def test():
	return today()

