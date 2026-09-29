import json
from pathlib import Path

import frappe


APP_ROLES = (
	"Property Manager",
	"Maintenance Manager",
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


def _delete_app_roles():
	# "Has Role" is used by User, Role Profile, Report roles, and similar child tables.
	frappe.db.delete("Has Role", {"role": ["in", list(APP_ROLES)]})

	for role in APP_ROLES:
		if frappe.db.exists("Role", role):
			frappe.delete_doc("Role", role, ignore_permissions=True, force=True)


def after_uninstall():
	"""Remove PropMS customizations that Frappe leaves behind after uninstall-app."""
	app_doctypes = _get_app_doctypes()

	_delete_app_custom_docperms(app_doctypes)
	_delete_app_custom_fields(app_doctypes)
	_delete_app_property_setters(app_doctypes)
	_delete_app_roles()

	frappe.clear_cache()
