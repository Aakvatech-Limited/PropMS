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
            fieldname: 'type_name',
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
            "fieldname":"from_date",
            "label": __("Start Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.year_start(),
            "reqd": 1
        },
        {
            "fieldname":"to_date",
            "label": __("End Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        }
	]
};
