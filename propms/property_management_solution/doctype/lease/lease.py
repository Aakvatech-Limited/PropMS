# -*- coding: utf-8 -*-
# Copyright (c) 2018, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, format_datetime, now_datetime,add_days,today,formatdate,date_diff,getdate,get_last_day,add_months
from frappe import throw, msgprint, _
from datetime import datetime
from datetime import date
from datetime import timedelta

import calendar
import collections
import json
from propms.auto_custom import app_error_log,makeInvoiceSchedule,getMonthNo
from propms.lease_invoice import makeInvoice


class Lease(Document):
	def on_submit(self):
		try:
			checklist_doc=frappe.get_doc("Checklist Checkup Area","Handover")
			if checklist_doc:
				check_list=[]
				for task in checklist_doc.task:
					check={}
					check["checklist_task"]=task.task_name
					check_list.append(check)

				daily_checklist_doc=frappe.get_doc(dict(
					doctype="Daily Checklist",
					area="Handover",
					checkup_date=self.start_date,
					daily_checklist_detail=check_list,
					property=self.property
				)).insert()
		except Exception as e:
			error_log=app_error_log(frappe.session.user,str(e))


	def after_insert(self):
		try:
			if len(self.lease_item)>=1:
				item_arr=[]
				for item in self.lease_item:
					if item.frequency=="Quarterly":
						end_date=self.end_date
						start_date=self.start_date
						while end_date>=start_date:
							new_end_date=add_months(start_date,3)
							frappe.msgprint("new_end_date"+str(new_end_date))
							if new_end_date<=end_date:
								makeInvoiceSchedule(start_date,item.lease_item,item.paid_by,item.lease_item,self.name,3,item.amount)
								start_date=add_days(add_months(new_end_date,3),-1)
								frappe.msgprint("start_date"+str(start_date))	
								if not start_date<=end_date:
									frappe.msgprint(str(getMonthNo(new_end_date,end_date)))
									makeInvoiceSchedule(new_end_date,item.lease_item,item.paid_by,item.lease_item,self.name,getMonthNo(end_date,new_end_date),item.amount)
									break
								else:
									start_date=new_end_date
									
									
						item_json={}
						item_json["item_code"]=item.lease_item
						item_json["qty"]=3
						item_json["rate"]=item.amount
						item_arr.append(item_json)
						makeInvoice(self.start_date,item.paid_by,json.dumps(item_arr),item.currency_code)
						del item_arr[:]
					if item.frequency=="Monthly":
						item_json={}
						item_json["item_code"]=item.lease_item
						item_json["qty"]=1
						item_json["rate"]=item.amount
						item_arr.append(item_json)
						makeInvoice(self.start_date,item.paid_by,json.dumps(item_arr),item.currency_code)
						del item_arr[:]
					
		except Exception as e:
			frappe.msgprint("Test")
			error_log=app_error_log(frappe.session.user,str(e))

