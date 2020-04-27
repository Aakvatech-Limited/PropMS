// Copyright (c) 2016, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Subscription Service Report"] = {
        "filters": [
			{
				"fieldname":"service_type",
				"label": __("Service Type"),
				"fieldtype": "Link",
				"options": "Item",
				"default": "Gym services",
				"reqd": 1
				get_query: () => {
					return {
						filters: {
							'item_group': "Services"
						}
					}
				}
			},	
			{
				"fieldname":"to_date",
				"label": __("To Date"),
				"fieldtype": "Date",
				"default": frappe.datetime.get_today(),
				"reqd": 1
			}
        ]
}
