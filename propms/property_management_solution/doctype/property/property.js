// Copyright (c) 2018, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Property', {
	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(
				__("Create Cost Center"),
				function () {
					let dialog = new frappe.ui.Dialog({
						title: __("Create Cost Center"),
						fields: [
							{
								fieldtype: "Data",
								fieldname: "cost_center_name",
								label: __("Cost Center Name"),
								reqd: 1,
							},
							{
								fieldtype: "Link",
								fieldname: "parent_cost_center",
								label: __("Parent Cost Center"),
								options: "Cost Center",
								reqd: 1,
								get_query: function () {
									return {
										filters: {
											is_group: 1,
										},
									};
								},
							},
							{
								fieldtype: "Link",
								fieldname: "company",
								label: __("Company"),
								options: "Company",
								reqd: 1,
								default: frappe.defaults.get_default("Company"),
							},
						],
						primary_action_label: __("Create"),
						primary_action(values) {
							frappe.call({
								method: "frappe.client.insert",
								args: {
									doc: {
										doctype: "Cost Center",
										cost_center_name: values.cost_center_name,
										parent_cost_center: values.parent_cost_center,
										company: values.company,
									},
								},
								callback: function (r) {
									if (r.message) {
										frm.set_value("cost_center", r.message.name);

										frappe.show_alert({
											message: __("Cost Center Created Successfully"),
											indicator: "green",
										});

										dialog.hide();
									}
								},
							});
						},
					});

					dialog.show();
				},
				__("Actions"),
			);
		}
	},
	setup: function(frm) {
		frm.set_query("cost_center", function() {
			return {
				"filters": {
                    "company": frm.doc.company,
				},
			};
		});

		frm.set_query("parent_property", {is_group: 1});
		frm.set_query("lease_item", "lease_increment_rules", function() {
			return {
				"filters": [
					["item_group", "=", "Lease Items"],
				]
			};
		});
	},
	company: function(frm) {
		frm.set_value("cost_center", "");
	},
});

frappe.ui.form.on('Property Meter Reading', {
    meter_number: function(frm,cdt,cdn) {
		var property_doc = frm.doc;
		var meter_doc = locals[cdt][cdn];
		if (meter_doc.meter_number != "") {
			$.each(property_doc.property_meter_reading, function(i, d) {
				if(d.name!=meter_doc.name && meter_doc.meter_type==d.meter_type && d.status=="Active")	{
					var msg="Another Active Meter of type "+meter_doc.meter_type+" Is Already allocated. Please de-activate it before adding a new meter of same type."
					frappe.model.set_value(cdt,cdn,"meter_number",'')
					frappe.throw(__(msg))
				}
			})
		}
	},
	status: function(frm,cdt,cdn) {
		var property_doc = frm.doc;
		var meter_doc = locals[cdt][cdn];
		if (meter_doc.meter_number != "") {
			$.each(property_doc.property_meter_reading, function(i, d) {
				if(d.name!=meter_doc.name && meter_doc.meter_type==d.meter_type && d.status=="Active")	{
					var msg="Another Active Meter of type "+meter_doc.meter_type+" Is Already allocated. Please de-activate it before adding a new meter of same type."
					frappe.model.set_value(cdt,cdn,"status",'')
					frappe.throw(__(msg))
				}
			})
		}
	}
})
