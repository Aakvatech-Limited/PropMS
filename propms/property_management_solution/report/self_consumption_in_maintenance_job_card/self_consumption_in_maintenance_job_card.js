frappe.query_reports["Self Consumption in Maintenance Job Card"] = {
    "filters": [
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
        },
    ]
}
