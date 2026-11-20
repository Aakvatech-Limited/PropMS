import json
import os

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

folder = "../patches/property_setter/property_setter_json"


def load_json(file):
	CURR_DIR = os.path.abspath(os.path.dirname(__file__))
	json_file_path = os.path.join(CURR_DIR, folder, file)
	with open(json_file_path) as file:
		data = json.load(file)
	return data


def create_property_setter_from_json(property_setters_obj):
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

	# Fetching existing setters using composite key (DocType, Field, Property)
	existing_data = frappe.db.get_all(
		"Property Setter",
		fields=["name", "doc_type", "field_name", "property", "value", "property_type"],
		page_length=20000,
	)

	# Create a mapping: {(doc_type, field_name, property): record}
	existing_map = {}
	for d in existing_data:
		key = (d.doc_type, d.field_name or "", d.property)
		existing_map[key] = d

	for property_setter in property_setters_obj:
		doc_type = property_setter.get("doc_type")
		field_name = property_setter.get("field_name")
		prop = property_setter.get("property")
		key = (doc_type, field_name or "", prop)

		if key in existing_map:
			existing = existing_map[key]

			# Normalizing values for comparison
			old_val = str(existing.get("value") if existing.get("value") is not None else "")
			new_val = str(property_setter.get("value") if property_setter.get("value") is not None else "")

			old_prop_type = str(
				existing.get("property_type") if existing.get("property_type") is not None else ""
			)
			new_prop_type = str(
				property_setter.get("property_type")
				if property_setter.get("property_type") is not None
				else ""
			)

			if old_val.strip() == new_val.strip() and old_prop_type.strip() == new_prop_type.strip():
				continue

		if property_setter.get("doctype_or_field") == "DocType":
			for_doctype = True
		else:
			for_doctype = False

		all_fields = frappe.get_meta("Property Setter").get_valid_columns()
		field_list = set(all_fields).difference(disallowed_fields)

		property_setter_dict = {
			field: property_setter.get(field) for field in field_list if field in property_setter
		}

		make_property_setter(
			doctype=property_setter_dict["doc_type"],
			fieldname=property_setter_dict.get("field_name", None),
			property=property_setter_dict["property"],
			value=property_setter_dict["value"],
			property_type=property_setter_dict["property_type"],
			for_doctype=for_doctype,
		)


def execute():
	# read names of only json files in this folder and put it into files list
	files = list(
		filter(
			lambda x: x.endswith(".json"),
			os.listdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), folder)),
		)
	)
	for file in files:
		data = load_json(file)
		create_property_setter_from_json(data)
