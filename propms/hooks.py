# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "propms"
app_title = "Property Management Solution"
app_publisher = "Aakvatech"
app_description = "Property Management Solution"
app_icon = "octicon octicon-home"
app_color = "grey"
app_email = "info@aakvatech.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/propms/css/propms.css"
# app_include_js = "/assets/propms/js/propms.js"

# include js, css files in header of web template
# web_include_css = "/assets/propms/css/propms.css"
# web_include_js = "/assets/propms/js/propms.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}
page_js = {
	"pos" : "property_management_solution/point_of_sale.js",
	"point-of-sale" : "property_management_solution/point_of_sale.js"
}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {
	"Sales Invoice" : "property_management_solution/sales_invoice.js",
	"Journal Entry Account" : "property_management_solution/journal_entry_account.js",
	"Issue" : "property_management_solution/issue.js",
	"Company" : "property_management_solution/company.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "propms.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "propms.install.before_install"
# after_install = "propms.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "propms.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

fixtures = [
	{"doctype":"Custom Field", "filters": [["name", "in", (
		"Item-reading_required",
		"Sales Invoice-lease_item",
		"Sales Invoice-lease_information",
		"Sales Invoice-lease",
		"Issue-sub_contractor_name",
		"Issue-customer_feedback",
		"Issue-section_break_15",
		"Issue-col_brk_001",
		"Issue-property_name",
		"Issue-person_in_charge",
		"Material Request-sales_invoice",
		"Issue-sub_contractor_contact",
		"Issue-materials_required",
		"Issue-material_request",
		"Issue-column_break_14",
		"Issue-defect_found",
		"Issue-person_in_charge_name",
		"Sales Invoice-job_card",
		"Issue-column_break_4",
		"Issue-materials_billed",
		"Quotation-cost_center",
		"Company-property_management_settings",
		"Company-security_account_code",
		"Company-default_tax_account_head",
		"Company-default_tax_template",
		"Company-default_maintenance_tax_template"
	)]]},
	{"doctype":"Property Setter", "filters": [["name", "in", (
		"Contact-department-fieldtype",
		"Contact-department-options",
		# "Security Attendance-default_print_format",
		"Daily Checklist-default_print_format",
		"Issue-issue_type-reqd",
		"Issue-status-options",
		"Issue-raised_by-in_list_view",
		"Issue-opening_date-in_list_view",
		# "Issue-default_print_format",
		"Issue-quick_entry",
		"Issue-email_account-report_hide",
		"Issue-raised_by-report_hide",
		"Issue-section_break_19-collapsible",
		"Issue-section_break_7-collapsible",
		"Issue-issue_type-in_standard_filter",
		"Issue-priority-in_standard_filter",
		"Lease-security_status-options",
		"Lease-wtax_paid_by-in_standard_filter",
		"Lease-property-in_standard_filter",
		"Lease-security_status-in_standard_filter",
		"Lease-property_user-in_standard_filter",
		"Lease-customer-in_standard_filter",
		"Lease-lease_customer-in_standard_filter",
		"Lease-property_owner-in_standard_filter",
		# "Payment Entry-default_print_format",
		# "Outsourcing Attendance-default_print_format",
		"Lease-end_date-in_list_view",
		"Lease-start_date-in_list_view",
		"Lease-customer-in_list_view",
		"Lease-property_owner-in_list_view",
		"Journal Entry Account-cost_center-columns",
		"Journal Entry Account-party_type-columns",
		"Journal Entry Account-party-columns",
		"Journal Entry Account-account-columns",
		"Material Request-material_request_type-options",
		"Key Set Detail-key_set-in_standard_filter",
		"Key Set Detail-returned-in_standard_filter",
		"Key Set Detail-taken_by-in_standard_filter",
		"Property-section_break_22-bold",
		"Property-section_break_13-bold",
		"Property-section_break_4-bold",
		"Property-identification_section-bold",
		"Unit Type-search_fields",
		"Issue-customer-fetch_from"
	)]]},
]


doc_events = {
	"Issue": {
		"validate": [
			"propms.issue_hook.validate",
			],
	},
	"Material Request": {
		"validate": "propms.auto_custom.makeSalesInvoice",
		"on_update":"propms.auto_custom.makeSalesInvoice",
		"on_change":"propms.auto_custom.makeSalesInvoice"

	},
	"Sales Order": {
		"validate": "propms.auto_custom.validateSalesInvoiceItemDuplication"
	},
	"Key Set Detail": {
		"on_change": "propms.auto_custom.changeStatusKeyset"
	},
	"Meter Reading": {
		"before_submit": "propms.auto_custom.make_invoice_meter_reading"
	}


}


scheduler_events = {
	"daily": [
		"propms.auto_custom.statusChangeBeforeLeaseExpire",
		"propms.auto_custom.statusChangeAfterLeaseExpire"
	],
	"cron": {
		"00 12 * * *": [
			"propms.lease_invoice.leaseInvoiceAutoCreate"
			]
		}
}





# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"propms.tasks.all"
#	],
#	"daily": [
#		"propms.tasks.daily"
#	],
#	"hourly": [
#		"propms.tasks.hourly"
#	],
#	"weekly": [
#		"propms.tasks.weekly"
#	]
#	"monthly": [
#		"propms.tasks.monthly"
#	]
# }

# Testing
# -------

# before_tests = "propms.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "propms.event.get_events"
# }

