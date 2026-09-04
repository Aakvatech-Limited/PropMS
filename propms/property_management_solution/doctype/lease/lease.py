# Copyright (c) 2018, Aakvatech and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, add_months, cint, get_datetime, getdate, now, nowdate, today

from propms.auto_custom import app_error_log, getDateMonthDiff, makeInvoiceSchedule


class Lease(Document):
	def get_all_properties(self):
		properties = set()
		if self.property:
			properties.add(self.property)
		for item in self.lease_item:
			if item.property_unit:
				properties.add(item.property_unit)
		return list(properties)

	def on_submit(self):
		try:
			properties = self.get_all_properties()
			for prop in properties:
				checklist_doc = frappe.get_doc("Checklist Checkup Area", "Handover")
				if checklist_doc:
					check_list = []
					for task in checklist_doc.task:
						check = {}
						check["checklist_task"] = task.task_name
						check_list.append(check)

					frappe.get_doc(
						dict(
							doctype="Daily Checklist",
							area="Handover",
							checkup_date=self.start_date,
							daily_checklist_detail=check_list,
							property=prop,
						)
					).insert()
		except Exception as e:
			app_error_log(frappe.session.user, str(e))

	def validate(self):
		self.set_lease_status()
		self.validate_days_to_invoice_in_advance()
		try:
			properties = self.get_all_properties()
			# Lease Status Validation: Prevent multiple active leases per property
			if self.lease_status == "Active":
				for prop in properties:
					max_allowed = (
						cint(frappe.db.get_value("Property", prop, "max_active_leases"))
						or cint(
							frappe.db.get_single_value("Property Management Settings", "max_active_leases")
						)
						or 1
					)
					# Query for other non-draft leases for the same property
					conflicting_leases = frappe.db.get_all(
						"Lease",
						filters={
							"property": prop,
							"lease_status": ["!=", "Draft"],
							"name": ["!=", self.name],
							"docstatus": ["<", 2],  # Exclude cancelled
						},
						fields=["name", "end_date", "lease_status"],
					)
					active_conflicts = [
						l
						for l in conflicting_leases
						if not l["end_date"] or getdate(l["end_date"]) >= getdate(self.start_date)
					]
					if len(active_conflicts) >= max_allowed:
						msg = _(
							"Cannot activate lease <b>{0}</b> for property <b>{1}</b>.<br><br>"
							"• <b>Max Allowed Active Leases:</b> {2}<br>"
							"• <b>Currently Active Leases:</b> {3}<br><br>"
							"<i>Please contact Administrator if you need to increase the limit for this property.</i>"
						).format(self.name, prop, max_allowed, len(active_conflicts))
						frappe.throw(msg, title=_("Active Lease Limit Exceeded"))

			for prop in properties:
				if self.skip_end_date is None:
					if (
						get_datetime(add_months(self.end_date, -3))
						<= get_datetime(now())
						<= get_datetime(add_months(self.end_date, 3))
					):
						frappe.db.set_value("Property", prop, "status", "Off Lease in 3 Months")
						frappe.msgprint(
							_(
								'Property "{0}" has now been set <b>Off Lease in 3 Months</b> for Lease "{1}"'
							).format(prop, self.name)
						)
					elif self.lease_status != "Draft" and (
						get_datetime(self.start_date)
						<= get_datetime(now())
						<= get_datetime(add_months(self.end_date, -3))
					):
						frappe.db.set_value("Property", prop, "status", "On Lease")
						frappe.msgprint(
							_(
								'Property "{0}" has now been set <b>On Lease from Active</b> for Lease "{1}"'
							).format(prop, self.name)
						)
				else:
					if self.lease_status != "Draft":
						frappe.db.set_value("Property", prop, "status", "On Lease")
						frappe.msgprint(
							_(
								'Property "{0}" has now been set <b>On Lease from Active</b> for Lease "{1}"'
							).format(prop, self.name)
						)
		except frappe.ValidationError:
			raise
		except Exception as e:
			app_error_log(frappe.session.user, str(e))

	def validate_days_to_invoice_in_advance(self):
		"""Prevent changing 'Days to Invoice in Advance' once invoices have been generated."""
		if not self.is_new() and self.has_value_changed("days_to_invoice_in_advance"):
			has_generated_invoices = any(
				row.invoice_number or row.sales_order_number for row in (self.lease_invoice_schedule or [])
			)
			if not has_generated_invoices:
				has_generated_invoices = frappe.db.exists(
					"Lease Invoice Schedule",
					{
						"parent": self.name,
						"invoice_number": ["is", "set"],
					},
				)
			if has_generated_invoices:
				frappe.throw(
					_(
						"Cannot change 'Days to Invoice in Advance' after invoices have been generated for this Lease."
					),
					title=_("Field Read Only"),
				)

	def validate_days_to_invoice_in_advance(self):
		"""Prevent changing 'Days to Invoice in Advance' once invoices have been generated."""
		if not self.is_new() and self.has_value_changed("days_to_invoice_in_advance"):
			has_generated_invoices = any(
				row.invoice_number or row.sales_order_number for row in (self.lease_invoice_schedule or [])
			)
			if not has_generated_invoices:
				has_generated_invoices = frappe.db.exists(
					"Lease Invoice Schedule",
					{
						"parent": self.name,
						"invoice_number": ["is", "set"],
					},
				)
			if has_generated_invoices:
				frappe.throw(
					_(
						"Cannot change 'Days to Invoice in Advance' after invoices have been generated for this Lease."
					),
					title=_("Field Read Only"),
				)

	def set_lease_status(self):
		"""
		Set lease status on save.

		Only system-controlled statuses are automatically changed:
		Upcoming, Active, Expired.

		All other statuses are considered manual and are not overwritten.
		"""

		if self.lease_status and self.lease_status not in get_system_controlled_statuses():
			return

		status = get_status_for_lease(self)

		if status:
			self.lease_status = status


