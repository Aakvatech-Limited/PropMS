// Copyright (c) 2016, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Lease Information"] = {
        "filters": [
			{
				"fieldname":"property_type",
				"label": __("Property Type"),
				"fieldtype": "Link",
				"options": "Unit Type",
				"default": " ",
				"reqd": 1
			},
        ]
}
