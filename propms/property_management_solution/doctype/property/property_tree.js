frappe.treeview_settings["Property"] = {
	get_tree_nodes: "propms.property_management_solution.doctype.property.property.get_children",
	add_tree_node: "propms.property_management_solution.doctype.property.property.add_node",
	get_tree_root: false,
	root_label: "Property",
	filters: [
		{
			fieldname: "company",
			fieldtype:"Link",
			options: "Company",
			label: __("Company"),
			default: frappe.user_defaults.company,
		},
	],

	fields: [
		{ fieldtype: "Data", fieldname: "name1", label: __("New Property Name"), reqd: true },
		{
			fieldtype: "Check",
			fieldname: "is_group",
			label: __("Is Group"),
			description: __("Child nodes can be only created under 'Group' type nodes"),
		},
	],
	ignore_fields: ["parent_property"],
	root_label: __("All Property"),
}
