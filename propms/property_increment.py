import math

import frappe
from frappe import _
from frappe.utils import add_months, getdate, nowdate
from frappe.utils.data import cint, flt

VALID_UOM = {"Month": 1, "Year": 12}
VALID_INCREMENT_TYPES = {"Percent", "Amount"}
VALID_ROUNDING_MODES = {"Round", "Ceil", "Floor", "None"}


def validate_property_increment_settings(doc, method=None):
	if not cint(doc.get("enable_auto_increment")):
		return

	horizon_months = cint(doc.get("auto_create_lease_items_for_months"))
	if horizon_months <= 0:
		frappe.throw(_("Auto Create Lease Items For Months must be greater than 0."))

	rules = doc.get("lease_increment_rules") or []
	if not rules:
		frappe.throw(_("Please add at least one Lease Increment Rule."))

	rounding_mode = (doc.get("increment_rounding_mode") or "Round").strip()
	if rounding_mode not in VALID_ROUNDING_MODES:
		frappe.throw(_("Increment Rounding Mode must be one of: Round, Ceil, Floor, None."))

	rounding_precision = cint(doc.get("increment_rounding_precision"))
	if rounding_precision < 0:
		frappe.throw(_("Increment Rounding Precision cannot be negative."))

	default_effective_from = doc.get("increment_effective_from")
	seen_rules = set()

	for row in rules:
		if not cint(row.get("is_active")):
			continue

		lease_item = row.get("lease_item")
		if not lease_item:
			frappe.throw(_("Lease Item is mandatory in Lease Increment Rules."))

		increment_every = cint(row.get("increment_every"))
		if increment_every <= 0:
			frappe.throw(_("Increment Every must be greater than 0 for Lease Item {0}.").format(lease_item))

		increment_uom = row.get("increment_uom")
		if increment_uom not in VALID_UOM:
			frappe.throw(_("Increment UOM must be Month or Year for Lease Item {0}.").format(lease_item))

		increment_type = row.get("increment_type")
		if increment_type not in VALID_INCREMENT_TYPES:
			frappe.throw(_("Increment Type must be Percent or Amount for Lease Item {0}.").format(lease_item))

		increment_value = flt(row.get("increment_value"))
		if increment_value <= 0:
			frappe.throw(_("Increment Value must be greater than 0 for Lease Item {0}.").format(lease_item))

		rule_effective_from = row.get("rule_effective_from") or default_effective_from
		if not rule_effective_from:
			frappe.throw(_("Rule Effective From is required for Lease Item {0}.").format(lease_item))

		dedupe_key = (lease_item, str(getdate(rule_effective_from)))
		if dedupe_key in seen_rules:
			frappe.throw(
				_("Duplicate active rule found for Lease Item {0} on {1}.").format(lease_item, dedupe_key[1])
			)
		seen_rules.add(dedupe_key)


def run_property_increment_engine():
	_run_increment_engine()


def _run_increment_engine():
	property_names = frappe.get_all("Property", filters={"enable_auto_increment": 1}, pluck="name")
	if not property_names:
		return

	for property_name in property_names:
		try:
			_process_property(property_name)
		except Exception:
			_log_increment_error(
				title="Property Increment Engine Error",
				details={
					"property": property_name,
					"stage": "property_loop",
				},
			)


def _process_property(property_name):
	property_doc = frappe.get_doc("Property", property_name)

	if not cint(property_doc.get("enable_auto_increment")):
		return

	horizon_months = cint(property_doc.get("auto_create_lease_items_for_months"))
	if horizon_months <= 0:
		return

	rules = [row for row in (property_doc.get("lease_increment_rules") or []) if cint(row.get("is_active"))]
	if not rules:
		return

	today = getdate(nowdate())
	horizon_end = getdate(add_months(today, horizon_months))
	default_effective_from = property_doc.get("increment_effective_from")

	leases = frappe.get_all(
		"Lease",
		filters={"property": property_doc.name, "lease_status": "Active", "docstatus": ["<", 2]},
		fields=["name", "start_date", "end_date"],
	)

	for lease_meta in leases:
		try:
			_process_lease(
				property_doc=property_doc,
				lease_name=lease_meta.name,
				rules=rules,
				default_effective_from=default_effective_from,
				today=today,
				horizon_end=horizon_end,
			)
		except Exception:
			_log_increment_error(
				title="Property Increment Engine Lease Error",
				details={
					"property": property_doc.name,
					"lease": lease_meta.name,
					"stage": "lease_loop",
				},
			)
			continue


