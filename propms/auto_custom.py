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
from frappe.utils import cint, format_datetime,get_datetime_str,now_datetime,add_days,today,formatdate,date_diff,getdate,add_months
from frappe.utils.password import update_password as _update_password
from frappe.utils.user import get_system_managers
from dateutil import relativedelta
import collections
import calendar
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
def makeSalesInvoice(self,method):
	try:
		if self.doctype=="Material Request":

			if self.status=="Issued":
				result=checkIssue(self.name)
				if not result==False:
					items=[]
					issue_details=frappe.get_doc("Issue",result)
					if issue_details.customer:
						material_request_details=frappe.get_doc("Material Request",self.name)
						if not material_request_details.sales_invoice:
							if not len(material_request_details.items)==0:					
								for item in material_request_details.items:
									item_json={}
									item_json["item_code"]=item.item_code
									item_json["qty"]=item.qty
									items.append(item_json)
			
								sales_invoice = frappe.get_doc(dict(
										doctype='Sales Invoice',
										company=frappe.db.get_single_value('Global Defaults', 'default_company'),
										fiscal_year=frappe.db.get_single_value('Global Defaults', 'current_fiscal_year'),
										posting_date=today(),
										items=items,
										customer=str(issue_details.customer),
										due_date=add_days(today(),2),
										update_stock=1
								)).insert()
								if sales_invoice.name:
									assignInvoiceNameInMR(sales_invoice.name,material_request_details.name)
			
			changeStatusIssue(self.name,self.status)
		else:
			if self.customer:
				if not len(self.materials_required)==0:
					items=[]
					for row in self.materials_required:
						material_request_details=frappe.get_doc("Material Request",row.material_request)
						if material_request_details.status=="Issued" and not material_request_details.sales_invoice:
						
							if not len(material_request_details.items)==0:
								for item in material_request_details.items:
									item_json={}
									item_json["item_code"]=item.item_code
									item_json["qty"]=item.qty
									items.append(item_json)
			
					
					

								sales_invoice = frappe.get_doc(dict(
										doctype='Sales Invoice',
										company=frappe.db.get_single_value('Global Defaults', 'default_company'),
										fiscal_year=frappe.db.get_single_value('Global Defaults', 'current_fiscal_year'),
										posting_date=today(),
										items=items,
										customer=str(self.customer),
										due_date=add_days(today(),2),
										update_stock=1
								)).insert()
								if sales_invoice.name:
									assignInvoiceNameInMR(sales_invoice.name,material_request_details.name)
									
			


	except Exception as e:
		error_log=app_error_log(frappe.session.user,str(e))



def checkIssue(name):
	data=frappe.db.sql("""select parent from `tabIssue Materials Detail` where material_request=%s""",name)
	if data:
		if not data[0][0]==None:
			return data[0][0]
		else:
			return False
	else:
		return False


def assignInvoiceNameInMR(invoice,pr):
	frappe.db.sql("""update `tabMaterial Request` set sales_invoice=%s where name=%s""",(invoice,pr))


@frappe.whitelist()
def changeStatusKeyset(self,method):
	try:
		keyset_name=getKeysetName(self.key_set)
		if keyset_name:
			doc=frappe.get_doc("Key Set", keyset_name)
			if self.returned:
				doc.status="In"
			else:
				doc.status="Out"
			doc.save()
		else:
			frappe.throw("Key set not found - {0}.".format(self.key_set))

	except Exception as e:
		error_log=app_error_log(frappe.session.user,str(e))


def getKeysetName(name):
	data=frappe.db.sql("""select name from `tabKey Set` where name=%s""",name)
	if data:
		if not data[0][0]==None:
			return data[0][0]
		else:
			return False
	else:
		return False

@frappe.whitelist()
def changeStatusIssue(name,status):
	try:
		issue_name=getIssueName(name)
		if issue_name:
			doc=frappe.get_doc("Issue Materials Detail",issue_name)
			doc.material_status=status
			doc.save()

	except Exception as e:
		error_log=app_error_log(frappe.session.user,str(e))

	

	

def getIssueName(name):
	data=frappe.db.sql("""select name from `tabIssue Materials Detail` where material_request=%s""",name)
	if data:
		if not data[0][0]==None:
			return data[0][0]
		else:
			return False
	else:
		return False


@frappe.whitelist()
def validateSalesInvoiceItemDuplication(self,method):
	for item in self.items:
		for item_child in self.items:
			if not item.name==item_child.name:
				if item.item_code==item_child.item_code:
					frappe.throw("Duplicate Item Exists - {0}. Duplications are not allowed.".format(item.item_code))


@frappe.whitelist()
def statusChangeBeforeLeaseExpire():
	try:
		lease_doclist=frappe.get_all("Lease",filters=[["Lease","end_date","Between",[str(today()),str(add_months(today(),3))]]],fields=["name","property"])
		if lease_doclist:
			for lease in lease_doclist:
				property_doc=frappe.get_doc("Property",lease.property)
				if not property_doc.status=="Off lease in 3 months":
					frappe.db.set_value("Property",lease.property,"status","Off lease in 3 months")
					


	except Exception as e:
		error_log=app_error_log(frappe.session.user,str(e))

@frappe.whitelist()
def statusChangeAfterLeaseExpire():
	try:
		lease_doclist=frappe.get_all("Lease",filters=[["Lease","end_date","=",add_days(today(),-1)]],fields=["name","property"])
		if lease_doclist:
			for lease in lease_doclist:
				property_doc=frappe.get_doc("Property",lease.property)
				if not property_doc.status=="Available":
					frappe.db.set_value("Property",lease.property,"status","Available")


	except Exception as e:
		error_log=app_error_log(frappe.session.user,str(e))