def get_system_controlled_statuses():
	"""
	Statuses controlled by system automation.

	Any lease_status outside this set is treated as manually controlled
	and will not be overwritten by validate() or the daily scheduler.
	"""

	return {"Upcoming", "Active", "Expired"}


def update_lease_statuses():
	"""
	Daily scheduler method.

	Updates only system-controlled Lease statuses:
	Upcoming, Active, Expired.

	Uses frappe.db.set_value() to avoid full document save hooks,
	and adds a timeline comment for audit visibility.
	"""

	today_date = getdate(nowdate())
	system_controlled_statuses = list(get_system_controlled_statuses())

	leases = frappe.get_all(
		"Lease",
		fields=[
			"name",
			"lease_status",
			"start_date",
			"end_date",
			"skip_end_date",
		],
		filters=[
			["lease_status", "in", system_controlled_statuses],
			["docstatus", "<", 2],
		],
	)

	for lease in leases:
		old_status = lease.lease_status
		new_status = get_status_for_lease(lease, today_date)

		if not new_status or new_status == old_status:
			continue

		frappe.db.set_value(
			"Lease",
			lease.name,
			"lease_status",
			new_status,
			update_modified=True,
		)

		doc = frappe.get_doc("Lease", lease.name)
		doc.add_comment(
			"Info",
			_("Lease Status automatically changed from {0} to {1} by daily scheduler.").format(
				old_status or "blank", new_status
			),
		)

	# Scheduler entry point, not a document hook: the batch has to be durable.
	frappe.db.commit()  # nosemgrep


def get_status_for_lease(lease, today_date=None):
	"""
	Return calculated Lease Status.

	Rules:
	- Future start_date => Upcoming
	- start_date <= today and end_date >= today => Active
	- end_date < today => Expired
	- If skip_end_date is checked, do not mark as Expired
	- end_date equal to today remains Active until the next day
	"""

	today_date = today_date or getdate(nowdate())

	start_date = getdate(lease.start_date) if lease.start_date else None
	end_date = getdate(lease.end_date) if lease.end_date else None
	skip_end_date = bool(lease.skip_end_date)

	if start_date and start_date > today_date:
		return "Upcoming"

	if not skip_end_date and end_date and end_date < today_date:
		return "Expired"

	if start_date and start_date <= today_date:
		if skip_end_date or not end_date or end_date >= today_date:
			return "Active"

	return None


@frappe.whitelist()
def getAllLease():
	# Below is temporarily created to manually run through all lease and refresh lease invoice schedule. Hardcoded to start from 1st Jan 2020.
	frappe.msgprint(
		_("The task of making lease invoice schedule for all users has been sent for background processing.")
	)
	invoice_start_date = frappe.db.get_single_value("Property Management Settings", "invoice_start_date")
	lease_list = frappe.get_all("Lease", filters={"end_date": (">=", invoice_start_date)}, fields=["name"])
	# frappe.msgprint("Working on lease_list" + str(lease_list))
	lease_list_len = len(lease_list)
	frappe.msgprint(_("Total number of lease to be processed is {0}").format(lease_list_len))
	for lease in lease_list:
		make_lease_invoice_schedule(lease.name)


