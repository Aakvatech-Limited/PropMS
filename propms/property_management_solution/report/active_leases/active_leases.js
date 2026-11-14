frappe.query_reports["Active Leases"] = {
	filters: [
		{ fieldname: "as_on", label: __("As On"), fieldtype: "Date", default: frappe.datetime.get_today() },
		{ fieldname: "property", label: __("Property"), fieldtype: "Link", options: "Property" },
	],
};
