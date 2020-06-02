// Copyright (c) 2016, Aakvatech
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Withholding Tax Summary on Sales (Properties)"] = {
	"filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
        },
	]
};