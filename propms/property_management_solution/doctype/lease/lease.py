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
from propms.auto_custom import app_error_log,makeInvoiceSchedule,getMonthNo,getDateMonthDiff
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


	def validate(self):
	#def after_insert(self):
		try:
			if len(self.lease_item)>=1:
				item_arr=[]
				for item in self.lease_item:
					if item.frequency=="Quarterly":
						end_date=self.end_date
						start_date=self.start_date
						while end_date>=start_date:
							new_end_date=add_days(add_months(start_date,3),-1)
							#frappe.msgprint("new_end_date"+str(new_end_date))
							if new_end_date<=end_date and start_date >= "2019-01-01":
								makeInvoiceSchedule(start_date,item.lease_item,item.paid_by,item.lease_item,self.name,3,item.amount,item.currency_code,item.witholding_tax)
								start_date=add_months(new_end_date,3)
								#frappe.msgprint("start_date"+str(start_date))	
								if not start_date<end_date:
									
									if not new_end_date==end_date:
										makeInvoiceSchedule(add_days(new_end_date,1),item.lease_item,item.paid_by,item.lease_item,self.name,getDateMonthDiff(new_end_date,end_date,3),item.amount,item.currency_code,item.witholding_tax)
										break
									else:
										break
								else:
									start_date=add_days(new_end_date,1)
							else:
								break

					if item.frequency=="Monthly":
						end_date=self.end_date
						start_date=self.start_date
						while end_date>=start_date:
							new_end_date=add_days(add_months(start_date,1),-1)
							#frappe.msgprint("new_end_date"+str(new_end_date))
							#if new_end_date<=end_date:
							if new_end_date<=end_date and start_date >= "2019-01-01":
								makeInvoiceSchedule(start_date,item.lease_item,item.paid_by,item.lease_item,self.name,1,item.amount,item.currency_code,item.witholding_tax)
								start_date=add_months(new_end_date,1)
								#frappe.msgprint("start_date"+str(start_date))	
								if not start_date<end_date:
									if not new_end_date==end_date:
										makeInvoiceSchedule(add_days(new_end_date,1),item.lease_item,item.paid_by,item.lease_item,self.name,getDateMonthDiff(new_end_date,end_date,1),item.amount,item.currency_code,item.witholding_tax)
										break
									else:
										break
								else:
									start_date=add_days(new_end_date,1)
							else:
								break


					if item.frequency=="6 months":
						end_date=self.end_date
						start_date=self.start_date
						while end_date>=start_date:
							new_end_date=add_days(add_months(start_date,6),-1)
							frappe.msgprint("new_end_date: "+str(new_end_date))
							if new_end_date<=end_date and start_date >= "2019-01-01":
							#if new_end_date<=end_date:
								makeInvoiceSchedule(start_date,item.lease_item,item.paid_by,item.lease_item,self.name,6,item.amount,item.currency_code,item.witholding_tax)
								start_date=add_months(new_end_date,6)
								frappe.msgprint("start_date: "+str(start_date))	
								frappe.msgprint("end_date: "+str(end_date))	
								if not start_date<end_date:
									if not new_end_date==end_date:
										makeInvoiceSchedule(add_days(new_end_date,1),item.lease_item,item.paid_by,item.lease_item,self.name,getDateMonthDiff(new_end_date,end_date,6),item.amount,item.currency_code,item.witholding_tax)
										break
									else:
										break
								else:
									start_date=add_days(new_end_date,1)
							else:
								break

					if item.frequency=="Annually":
						end_date=self.end_date
						start_date=self.start_date
						while end_date>=start_date:
							new_end_date=add_days(add_months(start_date,12),-1)
							#frappe.msgprint("new_end_date"+str(new_end_date))
							if new_end_date<=end_date and start_date >= "2019-01-01":
							#if new_end_date<=end_date:
								makeInvoiceSchedule(start_date,item.lease_item,item.paid_by,item.lease_item,self.name,12,item.amount,item.currency_code,item.witholding_tax)
								start_date=add_months(new_end_date,12)
								#frappe.msgprint("start_date"+str(start_date))	
								if not start_date<end_date:
									if not new_end_date==end_date:
										makeInvoiceSchedule(add_days(new_end_date,1),item.lease_item,item.paid_by,item.lease_item,self.name,getDateMonthDiff(new_end_date,end_date,12),item.amount,item.currency_code,item.witholding_tax)
										break
									else:
										break
								else:
									start_date=add_days(new_end_date,1)
							else:
								break

	
				lease_invoice=frappe.get_all("Lease Invoice Schedule",filters={"parent":self.name},fields=["name"])
				for row in lease_invoice:
					invoice_item=frappe.get_doc("Lease Invoice Schedule",row.name)
					item_dict=[]
					if invoice_item.date_to_invoice<=getdate(today()) and invoice_item.date_to_invoice >="2019-01-01":
					#if invoice_item.date_to_invoice<=getdate(today()):
						item_json={}
						item_json["item_code"]=invoice_item.lease_item
						item_json["qty"]=invoice_item.qty
						item_json["rate"]=invoice_item.rate
						item_dict.append(item_json)
						res=makeInvoice(invoice_item.date_to_invoice,invoice_item.paid_by,json.dumps(item_dict),invoice_item.currency,self.name,row.name,invoice_item.tax)
						if res:
							frappe.db.set_value("Lease Invoice Schedule",invoice_item.name,"invoice_number",res.name)
					
		except Exception as e:
			frappe.msgprint("Exception error! Check app error log.")
			error_log=app_error_log(frappe.session.user,str(e))