# def on_update(self):
@frappe.whitelist()
def make_lease_invoice_schedule(leasedoc):
	# frappe.msgprint("This is the parameter passed: " + str(leasedoc))
	lease = frappe.get_doc("Lease", str(leasedoc))
	try:
		# Delete unnecessary records after lease end date
		lease_invoice_schedule_list = frappe.get_list(
			"Lease Invoice Schedule",
			fields=[
				"name",
				"parent",
				"lease_item",
				"invoice_number",
				"date_to_invoice",
			],
			filters={"parent": lease.name, "date_to_invoice": (">", lease.end_date)},
			parent_doctype="Lease",
		)
		for lease_invoice_schedule in lease_invoice_schedule_list:
			frappe.delete_doc("Lease Invoice Schedule", lease_invoice_schedule.name)
		# Only process lease that items and is current
		if len(lease.lease_item) >= 1 and lease.end_date >= getdate(today()):
			# Clean up records that are no longer required, i.e. of unnecessary lease items and unnecessary dates
			# Records before Invoice Start Date
			invoice_start_date = frappe.db.get_single_value(
				"Property Management Settings", "invoice_start_date"
			)
			lease_invoice_schedule_list = frappe.get_list(
				"Lease Invoice Schedule",
				fields=["name", "parent", "invoice_number", "date_to_invoice"],
				filters={
					"parent": lease.name,
					"date_to_invoice": ("<", invoice_start_date),
				},
				parent_doctype="Lease",
			)
			# frappe.msgprint("Records before Invoice Start Date " + str(lease_invoice_schedule_list))
			for lease_invoice_schedule in lease_invoice_schedule_list:
				# frappe.msgprint("Deleting Record before Invoice Start Date " + str(invoice_start_date) + str(lease_invoice_schedule.name))
				frappe.delete_doc("Lease Invoice Schedule", lease_invoice_schedule.name)
			# Records of lease_items that no longer existing in lease.lease_item
			lease_invoice_schedule_list = frappe.get_list(
				"Lease Invoice Schedule",
				fields=[
					"name",
					"parent",
					"lease_item",
					"invoice_number",
					"date_to_invoice",
				],
				filters={"parent": lease.name},
				parent_doctype="Lease",
			)
			lease_items_list = frappe.get_list(
				"Lease Item",
				fields=["name", "parent", "lease_item"],
				filters={"parent": lease.name},
				parent_doctype="Lease",
			)
			# Create list of lease items that are part of lease.lease_item
			lease_item_name_list = [lease_item["lease_item"] for lease_item in lease_items_list]
			# frappe.msgprint(str(lease_item_list))
			for lease_invoice_schedule in lease_invoice_schedule_list:
				if lease_invoice_schedule.lease_item not in lease_item_name_list:
					# frappe.msgprint("This lease item will be removed from invoice schedule " + str(lease_invoice_schedule.lease_item))
					frappe.delete_doc("Lease Invoice Schedule", lease_invoice_schedule.name)
			item_invoice_frequency = {
				"Monthly": 1.00,  # .00 to make it float type
				"Bi-Monthly": 2.00,
				"Quarterly": 3.00,
				"6 months": 6.00,
				"Annually": 12.00,
			}
			idx = 1
			for item in lease.lease_item:
				# frappe.msgprint("Lease item being processed: " + str(item.lease_item))
				lease_invoice_schedule_list = frappe.get_all(
					"Lease Invoice Schedule",
					fields=[
						"name",
						"parent",
						"lease_item",
						"schedule_start_date",
						"qty",
						"invoice_number",
						"date_to_invoice",
					],
					filters={"parent": lease.name, "lease_item": item.lease_item},
					order_by="date_to_invoice",
				)
				# frappe.msgprint(str(lease_invoice_schedule_list))
				# Get the latest item frequency incase lease was changed.
				frequency_factor = item_invoice_frequency.get(item.frequency, "Invalid frequency")
				# frappe.msgprint("Next Invoice date calculated: " + str(invoice_date))
				if frequency_factor == "Invalid frequency":
					message = (
						"Invalid frequency: "
						+ str(item.frequency)
						+ " for "
						+ str(leasedoc)
						+ " not found. Contact the developers!"
					)
					frappe.log_error("Frequency incorrect", message)
					break
				invoice_qty = float(frequency_factor)
				end_date = lease.end_date
				invoice_date = lease.start_date
				# Find out the first invoice date on or after Invoice Start Date process.
				while end_date >= invoice_date and invoice_date < invoice_start_date:
					invoice_period_end = add_days(add_months(invoice_date, frequency_factor), -1)
					# Set invoice_Qty as appropriate fraction of frequency_factor
					if invoice_period_end > end_date:
						invoice_qty = getDateMonthDiff(invoice_date, end_date, 1)
						# frappe.msgprint("Invoice quantity corrected as " + str(invoice_qty))
					invoice_date = add_days(invoice_period_end, 1)
				# If there is no lease_invoice_schedule_list found, i.e. it is fresh new list to be created
				if not lease_invoice_schedule_list:
					while end_date >= invoice_date:
						invoice_period_end = add_days(add_months(invoice_date, frequency_factor), -1)
						# frappe.msgprint("Invoice period end: " + str(invoice_period_end) + "--- Invoice Date: " + str(invoice_date))
						# frappe.msgprint("End Date: " + str(end_date))
						# set invoice_Qty as appropriate fraction of frequency_factor
						if invoice_period_end > end_date:
							invoice_qty = getDateMonthDiff(invoice_date, end_date, 1)
							# frappe.msgprint("Invoice quantity corrected as " + str(invoice_qty))
						# frappe.msgprint("Making Fresh Invoice Schedule for " + str(invoice_date)
						# 	+ ", Quantity calculated: " + str(invoice_qty))
						makeInvoiceSchedule(
							invoice_date,
							item.lease_item,
							item.paid_by,
							item.lease_item,
							lease.name,
							invoice_qty,
							item.amount,
							idx,
							item.currency_code,
							item.witholding_tax,
							lease.days_to_invoice_in_advance,
							item.invoice_item_group,
							item.document_type,
						)
						idx += 1
						invoice_date = add_days(invoice_period_end, 1)
				for lease_invoice_schedule in lease_invoice_schedule_list:
					# frappe.msgprint("Upon entering lease_invoice_schedule_list - Date to invoice: " + str(lease_invoice_schedule.date_to_invoice)
					# 	+ " and invoice date to process is " + str(invoice_date))
					if not (lease_invoice_schedule.schedule_start_date):
						lease_invoice_schedule.schedule_start_date = lease_invoice_schedule.date_to_invoice
					while (
						end_date >= invoice_date and lease_invoice_schedule.schedule_start_date > invoice_date
					):
						invoice_period_end = add_days(add_months(invoice_date, frequency_factor), -1)
						# frappe.msgprint("Upon entering Invoice period end: " + str(invoice_period_end) + "--- Invoice Date: " + str(invoice_date))
						# frappe.msgprint("End Date: " + str(end_date))
						# set invoice_Qty as appropriate fraction of frequency_factor
						if invoice_period_end > end_date:
							invoice_qty = getDateMonthDiff(invoice_date, end_date, 1)
							# frappe.msgprint("Invoice quantity corrected as " + str(invoice_qty))
						# frappe.msgprint("Making Pre Invoice Schedule for " + str(invoice_date) + ", Quantity calculated: " + str(invoice_qty))
						makeInvoiceSchedule(
							invoice_date,
							item.lease_item,
							item.paid_by,
							item.lease_item,
							lease.name,
							invoice_qty,
							item.amount,
							idx,
							item.currency_code,
							item.witholding_tax,
							lease.days_to_invoice_in_advance,
							item.invoice_item_group,
							item.document_type,
						)
						idx += 1
						invoice_date = add_days(invoice_period_end, 1)
					# frappe.msgprint(str(lease_invoice_schedule))
					# If the record already exists and invoice is generated
					if (
						lease_invoice_schedule.invoice_number is not None
						and lease_invoice_schedule.invoice_number != ""
					):
						# frappe.msgprint("Lease Invoice Schedule retained: " + lease_invoice_schedule.name
						# 	+ " for invoice number: " + str(lease_invoice_schedule.invoice_number)
						# 	+ " dated " + str(lease_invoice_schedule.date_to_invoice)
						# )
						# Set months as rounded up by 1 if the month is a fraction (last invoice for the lease item already created).
						# Above needed to escape from infinite loop of rounded down date and therefore never reaching end of the lease.
						if lease_invoice_schedule.qty != round(lease_invoice_schedule.qty, 0):
							add_months_value = round(lease_invoice_schedule.qty, 0) + 1
						else:
							add_months_value = lease_invoice_schedule.qty
						# frappe.msgprint("Add Months Value" + str(add_months_value) + " due to qty = " + str(lease_invoice_schedule.qty))
						invoice_date = add_months(
							lease_invoice_schedule.schedule_start_date, add_months_value
						)
						# Set sequence to show it on the top
						frappe.db.set_value(
							"Lease Invoice Schedule",
							lease_invoice_schedule.name,
							"idx",
							idx,
						)
						idx += 1
					# If the invoice is not created
					else:
						# frappe.msgprint("Deleting schedule :" + lease_invoice_schedule.name + " dated: " + str(lease_invoice_schedule.date_to_invoice) + " for " + str(lease_invoice_schedule.lease_item))
						frappe.delete_doc("Lease Invoice Schedule", lease_invoice_schedule.name)
				# frappe.msgprint("first invoice_date: " + str(invoice_date), "Lease Invoice Schedule")
				while end_date >= invoice_date:
					invoice_period_end = add_days(add_months(invoice_date, frequency_factor), -1)
					# frappe.msgprint("Invoice period end: " + str(invoice_period_end) + "--- Invoice Date: " + str(invoice_date))
					# frappe.msgprint("End Date: " + str(end_date))
					# set invoice_Qty as appropriate fraction of frequency_factor
					if invoice_period_end > end_date:
						invoice_qty = getDateMonthDiff(invoice_date, end_date, 1)
						# frappe.msgprint("Invoice quantity corrected as " + str(invoice_qty))
					# frappe.msgprint("Making Post Invoice Schedule for " + str(invoice_date) + ", Quantity calculated: " + str(invoice_qty))
					makeInvoiceSchedule(
						invoice_date,
						item.lease_item,
						item.paid_by,
						item.lease_item,
						lease.name,
						invoice_qty,
						item.amount,
						idx,
						item.currency_code,
						item.witholding_tax,
						lease.days_to_invoice_in_advance,
						item.invoice_item_group,
						item.document_type,
					)
					idx += 1
					invoice_date = add_days(invoice_period_end, 1)

		frappe.msgprint(_("Completed making of invoice schedule."))

	except Exception as e:
		frappe.msgprint(_("Exception error! Check app error log."))
		app_error_log(frappe.session.user, str(e))


