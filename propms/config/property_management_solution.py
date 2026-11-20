from frappe import _


def get_data():
	return [
		{
			"label": _("Masters"),
			"items": [
				{
					"type": "doctype",
					"name": "Property",
					"label": _("Properties & Units"),
				},
				{
					"type": "doctype",
					"name": "Unit Type",
					"label": _("Unit Type"),
				},
				{
					"type": "doctype",
					"name": "Customer",
					"label": _("Tenants & Owners"),
				},
				{
					"type": "doctype",
					"name": "Contact",
					"label": _("Contact"),
				},
				{
					"type": "doctype",
					"name": "Item",
					"label": _("Billing Items"),
				},
			],
		},
		{
			"label": _("Transactions"),
			"items": [
				{
					"type": "doctype",
					"name": "Lease",
					"label": _("Lease"),
				},
				{
					"type": "doctype",
					"name": "Exit",
					"label": _("Lease Exits"),
				},
				{
					"type": "doctype",
					"name": "Insurance",
					"label": _("Insurance"),
				},
				{
					"type": "doctype",
					"name": "Sales Order",
					"label": _("Sales Order"),
				},
				{
					"type": "doctype",
					"name": "Sales Invoice",
					"label": _("Sales Invoice"),
				},
				{
					"type": "doctype",
					"name": "Payment Entry",
					"label": _("Payment Entry"),
				},
			],
		},
		{
			"label": _("Lease & Occupancy Reports"),
			"items": [
				{
					"type": "report",
					"name": "Lease Information",
					"label": _("Lease Information"),
					"is_query_report": True,
					"doctype": "Lease",
				},
				{
					"type": "report",
					"name": "Property Status",
					"label": _("Property Status"),
					"is_query_report": True,
					"doctype": "Lease",
				},
				{
					"type": "report",
					"name": "Property Status Report",
					"label": _("Property Status Register"),
					"is_query_report": False,
					"doctype": "Lease",
				},
				{
					"type": "report",
					"name": "Customer Report",
					"label": _("Lease Customer Register"),
					"is_query_report": False,
					"doctype": "Lease",
				},
				{
					"type": "report",
					"name": "Pending Signed Agreement",
					"label": _("Pending Signed Agreement"),
					"is_query_report": False,
					"doctype": "Lease",
				},
				{
					"type": "report",
					"name": "Notification Report",
					"label": _("Lease Notifications"),
					"is_query_report": False,
					"doctype": "Lease",
				},
			],
		},
		{
			"label": _("Billing & Income Reports"),
			"items": [
				{
					"type": "report",
					"name": "Rent Invoices Details",
					"label": _("Rent Invoices Details"),
					"is_query_report": True,
					"doctype": "Sales Invoice",
				},
				{
					"type": "report",
					"name": "Rent Invoices Details USD",
					"label": _("Rent Invoices Details USD"),
					"is_query_report": True,
					"doctype": "Sales Invoice",
				},
				{
					"type": "report",
					"name": "Invoice Details",
					"label": _("Invoice Details"),
					"is_query_report": True,
					"doctype": "Sales Invoice",
				},
				{
					"type": "report",
					"name": "Mis-Income Break Up",
					"label": _("Income Breakdown"),
					"is_query_report": True,
					"doctype": "Sales Invoice",
				},
				{
					"type": "report",
					"name": "Subscription Service Report",
					"label": _("Subscription Service Report"),
					"is_query_report": True,
					"doctype": "Sales Invoice",
				},
				{
					"type": "report",
					"name": "Utility Invoices",
					"label": _("Utility Invoices"),
					"is_query_report": True,
					"doctype": "Sales Invoice",
				},
			],
		},
		{
			"label": _("Collections & Tax Reports"),
			"items": [
				{
					"type": "report",
					"name": "Debtors Report",
					"label": _("Debtors Report"),
					"is_query_report": True,
					"doctype": "Sales Invoice",
				},
				{
					"type": "report",
					"name": "Creditors Report",
					"label": _("Creditors Report"),
					"is_query_report": True,
					"doctype": "Purchase Invoice",
				},
				{
					"type": "report",
					"name": "Security Deposit",
					"label": _("Security Deposit"),
					"is_query_report": True,
					"doctype": "Journal Entry",
				},
				{
					"type": "report",
					"name": "Stamp Duty Paid by Tenant",
					"label": _("Stamp Duty Paid by Tenant"),
					"is_query_report": False,
					"doctype": "Lease",
				},
				{
					"type": "report",
					"name": "Withholding Tax Summary on Sales for Properties",
					"label": _("Property Withholding Tax"),
					"is_query_report": True,
					"doctype": "Sales Invoice",
				},
			],
		},
		{
			"label": _("Operations"),
			"items": [
				{
					"type": "doctype",
					"name": "Daily Checklist",
					"label": _("Daily Checklist"),
				},
				{
					"type": "doctype",
					"name": "Issue",
					"label": _("Maintenance Job Cards"),
				},
				{
					"type": "doctype",
					"name": "Material Request",
					"label": _("Material Request"),
				},
				{
					"type": "doctype",
					"name": "Meter Reading",
					"label": _("Meter Reading"),
				},
				{
					"type": "doctype",
					"name": "Security Attendance",
					"label": _("Security Attendance"),
				},
				{
					"type": "doctype",
					"name": "Outsourcing Attendance",
					"label": _("Outsourcing Attendance"),
				},
			],
		},
		{
			"label": _("Custody Transactions"),
			"items": [
				{
					"type": "doctype",
					"name": "Key Set Detail",
					"label": _("Key Issue & Return"),
				},
				{
					"type": "doctype",
					"name": "Tool Item Record",
					"label": _("Tool Issue & Return"),
				},
			],
		},
		{
			"label": _("Masters"),
			"items": [
				{
					"type": "doctype",
					"name": "Checklist Checkup Area",
					"label": _("Checklist Checkup Area"),
				},
				{
					"type": "doctype",
					"name": "Meter",
					"label": _("Meter"),
				},
				{
					"type": "doctype",
					"name": "Guard Shift",
					"label": _("Guard Shift"),
				},
				{
					"type": "doctype",
					"name": "Outsourcing Category",
					"label": _("Outsourcing Category"),
				},
				{
					"type": "doctype",
					"name": "Outsourcing Shift",
					"label": _("Outsourcing Shift"),
				},
			],
		},
		{
			"label": _("Custody Masters"),
			"items": [
				{
					"type": "doctype",
					"name": "Key Set",
					"label": _("Key Set"),
				},
				{
					"type": "doctype",
					"name": "Tool Item Set",
					"label": _("Tool Item Set"),
				},
			],
		},
		{
			"label": _("Reports & Analytics"),
			"items": [
				{
					"type": "report",
					"name": "Security Attendance Report",
					"label": _("Security Attendance Report"),
					"is_query_report": True,
					"doctype": "Security Attendance",
				},
				{
					"type": "report",
					"name": "Outsourcing Attendance",
					"label": _("Outsourcing Attendance Report"),
					"is_query_report": True,
					"doctype": "Outsourcing Attendance",
				},
				{
					"type": "report",
					"name": "Self Consumption in Maintenance Job Card",
					"label": _("Self Consumption in Maintenance Job Card"),
					"is_query_report": True,
					"doctype": "Issue",
				},
			],
		},
		{
			"label": _("Settings"),
			"items": [
				{
					"type": "doctype",
					"name": "Property Management Settings",
					"label": _("Property Management Settings"),
				},
			],
		},
		{
			"label": _("Legacy Registers"),
			"items": [
				{
					"type": "doctype",
					"name": "Apartment Status",
					"label": _("Apartment Status"),
				},
				{
					"type": "doctype",
					"name": "Security Deposit Details",
					"label": _("Security Deposit Details"),
				},
			],
		},
	]
