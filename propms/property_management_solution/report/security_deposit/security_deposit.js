// Copyright (c) 2016, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Security Deposit"] = {
        "filters": [
			{
				"fieldname":"account",
				"label": __("Account"),
				"fieldtype": "Select",
				"width": "120",
				"options": "options": ["21401 - Security Deposit Commercial - VPL","21402 - Security Deposit Residential - VPL"]
			},
        ]
}