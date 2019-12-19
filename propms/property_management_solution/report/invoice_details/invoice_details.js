// Copyright (c) 2016, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Invoice Details"] = {
	"filters": [
		{
			"fieldname":"rental",
			"label": __("Rental"),
			"fieldtype": "Select",
			"options": "Commercial Rent\nResidential Rent",
			"default": "Commercial Rent"
		},
		{
			"fieldname":"maintenance",
			"label": __("Maintenance"),
			"fieldtype": "Check"
		},
		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year"
		}
	]
};
