from __future__ import unicode_literals
import frappe
from frappe.utils import cint, get_gravatar, format_datetime, now_datetime,add_days,today,formatdate,date_diff,getdate,get_last_day
from frappe import throw, msgprint, _
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.utils.password import update_password as _update_password
from erpnext.controllers.accounts_controller import get_taxes_and_charges
from frappe.desk.notifications import clear_notifications
from frappe.utils.user import get_system_managers
import frappe.permissions
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




















	
