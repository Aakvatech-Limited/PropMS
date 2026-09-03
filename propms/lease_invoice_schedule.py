import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.utils import add_days, add_months, get_first_day, get_last_day, getdate, today

from propms.auto_custom import app_error_log, makeInvoiceSchedule


def get_aligned_invoice_date(date):
	"""Returns the first day of the month for the given date"""
	return get_first_day(date)


@frappe.whitelist()
def make_lease_invoice_schedule():
	# First check if make_invoice_schedule_up_to_tomorrow_only is enabled
	settings = frappe.get_single("Property Management Settings")
	make_schedule_up_to_tomorrow = settings.get("make_invoice_schedule_up_to_tomorrow_only", 0)
	if not make_schedule_up_to_tomorrow:
		return

	# Proceed with other computations only if the setting is enabled
	use_valid_from_date = settings.use_valid_from_date
	today_date = getdate(today())
	next_month_end = get_last_day(add_months(today_date, 1))  # End of next month
	invoice_start_date = getdate(settings.get("invoice_start_date", None))

	if not invoice_start_date:
		frappe.throw(_("Please set Invoice Start Date in Property Management Settings"))

	Lease = DocType("Lease")
	query = (
		frappe.qb.from_(Lease)
		.select(Lease.name)
		.where(
			(Lease.start_date <= today_date)  # Only check start_date, ignore end_date for inclusion
			& (Lease.lease_status == "Active")  # Filter for active leases
			# Only check start_date, ignore end_date for inclusion
		)
	)
	lease_names = [row[0] for row in frappe.db.sql(query.get_sql())]

	for lease_name in lease_names:
		try:
			lease = frappe.get_doc("Lease", lease_name)
			lease_start = getdate(lease.start_date)
			schedule_end = getdate(lease.end_date) if lease.end_date else next_month_end

			# Use the later date between lease_start and invoice_start_date
			schedule_start = max(lease_start, invoice_start_date) if lease_start else invoice_start_date
			if not schedule_start:
				continue  # skip if no start_date

			# Clean up schedule entries for removed lease items
			lease_item_names = [li.lease_item for li in lease.lease_item]
			schedule_items = frappe.get_all(
				"Lease Invoice Schedule", filters={"parent": lease.name}, fields=["name", "lease_item"]
			)
			for s in schedule_items:
				if s.lease_item not in lease_item_names:
					frappe.delete_doc("Lease Invoice Schedule", s.name)

			# Frequency map
			freq_map = {
				"Monthly": 1.0,
				"Bi-Monthly": 2.0,
				"Quarterly": 3.0,
				"6 months": 6.0,
				"Annually": 12.0,
			}

			idx = 1
			for item in lease.lease_item:
				if not item.frequency:
					continue

				freq = freq_map.get(item.frequency)
				if not freq:
					frappe.log_error(
						f"Invalid frequency '{item.frequency}' for item {item.lease_item} in lease {lease.name}",
						"Invalid Frequency",
					)
					continue

				invoice_qty = float(freq)

				# Default to base amount
				item_amount = item.amount

				# Get the latest active lease item that has valid_from date
				lease_items = frappe.get_all(
					"Lease Item",
					filters={
						"parent": lease.name,
						"lease_item": item.lease_item,
						"valid_from": ("<=", today_date),
					},
					fields=["amount", "valid_from"],
					order_by="valid_from desc",
					limit=1,
				)

				# Use amount from the most recent active lease item if found
				if use_valid_from_date and lease_items:
					item_amount = lease_items[0].amount

				# Get the first day of the month in which schedule_start falls
				invoice_date = get_first_day(schedule_start)

				# Generate invoice schedules up to next month
				while schedule_end >= invoice_date and invoice_date <= next_month_end:
					# Calculate period end as last day of the month after freq months
					invoice_period_end = get_last_day(add_months(invoice_date, freq - 1))

					# Only create schedule if date_to_invoice is between invoice start date and today + next month
					if schedule_start <= invoice_date <= next_month_end:
						exists = frappe.db.exists(
							"Lease Invoice Schedule",
							{
								"parent": lease.name,
								"lease_item": item.lease_item,
								"date_to_invoice": invoice_date,
							},
						)

						if not exists:
							makeInvoiceSchedule(
								invoice_date,
								item.lease_item,
								item.paid_by,
								item.lease_item,
								lease.name,
								invoice_qty,
								item_amount,
								idx,
								item.currency_code,
								item.witholding_tax,
								lease.days_to_invoice_in_advance,
								item.invoice_item_group,
								item.document_type,
							)
							frappe.db.commit()
							idx += 1

					# Move to first day of next period
					invoice_date = add_days(invoice_period_end, 1)

			frappe.msgprint(_(f"Completed invoice schedule for Lease: {lease.name}"))

		except Exception as e:
			frappe.msgprint(_(f"Error in {lease_name}. Check app error log."))
			app_error_log(frappe.session.user, f"{lease_name}: {str(e)}")
