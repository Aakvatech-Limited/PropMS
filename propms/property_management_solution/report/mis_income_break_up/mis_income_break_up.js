// Copyright (c) 2016, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */
var months = "January\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember"
frappe.query_reports["Mis-Income Break Up"] = {
	"filters": [
		{
			"fieldname":"from",
			"label": __("From Month"),
			"fieldtype": "Select",
			"options": months,
			"default": "January"
		},
		{
			"fieldname":"to",
			"label": __("To Month"),
			"fieldtype": "Select",
			"options": months,
			"default": "December"
		},
		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year"
		}
	],
	"formatter": function(value, row, column, data, default_formatter) {
	    value = default_formatter(value, row, column, data);
	    if (row[0].rowIndex === 5 || value === "RENTAL INCOME" || value === "MAINTENANCE INCOME" || value === "Maintenance Total"){
	        value = '<b style="font-weight:bold">'+value+'</b>';
	    }
	    return value;
	}

};
