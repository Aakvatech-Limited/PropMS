from __future__ import unicode_literals
import frappe
from frappe.utils import cint, get_gravatar, format_datetime, now_datetime,add_days,today,formatdate,date_diff,getdate,add_months
from frappe import throw, msgprint, _
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.utils.password import update_password as _update_password
from erpnext.controllers.accounts_controller import get_taxes_and_charges
from frappe.desk.notifications import clear_notifications
from frappe.utils.user import get_system_managers
import frappe.permissions
from frappe.model.mapper import get_mapped_doc
import frappe.share
import re
import string
import random
import json
import time
from datetime import datetime
from datetime import date
from datetime import timedelta
import collections
import math
import logging
from frappe.client import delete
import traceback
import urllib
import urllib2
from erpnext.accounts.utils import get_fiscal_year
from collections import defaultdict


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


