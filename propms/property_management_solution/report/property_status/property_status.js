// Copyright (c) 2016, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Property Status"] = {
        "filters": [
			{
				"fieldname":"property_type",
				"label": __("Property Type"),
				"fieldtype": "Link",
				"options": "Unit Type",
				"default": " ",
				"reqd": 1
			},
			{
				"fieldname":"owner_type",
				"label": __("Owner Type"),
				"fieldtype": "Link",
				"options": "Customer Group",
				"default": " ",
				"reqd": 1
			},
        ]
}
