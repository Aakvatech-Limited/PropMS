import json
from pathlib import Path

import frappe

# Roles introduced by PropMS. "Maintenance Manager" is deliberately absent: ERPNext
# ships it on Quotation, Maintenance Schedule, Competitor and Quotation Lost Reason,
# and Frappe grants it on Contact, so it has to outlive PropMS.
APP_ROLES = (
	"Property Manager",
	"Floor Maintenance Supervisor",
	"Maintenance Job in-charge",
)

APP_ROOT = Path(__file__).resolve().parent
DOCTYPE_ROOT = APP_ROOT / "property_management_solution" / "doctype"
CUSTOM_FIELD_ROOT = APP_ROOT / "patches" / "custom_fields" / "custom_fields_json"
PROPERTY_SETTER_ROOT = APP_ROOT / "patches" / "property_setter" / "property_setter_json"


def _load_json(path):
	with path.open(encoding="utf-8") as handle:
		return json.load(handle)


def _get_app_doctypes():
	doctypes = set()

	for path in DOCTYPE_ROOT.glob("*/*.json"):
		data = _load_json(path)
		if data.get("doctype") == "DocType" and data.get("name"):
			doctypes.add(data["name"])

	return doctypes


def _iter_json_records(root):
	if not root.exists():
		return

	for path in root.glob("*.json"):
		data = _load_json(path)
		if isinstance(data, list):
			yield from data
		elif isinstance(data, dict):
			yield data


def _delete_app_custom_fields(app_doctypes):
	# Remove custom fields attached to DocTypes that belong to PropMS.
	if app_doctypes:
		frappe.db.delete("Custom Field", {"dt": ["in", list(app_doctypes)]})

	# Remove fields PropMS created on standard/core DocTypes.
	for record in _iter_json_records(CUSTOM_FIELD_ROOT):
		dt = record.get("dt")
		fieldname = record.get("fieldname")
		if dt and fieldname:
			frappe.db.delete("Custom Field", {"dt": dt, "fieldname": fieldname})


def _delete_app_property_setters(app_doctypes):
	# Remove setters attached to DocTypes that belong to PropMS.
	if app_doctypes:
		frappe.db.delete("Property Setter", {"doc_type": ["in", list(app_doctypes)]})

	# Remove setters PropMS created on standard/core DocTypes.
	for record in _iter_json_records(PROPERTY_SETTER_ROOT):
		doc_type = record.get("doc_type")
		property_name = record.get("property")
		if not doc_type or not property_name:
			continue

		filters = {
			"doc_type": doc_type,
			"property": property_name,
			"field_name": record.get("field_name") or "",
		}
		frappe.db.delete("Property Setter", filters)


def _delete_app_custom_docperms(app_doctypes):
	if app_doctypes:
		frappe.db.delete("Custom DocPerm", {"parent": ["in", list(app_doctypes)]})

	# PropMS-specific roles should not remain on Custom DocPerm rows for core DocTypes.
	frappe.db.delete("Custom DocPerm", {"role": ["in", list(APP_ROLES)]})


def _is_role_still_granted(role):
	"""True while a DocType, or a report, page or web form, still grants this role.

	Keeps a role another app owns out of reach even if APP_ROLES drifts.
	"""
	if frappe.db.count("DocPerm", {"role": role}):
		return True
	if frappe.db.count("Custom DocPerm", {"role": role}):
		return True
	return bool(frappe.db.count("Has Role", {"role": role, "parenttype": ("!=", "User")}))


def _disable_app_roles():
	"""Disable the PropMS roles that nothing grants any more, rather than deleting them.

	Deleting a Role drops its "Has Role" rows, which silently strips the role from users
	and from other apps' reports. Any fixture that still grants it then recreates a
	"Has Role" row pointing at a Role that no longer exists, which is the orphan class
	this cleanup exists to prevent.
	"""
	for role in APP_ROLES:
		if not frappe.db.exists("Role", role):
			continue
		if _is_role_still_granted(role):
			continue
		frappe.db.set_value("Role", role, "disabled", 1)


def after_uninstall():
	"""Remove PropMS customizations that Frappe leaves behind after uninstall-app."""
	app_doctypes = _get_app_doctypes()

	remaining = sorted(name for name in app_doctypes if frappe.db.exists("DocType", name))
	if remaining:
		# Called outside an uninstall. The custom fields and property setters below are
		# live configuration while the DocTypes exist, so deleting them would lose data.
		print(f"propms: {len(remaining)} DocTypes are still present (e.g. {remaining[0]}), skipping cleanup")
		return

	_delete_app_custom_docperms(app_doctypes)
	_delete_app_custom_fields(app_doctypes)
	_delete_app_property_setters(app_doctypes)
	_disable_app_roles()

	frappe.clear_cache()
