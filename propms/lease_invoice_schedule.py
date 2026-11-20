import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.utils import add_days, add_months, get_first_day, get_last_day, getdate, today

from propms.auto_custom import app_error_log, makeInvoiceSchedule
from propms.lease_status_utils import get_active_lease_statuses


def get_aligned_invoice_date(date):
	"""Returns the first day of the month for the given date"""
	return get_first_day(date)


@frappe.whitelist(methods=["POST"])
def make_lease_invoice_schedule():
	# First check if make_invoice_schedule_up_to_tomorrow_only is enabled
	settings = frappe.get_single("Property Management Settings")
	make_schedule_up_to_tomorrow = settings.get("make_invoice_schedule_up_to_tomorrow_only", 0)
	if not make_schedule_up_to_tomorrow:
		return

	# Proceed with other computations only if the setting is enabled
	use_valid_from_date = settings.use_valid_from_date
	allow_backdated = bool(settings.get("allow_backdated_lease_invoice_schedule", 0))
	today_date = getdate(today())
	next_month_end = get_last_day(add_months(today_date, 1))  # End of next month
	invoice_start_date = getdate(settings.get("invoice_start_date", None))

	if not invoice_start_date:
		frappe.throw(_("Please set Invoice Start Date in Property Management Settings"))

	Lease = DocType("Lease")
	eligible_statuses = list(get_active_lease_statuses() or [])
	if allow_backdated:
		eligible_statuses.append("Expired")
	query = (
		frappe.qb.from_(Lease)
		.select(Lease.name)
		.where(Lease.lease_status.isin(eligible_statuses or [""]))
	)
	lease_names = [row[0] for row in query.run()]

	for lease_name in lease_names:
		try:
			lease = frappe.get_doc("Lease", lease_name)
			lease_start = getdate(lease.start_date)
			schedule_end = getdate(lease.end_date) if lease.end_date else next_month_end

			# Retain the original billing cycle; filter on actual invoice date.
			if not lease_start:
				continue

			# A future lease becomes eligible on its first invoice date,
			# not on the rental commencement date. This permits invoices
			# to be raised in advance without scheduling all future leases.
			first_invoice_date = getdate(add_days(
				lease_start, -(lease.days_to_invoice_in_advance or 0)
			))
			if first_invoice_date > today_date:
				continue

			# Clean up obsolete schedules only when no Sales Invoice or Sales Order
			# is linked, matching the protection in the manual lease generator.
			lease_item_names = {li.lease_item for li in lease.lease_item}
			schedule_items = frappe.get_all(
				"Lease Invoice Schedule",
				filters={"parent": lease.name},
				fields=["name", "lease_item", "invoice_number", "sales_order_number"],
			)
			for s in schedule_items:
				if (
					s.lease_item not in lease_item_names
					and not s.invoice_number
					and not s.sales_order_number
				):
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

				# Start on the original lease date, even for mid-month contracts.
				invoice_date = lease_start

				# Generate invoice schedules up to next month
				while schedule_end >= invoice_date and invoice_date <= next_month_end:
					# Calculate period end as last day of the month after freq months
					invoice_period_end = get_last_day(add_months(invoice_date, freq - 1))

					# The cutoff and duplicate checks use the invoice date
					# after applying invoice-in-advance days.
					date_to_invoice = getdate(add_days(
						invoice_date, -(lease.days_to_invoice_in_advance or 0)
					))
					if date_to_invoice >= invoice_start_date:
						exists = frappe.db.exists(
							"Lease Invoice Schedule",
							{
								"parent": lease.name,
								"lease_item": item.lease_item,
								"schedule_start_date": invoice_date,
							},
							) or frappe.db.exists(
							"Lease Invoice Schedule",
							{
								"parent": lease.name,
								"lease_item": item.lease_item,
								"date_to_invoice": date_to_invoice,
							},
							)
						if not exists:
							item_amount = item.amount
							if use_valid_from_date:
								# Rate valid for the rental period, not today's rate.
								lease_items = frappe.get_all(
									"Lease Item",
									filters={
										"parent": lease.name,
										"lease_item": item.lease_item,
										"valid_from": ("<=", invoice_date),
									},
									fields=["amount", "valid_from"],
									order_by="valid_from desc",
									limit=1,
								)
								if lease_items:
									item_amount = lease_items[0].amount
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

			frappe.msgprint(_("Completed invoice schedule for Lease: {0}").format(lease.name))

		except Exception as e:
			frappe.msgprint(_("Error in {0}. Check app error log.").format(lease_name))
			app_error_log(frappe.session.user, f"{lease_name}: {str(e)}")