@frappe.whitelist()
def initiate_lease_renewal(source_lease_name):
	# 1. Permission checks
	if not any(r in frappe.get_roles() for r in ["Property Manager", "System Manager"]):
		frappe.throw(
			_(
				"You are not authorized to renew leases. Only Property Managers and System Managers can perform this action."
			),
			frappe.PermissionError,
		)

	# 2. Fetch source document
	source_doc = frappe.get_doc("Lease", source_lease_name)

	# 3. Status checks
	if source_doc.lease_status not in ["Active", "Expired"]:
		frappe.throw(
			_("Lease {0} is not eligible for renewal. Status must be Active or Expired.").format(
				source_lease_name
			),
			frappe.ValidationError,
		)

	# 4. Duplicate renewal check (ignoring terminated or aborted renewals)
	duplicate_exists = frappe.db.exists(
		"Lease",
		{"renewed_from": source_lease_name, "lease_status": ["not in", ["Not Materialized", "Terminated"]]},
	)
	if duplicate_exists:
		frappe.throw(
			_("A renewal lease already exists for this lease: {0}").format(duplicate_exists),
			frappe.ValidationError,
		)

	# 5. Clone Lease using standard frappe.copy_doc
	new_lease = frappe.copy_doc(source_doc)
	new_lease.set("lease_invoice_schedule", [])  # Clear old invoice schedules

	# Set renewal reference fields
	new_lease.renewed_from = source_lease_name
	new_lease.lease_status = "Renewal to Previous Lease"
	new_lease.renewal_initiated_by = frappe.session.user

	# Calculate dates
	if source_doc.end_date:
		new_lease.start_date = add_days(source_doc.end_date, 1)
		if source_doc.start_date:
			duration_days = (getdate(source_doc.end_date) - getdate(source_doc.start_date)).days
			new_lease.end_date = add_days(new_lease.start_date, duration_days)
	else:
		new_lease.start_date = today()

	# Update valid_from date for items
	for item in new_lease.lease_item:
		item.valid_from = new_lease.start_date

	# Insert and save the new Lease as draft
	new_lease.insert(ignore_permissions=True)

	# Post a message/comment to the old lease with initiator and link details
	comment_text = _(
		"Lease renewal draft <a href='/desk/lease/{0}'><b>{0}</b></a> has been initiated by <b>{1}</b> on <b>{2}</b>."
	).format(new_lease.name, frappe.session.user, frappe.utils.formatdate(today()))
	source_doc.add_comment(text=comment_text)

	return new_lease.name
