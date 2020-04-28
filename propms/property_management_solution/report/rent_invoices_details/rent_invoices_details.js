// Copyright (c) 2016, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Rent Invoices Details"] = {
	"filters": [
		{
            fieldname: 'company',
            label: __('Company'),
            fieldtype: 'Link',
            options: 'Company',
			default: frappe.defaults.get_user_default('company'),
			"reqd": 1
        },
        {
            fieldname: 'Type',
            label: __('Type'),
            fieldtype: 'Select',
            options: [
                'All',
                'Rent',
				'Maintenance',
                'Utility'
            ],
			default: 'All',
			"reqd": 1
		},
		{
            "fieldname":"start_date",
            "label": __("Start Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1
        },
        {
            "fieldname":"end_date",
            "label": __("End Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        }
	]
};
