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


# Remarked as this is no longer necessary
# @frappe.whitelist()
# def makeLeaseInvoice(self,method):
	# try:
		# #frappe.msgprint("2")
		# if len(self.lease_item)>=1:
			# item_arr=[]
			# item_invoice_frequency = {
					# "Monthly": 1,
					# "Quarterly": 3,
					# "6 Months": 6,
					# "Annually": 12
			# }
			# for item in self.lease_item:
				# frequency_factor = item_invoice_frequency.get(item.frequency, "Invalid frequency")
				# if frequency_factor == "Invalid frequency":
					# frappe.msgprint("Invalid frequency: " + item.frequency + " not found. Contact the developers!")
				# item_json={}
				# item_json["item_code"]=item.lease_item
				# item_json["qty"]=frequency_factor
				# item_json["rate"]=item.amount
				# item_arr.append(item_json)
				# makeInvoice(self.start_date,item.paid_by,item_arr,item.currency_code)
				# del item_arr[:]
					
	# except Exception as e:
		# error_log=app_error_log(frappe.session.user,str(e))


@frappe.whitelist()
def makeInvoice(date,customer,items,currency=None,lease=None,lease_item=None):
	try:
		propm_setting=frappe.get_doc("Property Management Settings","Property Management Settings")
		tax_account = frappe.get_doc("Account", str(propm_setting.default_tax_account_head))
		tax=[]
		tax_json={}
		tax_json["charge_type"]="On Net Total"
		tax_json["account_head"]=tax_account.name
		tax_json["description"]="VAT account"
		tax_json["rate"]=tax_account.tax_rate
		tax.append(tax_json)
		sales_invoice=frappe.get_doc(dict(
					doctype='Sales Invoice',
					posting_date=date,
					items=json.loads(items),
					customer=str(customer),
					due_date=date,
					currency=currency,
					lease=lease,
					lease_item=lease_item,
					taxes=tax
		)).insert()
		return sales_invoice
	except Exception as e:
		error_log=app_error_log(frappe.session.user,str(e))


@frappe.whitelist()
def leaseInvoiceAutoCreate():
	try:
		lease_invoice = frappe.get_all("Lease Invoice Schedule", filters = {"date_to_invoice": ['between', ("2019-01-01", today())], "invoice_number": ""}, fields = ["name", "date_to_invoice", "invoice_number"])
		#frappe.msgprint("Lease being generated for " + str(lease_invoice))
		for row in lease_invoice:
			item_dict = []
			item_json = {}
			invoice_item = frappe.get_doc("Lease Invoice Schedule", row.name)
			#frappe.msgprint(row.name + " - " + str(invoice_item.date_to_invoice))
			item_json["item_code"] = invoice_item.lease_item
			item_json["qty"] = invoice_item.qty
			item_json["rate"] = invoice_item.rate
			item_dict.append(item_json)
			res = makeInvoice(invoice_item.date_to_invoice, invoice_item.paid_by, json.dumps(item_dict), invoice_item.currency, invoice_item.parent, invoice_item.lease_item)
			#frappe.msgprint(str(res))
			if res:
				frappe.db.set_value("Lease Invoice Schedule",invoice_item.name, "invoice_number", res.name)
				frappe.msgprint("Lease generated with number: " + str(res.name))
	except Exception as e:
		error_log = app_error_log(frappe.session.user, str(e))

@frappe.whitelist()
def test():
	return today()

