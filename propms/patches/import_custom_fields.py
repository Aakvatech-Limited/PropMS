import frappe
import json
import os

def execute():
    # Import custom fields from JSON files
    json_files = [
        "01_init.json",
        "02_territory_custom_field.json"
    ]

    for json_file in json_files:
        file_path = os.path.join(
            frappe.get_app_path("propms"),
            "patches",
            "custom_fields",
            "custom_fields_json",
            json_file
        )

        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    custom_fields = json.load(f)

                for field_data in custom_fields:
                    # Check if custom field already exists
                    if not frappe.db.exists("Custom Field", field_data.get("name")):
                        try:
                            # Create new custom field document
                            doc = frappe.get_doc(field_data)
                            doc.insert(ignore_permissions=True)
                            frappe.logger().info(f"Created Custom Field: {field_data.get('name')}")
                        except Exception as e:
                            frappe.logger().error(f"Error creating Custom Field {field_data.get('name')}: {str(e)}")
                    else:
                        frappe.logger().info(f"Custom Field {field_data.get('name')} already exists, skipping")

            except Exception as e:
                frappe.logger().error(f"Error processing {json_file}: {str(e)}")
        else:
            frappe.logger().warning(f"Custom fields JSON file not found: {file_path}")

    # Commit the changes
    frappe.db.commit()
