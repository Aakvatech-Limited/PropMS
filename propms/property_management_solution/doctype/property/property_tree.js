frappe.treeview_settings["Property"] = {
	add_tree_node: "propms.property_management_solution.doctype.property.property.add_node",
	filters: [
		{
			fieldname: "company",
			fieldtype:"Link",
			options: "Company",
			label: __("Company"),
			default: frappe.user_defaults.company,
		},
	],
	root_label: __("All Property"),
}
