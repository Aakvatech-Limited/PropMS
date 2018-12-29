# -*- coding: utf-8 -*-
# Copyright (c) 2018, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, get_gravatar, format_datetime, now_datetime,add_days,today,formatdate,date_diff,getdate,get_last_day
from frappe import throw, msgprint, _
from datetime import datetime
from datetime import date
from datetime import timedelta
import collections
from propms.auto_custom import app_error_log


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