def _process_lease(property_doc, lease_name, rules, default_effective_from, today, horizon_end):
	lease = frappe.get_doc("Lease", lease_name)
	lease_changed = False

	for rule in rules:
		rule_context = _build_rule_context(rule, default_effective_from)
		if not rule_context:
			continue

		item_rows = [
			row
			for row in (lease.get("lease_item") or [])
			if row.lease_item == rule_context["lease_item_code"]
		]
		if not item_rows:
			continue

		changed = _apply_rule_to_lease(
			lease=lease,
			property_doc=property_doc,
			rule=rule,
			rule_context=rule_context,
			item_rows=item_rows,
			today=today,
			horizon_end=horizon_end,
		)
		lease_changed = lease_changed or changed

	if lease_changed:
		lease.flags.ignore_validate_update_after_submit = True
		lease.save(ignore_permissions=True)


def _build_rule_context(rule, default_effective_from):
	effective_from = rule.get("rule_effective_from") or default_effective_from
	if not effective_from:
		return None

	interval_months = cint(rule.get("increment_every")) * VALID_UOM.get(rule.get("increment_uom"), 0)
	if interval_months <= 0:
		return None

	lease_item_code = rule.get("lease_item")
	if not lease_item_code:
		return None

	return {
		"effective_from": getdate(effective_from),
		"interval_months": interval_months,
		"lease_item_code": lease_item_code,
	}


def _apply_rule_to_lease(lease, property_doc, rule, rule_context, item_rows, today, horizon_end):
	lease_changed = False
	current_rows = _get_effective_rows(lease, item_rows)
	existing_dates = {row["effective_date"] for row in current_rows}
	candidate_date = rule_context["effective_from"]
	interval_months = rule_context["interval_months"]

	while candidate_date <= horizon_end:
		if lease.end_date and candidate_date > getdate(lease.end_date):
			break

		if candidate_date >= today and candidate_date not in existing_dates:
			prev_row = _get_previous_row(current_rows, candidate_date)
			if prev_row:
				new_amount = _apply_increment(
					prev_row["amount"],
					rule.get("increment_type"),
					rule.get("increment_value"),
					property_doc.get("increment_rounding_mode"),
					property_doc.get("increment_rounding_precision"),
				)
				_append_lease_item_version(lease, prev_row["row"], candidate_date, new_amount)
				current_rows.append(
					{
						"row": lease.get("lease_item")[-1],
						"effective_date": candidate_date,
						"amount": new_amount,
					}
				)
				current_rows.sort(key=lambda x: x["effective_date"])
				existing_dates.add(candidate_date)
				lease_changed = True

		candidate_date = getdate(add_months(candidate_date, interval_months))

	return lease_changed


def _append_lease_item_version(lease, source_row, candidate_date, new_amount):
	lease.append(
		"lease_item",
		{
			"lease_item": source_row.lease_item,
			"frequency": source_row.frequency,
			"amount": new_amount,
			"currency_code": source_row.currency_code,
			"charge_basis": source_row.charge_basis,
			"charge_rate": source_row.charge_rate,
			"witholding_tax": source_row.witholding_tax,
			"paid_by": source_row.paid_by,
			"invoice_item_group": source_row.invoice_item_group,
			"document_type": source_row.document_type,
			"valid_from": candidate_date,
			"is_active": 0,
		},
	)


def _get_effective_rows(lease, item_rows):
	lease_start = getdate(lease.start_date) if lease.start_date else getdate(nowdate())
	rows = []
	for row in item_rows:
		effective_date = getdate(row.valid_from) if row.valid_from else lease_start
		rows.append({"row": row, "effective_date": effective_date, "amount": flt(row.amount)})
	rows.sort(key=lambda x: x["effective_date"])
	return rows


def _get_previous_row(rows, candidate_date):
	previous = None
	for row in rows:
		if row["effective_date"] < candidate_date:
			previous = row
		else:
			break
	return previous


def _apply_increment(amount, increment_type, increment_value, rounding_mode, rounding_precision):
	base_amount = flt(amount)
	increment_value = flt(increment_value)
	precision = cint(rounding_precision) if rounding_precision is not None else 2
	mode = (rounding_mode or "Round").strip()

	if increment_type == "Percent":
		new_amount = base_amount + (base_amount * increment_value / 100.0)
	else:
		new_amount = base_amount + increment_value

	return _round_amount(new_amount, mode, precision)


def _round_amount(amount, mode, precision):
	if mode == "None":
		return amount
	if mode == "Round":
		return round(amount, precision)

	factor = 10**precision
	if mode == "Ceil":
		return math.ceil(amount * factor) / float(factor)
	if mode == "Floor":
		return math.floor(amount * factor) / float(factor)

	return round(amount, precision)


def _log_increment_error(title, details=None):
	context = details or {}
	message_lines = ["Property Increment Engine exception."]
	for key, value in context.items():
		message_lines.append(f"{key}: {value}")
	message_lines.append("")
	message_lines.append(frappe.get_traceback())
	frappe.log_error("\n".join(message_lines), title)
