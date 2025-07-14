import frappe
import json
import os

def execute():
    # Import property setters from JSON files
    json_files = [
        "01_init.json"
    ]

    for json_file in json_files:
        file_path = os.path.join(
            frappe.get_app_path("propms"),
            "patches",
            "property_setter",
            "property_setter_json",
            json_file
        )

        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    property_setters = json.load(f)

                for setter_data in property_setters:
                    # Check if property setter already exists
                    if not frappe.db.exists("Property Setter", setter_data.get("name")):
                        try:
                            # Create new property setter document
                            doc = frappe.get_doc(setter_data)
                            doc.insert(ignore_permissions=True)
                            frappe.logger().info(f"Created Property Setter: {setter_data.get('name')}")
                        except Exception as e:
                            frappe.logger().error(f"Error creating Property Setter {setter_data.get('name')}: {str(e)}")
                    else:
                        frappe.logger().info(f"Property Setter {setter_data.get('name')} already exists, skipping")

            except Exception as e:
                frappe.logger().error(f"Error processing {json_file}: {str(e)}")
        else:
            frappe.logger().warning(f"Property setters JSON file not found: {file_path}")

    # Commit the changes
    frappe.db.commit()
