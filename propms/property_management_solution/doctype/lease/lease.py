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
				item_invoice_frequency = {
					"Monthly": 1,
					"Quarterly": 3,
					"6 Months": 6,
					"Annually": 12
				}
				for item in self.lease_item:
					frequency_factor = item_invoice_frequency.get(item.frequency, "Invalid frequency")
					if frequency_factor == "Invalid frequency":
						frappe.msgprint("Invalid frequency: " + item.frequency + " not found. Contact the developers!")
					else:
						frappe.msgprint("Frequency: " + item.frequency + " found. Factor selected: " + str(frequency_factor))
					end_date = self.end_date
					invoice_date = self.start_date
					#frappe.msgprint("first invoice_date: " + str(invoice_date), "Lease Invoice Schedule")
					while end_date >= invoice_date:
						new_end_date = add_days(add_months(invoice_date,frequency_factor),-1)
						frappe.msgprint("New End Date: " + str(new_end_date))
						frappe.msgprint("End Date: " + str(end_date))
						if new_end_date <= end_date and new_end_date >= "2019-01-01":
							frappe.msgprint("Making Invoice Schedule for " + str(new_end_date))	
							makeInvoiceSchedule(invoice_date, item.lease_item, item.paid_by, item.lease_item, self.name, frequency_factor, item.amount, item.currency_code, item.witholding_tax)
							frappe.msgprint("Self Name: " + self.name)
							invoice_date = add_months(new_end_date, frequency_factor)
							if not invoice_date < end_date:
								if not new_end_date == end_date:
									makeInvoiceSchedule(add_days(new_end_date, 1), item.lease_item, item.paid_by, item.lease_item, self.name, getDateMonthDiff(new_end_date, end_date, frequency_factor), item.amount, item.currency_code, item.witholding_tax)
									break
								else:
									break
						invoice_date = add_days(new_end_date, 1)
						frappe.msgprint("Start Date: " + str(invoice_date))

				lease_invoice = frappe.get_all("Lease Invoice Schedule", filters = {"parent":self.name, "invoice_number":None}, fields = ["name"])
				for row in lease_invoice:
					invoice_item = frappe.get_doc("Lease Invoice Schedule", row.name)
					item_dict = []
					if invoice_item.date_to_invoice <= getdate(today()) and invoice_item.date_to_invoice >= getdate("2019-01-01"):
						item_json = {}
						item_json["item_code"] = invoice_item.lease_item
						item_json["qty"] = invoice_item.qty
						item_json["rate"] = invoice_item.rate
						item_dict.append(item_json)
						res = makeInvoice(invoice_item.date_to_invoice, invoice_item.paid_by, json.dumps(item_dict), invoice_item.currency, self.name, row.name, invoice_item.tax)
						if res:
							frappe.db.set_value("Lease Invoice Schedule", invoice_item.name,"invoice_number", res.name)
					
		except Exception as e:
			frappe.msgprint("Exception error! Check app error log.")
			error_log=app_error_log(frappe.session.user,str(e))

