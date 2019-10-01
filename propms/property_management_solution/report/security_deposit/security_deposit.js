// Copyright (c) 2016, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Security Deposit"] = {
        "filters": [

			{
				"fieldname":"account",
				"label": __("Account"),
				"fieldtype": "Link",
				"options": "Account",
				"default": "21401 - Security Deposit Commercial - VPL",	
				"get_query": function() {
					return {
						"query": "erpnext.controllers.queries.get_account_list",
						"filters": [
							['Account', 'account_number', 'like', '214%'],
							['Account', 'is_group', '=', 0],
						]
					}
				}
			},
        ]
}