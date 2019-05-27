from __future__ import unicode_literals
from frappe import _
import frappe

def get_data():
	config = [
		{
			"label": _("Property Management Documents"),
			"items": [
				{
					"type": "doctype",
					"name": "Property",
					"description": _("Property that needs to be managed."),
				},
				{
					"type": "doctype",
					"name": "Lease",
					"description": _("Lease pertaining to the properties."),
				},
				{
					"type": "doctype",
					"name": "Key Set Detail",
					"description": _("Key Set Detail"),
				},
				{
					"type": "doctype",
					"name": "Daily Checklist",
					"description": _("Daily Checklist"),
				},
				{
					"type": "doctype",
					"name": "Exit",
					"description": _("Exit"),
				},
				{
					"type": "doctype",
					"name": "Meter Reading",
					"description": _("Meter Reading"),
				},
				{
					"type": "doctype",
					"name": "Outsourcing Attendance",
					"description": _("Outsourcing Attendance"),
				},
				{
					"type": "doctype",
					"name": "Insurance",
					"description": _("Insurance"),
				},
				{
					"type": "doctype",
					"name": "Security Attendance",
					"description": _("Security Attendance"),
				},
				{
					"type": "doctype",
					"name": "Withholding Tax Summary",
					"description": _("Withholding Tax Summary"),
				}
			]
		},
		{
			"label": _("Property Management Masters"),
			"icon": "fa fa-cog",
			"items": [
				{
					"type": "doctype",
					"name": "Apartment Status",
					"description": _("Applicable Apartment Statuses.")
				},
				{
					"type": "doctype",
					"name": "Unit Type",
					"label": _("Unit Type"),
					"description": _("Unit Type definition."),
				},
				{
					"type": "doctype",
					"name": "Property",
					"description": _("Property database.")
				},
				{
					"type": "doctype",
					"name": "Lease Item",
					"label": _("Lease Item"),
					"description": _("Lease Item definition."),
				},
				{
					"type": "doctype",
					"name": "Checklist Checkup Area",
					"icon": "fa fa-sitemap",
					"label": _("Checklist Checkup Area"),
					"description": _("Areas for Checklist Checkup."),
				},
				{
					"type": "doctype",
					"name": "Guard Shift",
					"label": _("Guard Shift"),
					"description": _("Shif for security guards."),
				},
				{
					"type": "doctype",
					"name": "Key Set",
					"icon": "fa fa-sitemap",
					"label": _("Key Set"),
					"description": _("Key sets in custody."),
				},
				{
					"type": "doctype",
					"name": "Outsourcing Category",
					"label": _("Outsourcing Category"),
					"description": _("Outsourcing Category definition."),
				},
				{
					"type": "doctype",
					"name": "Property Amenity",
					"label": _("Property Amenity"),
					"description": _("Property Amenity definition."),
				},
				{
					"type": "doctype",
					"name": "Security Deposit Details",
					"label": _("Security Deposit Details"),
					"description": _("Security Deposit Details definition."),
				},
			]
		},
		{
			"label": _("Property Management Settings"),
			"items": [
				{
					"type": "doctype",
					"name": "Property Management Settings",
					"label": _("Property Management Settings"),
					"description": _("Property Management Settings"),
				},
			]
		},
		{
			"label": _("Property Management Analytics"),
			"items": [
				{
					"type": "report",
					"name": "Outsourcing Attendance",
					"is_query_report": True,
					"doctype": "Outsourcing Attendance",
				},
				{
					"type": "report",
					"name": "Security Attendance Report",
					"is_query_report": True,
					"doctype": "Security Attendance",
				}
			]
		}
	]
	return config