@frappe.whitelist()
def getCheckList():
	checklist_doc=frappe.get_doc("Checklist Checkup Area","Takeover")
	if checklist_doc:
		check_list=[]
		for task in checklist_doc.task:
			check={}
			check["checklist_task"]=task.task_name
			check_list.append(check)
		return check_list


@frappe.whitelist()
def makeDailyCheckListForTakeover(source_name, target_doc=None, ignore_permissions=True):
	try:
		def set_missing_values(source, target):
			target.checkup_date=today()
			target.area='Takeover'

		doclist = get_mapped_doc("Lease",source_name,
			{"Lease": {
				"doctype": "Daily Checklist",
				"field_map": {
					"property":"property"
				}
			}}, target_doc, set_missing_values, ignore_permissions=ignore_permissions)
		return doclist

	except Exception as e:
		error_log=app_error_log(frappe.session.user,str(e))


@frappe.whitelist()
def makeJournalEntry(customer,date,amount):
	try:
		propm_setting=frappe.get_doc("PropMS Settings","Propms Setting")
		j_entry=[]
		j_entry_debit={}
		j_entry_debit["account"]='Debtors - PMC'
		j_entry_debit["party_type"]='Customer'
		j_entry_debit["party"]=customer
		j_entry_debit["debit_in_account_currency"]=amount
		j_entry.append(j_entry_debit)
		j_entry_credit={}
		j_entry_credit["account"]='Cash - PMC'
		j_entry_credit["credit_in_account_currency"]=amount
		j_entry.append(j_entry_credit)
		j_entry=frappe.get_doc(dict(
			doctype="Journal Entry",
			posting_date=date,
			company=propm_setting.company,
			accounts=j_entry,
			mode_of_payment=propm_setting.security_deposit_payment_type	
		)).insert()
		return j_entry.name

	except Exception as e:
		error_log=app_error_log(frappe.session.user,str(e))


@frappe.whitelist()
def getMonthADD(date,month):
	return add_months(getdate(date),int(month))

@frappe.whitelist()
def getDateDiff(date1,date2):
	return date_diff(getdate(date1),getdate(date2))

@frappe.whitelist()
def getNumberOfDays(date):
	return calendar.monthrange(getdate(date).year,getdate(date).month)[1]

@frappe.whitelist()
def getMonthNo(date1,date2):
	d1=getdate(date1)
	d2=getdate(date2)
	return diff_month(datetime(d1.year,d1.month,d1.day), datetime(d2.year,d2.month,d2.day))

@frappe.whitelist()
def makeInvoiceSchedule(date,item,paid_by,item_name,name,qty,rate,currency=None):
	try:
		doc=frappe.get_doc(dict(
			doctype="Lease Invoice Schedule",
			parent=name,
			parentfield="lease_invoice_schedule",
			parenttype="lease",
			lease_item=item,
			date_to_invoice=date,
			paid_by=paid_by,
			lease_item_name=item_name,
			qty=qty,
			rate=rate,
			currency=currency
		)).insert()
	except Exception as e:
		error_log=app_error_log(frappe.session.user,str(e))






def diff_month(d1, d2):
	if d1.day>=d2.day-1:
		return (d1.year - d2.year) * 12 + d1.month - d2.month
	else:
		return (d1.year - d2.year) * 12 + d1.month - d2.month-1
		
	




def get_exchange_rate(from_currency, to_currency, transaction_date=None, args=None):
	if not (from_currency and to_currency):
		# manqala 19/09/2016: Should this be an empty return or should it throw and exception?
		print("No need to convert")
		return
	if from_currency == to_currency:
		return 1

	if not transaction_date:
		transaction_date = nowdate()
	currency_settings = frappe.get_doc("Accounts Settings").as_dict()
	print(transaction_date)
	allow_stale_rates = currency_settings.get("allow_stale")

	filters = [
		["date", "<=", get_datetime_str(transaction_date)],
		["from_currency", "=", from_currency],
		["to_currency", "=", to_currency]
	]

	if args == "for_buying":
		filters.append(["for_buying", "=", "1"])
	elif args == "for_selling":
		filters.append(["for_selling", "=", "1"])

	if not allow_stale_rates:
		stale_days = currency_settings.get("stale_days")
		checkpoint_date = add_days(transaction_date, -stale_days)
		filters.append(["date", ">", get_datetime_str(checkpoint_date)])

	# cksgb 19/09/2016: get last entry in Currency Exchange with from_currency and to_currency.
	entries = frappe.get_all(
		"Currency Exchange", fields=["exchange_rate"], filters=filters, order_by="date desc",
		limit=1)
	if entries:
		return flt(entries[0].exchange_rate)

	try:
		cache = frappe.cache()
		key = "currency_exchange_rate:{0}:{1}".format(from_currency, to_currency)
		value = cache.get(key)

		if not value:
			import requests
			print('Trying to get from Frankfurter')
			api_url = "https://frankfurter.erpnext.org/{0}".format(transaction_date)
			response = requests.get(api_url, params={
				"base": from_currency,
				"symbols": to_currency
			})
			# expire in 6 hours
			response.raise_for_status()
			value = response.json()["rates"][to_currency]
			print(value)
			cache.setex(key, value, 6 * 60 * 60)
		return flt(value)
	except:
		frappe.msgprint(_("Unable to find exchange rate for {0} to {1} for key date {2}. Please create a Currency Exchange record manually").format(from_currency, to_currency, transaction_date))
		return 0.0

