import json
from pathlib import Path

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

JSON_DIRECTORY = (
	Path(__file__).resolve().parent.parent / "patches" / "custom_fields/custom_fields_json"
).resolve()


def load_json(file):
	"""Load only JSON filenames directly inside the packaged patch directory."""
	if not isinstance(file, str) or Path(file).name != file or not file.endswith(".json"):
		raise ValueError("Invalid patch JSON filename")
	json_path = (JSON_DIRECTORY / file).resolve()
	if json_path.parent != JSON_DIRECTORY:
		raise ValueError("Patch JSON must be inside the configured directory")
	return json.loads(json_path.read_text(encoding="utf-8"))


def create_fields_from_json(custom_fields_obj):
	disallowed_fields = [
		"name",
		"owner",
		"creation",
		"modified",
		"modified_by",
		"docstatus",
		"idx",
		"is_system_generated",
		"__last_sync_on",
	]
	doctype_custom_fields_dict = {}

	for custom_field in custom_fields_obj:
		doctype = custom_field["dt"]
		all_fields = frappe.get_meta("Custom Field").get_valid_columns()
		field_list = set(all_fields).difference(disallowed_fields)
		custom_field_dict = {}
		for field_name in field_list:
			custom_field_dict[field_name] = custom_field.get(field_name)

		# Ensure the list for the doctype is initialized
		if doctype not in doctype_custom_fields_dict:
			doctype_custom_fields_dict[doctype] = []

		doctype_custom_fields_dict[doctype].append(custom_field_dict)

	create_custom_fields(doctype_custom_fields_dict, update=False)


def execute():
	# read names of only json files in this folder and put it into files list
	files = sorted(
		path.name for path in JSON_DIRECTORY.iterdir() if path.is_file() and path.suffix == ".json"
	)
	for file in files:
		data = load_json(file)
		create_fields_from_json(data)


@frappe.whitelist()
def export_custom_fields(docnames):
	docnames = frappe.parse_json(docnames)
	custom_fields = []

	for docname in docnames:
		doc = frappe.get_doc("Custom Field", docname)
		custom_fields.append(doc.as_dict(convert_dates_to_str=True, no_default_fields=True, no_nulls=True))

	return str(custom_fields)
