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


@frappe.whitelist()
def getAllLease():
	lease_list = frappe.get_all("Lease",filters={"end_date": (">=", "2019-01-01")},fields=["name"])
	frappe.msgprint("working on lease_list" + str(lease_list))
	for lease in lease_list:
		make_lease_invoice_schedule(lease.name)

#def on_update(self):
@frappe.whitelist()
def make_lease_invoice_schedule(leasedoc):
	#frappe.msgprint("This is the parameter passed: " + str(leasedoc))
	lease = frappe.get_doc("Lease", str(leasedoc)) 
	try:
		if len(lease.lease_item)>=1:
			item_invoice_frequency = {
				"Monthly": 1.00, # .00 to make it float type
				"Bi-Monthly": 2.00,
				"Quarterly": 3.00,
				"6 months": 6.00,
				"Annually": 12.00
			}
			for item in lease.lease_item:
				end_date = lease.end_date
				invoice_date = lease.start_date
				for lease_invoice_schedule in lease.lease_invoice_schedule:
					if lease_invoice_schedule.invoice_number is None:
						#frappe.msgprint("Deleting schedule :" + lease_invoice_schedule.name + " dated: " + str(lease_invoice_schedule.date_to_invoice))
						frappe.delete_doc("Lease Invoice Schedule", lease_invoice_schedule.name)
					else:
						invoice_date = add_months(lease_invoice_schedule.date_to_invoice, lease_invoice_schedule.qty)
						frappe.msgprint("Lease Invoice Schedule retained: " + lease_invoice_schedule.name + " for invoice number: " + str(lease_invoice_schedule.invoice_number))
				frequency_factor = item_invoice_frequency.get(item.frequency, "Invalid frequency")
				#frappe.msgprint("Next Invoice date calculated: " + str(invoice_date))
				if frequency_factor == "Invalid frequency":
					frappe.msgprint("Invalid frequency: " + str(item.frequency) + " for " + str(leasedoc) + " not found. Contact the developers!")
					break
				invoice_qty = float(frequency_factor)
				#frappe.msgprint("first invoice_date: " + str(invoice_date), "Lease Invoice Schedule")
				while end_date >= invoice_date:
					invoice_period_end = add_days(add_months(invoice_date, frequency_factor), -1)
					#frappe.msgprint("Invoice period end: " + str(invoice_period_end) + "--- Invoice Date: " + str(invoice_date))
					#frappe.msgprint("End Date: " + str(end_date))
					# set invoice_Qty as appropriate fraction of frequency_factor
					if invoice_period_end > end_date:
						invoice_qty = getDateMonthDiff(invoice_date, end_date, 1)
						#frappe.msgprint("Invoice quantity corrected as " + str(invoice_qty))
					#frappe.msgprint("Making Invoice Schedule for " + str(invoice_date) + ", Quantity calculated: " + str(invoice_qty))
					makeInvoiceSchedule(invoice_date, item.lease_item, item.paid_by, item.lease_item, lease.name, invoice_qty, item.amount, item.currency_code, item.witholding_tax)
					invoice_date = add_days(invoice_period_end, 1)
		frappe.msgprint("Completed making of invoice schedule.")

	except Exception as e:
		frappe.msgprint("Exception error! Check app error log.")
		error_log=app_error_log(frappe.session.user,str(e))
