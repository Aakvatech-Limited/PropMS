// Copyright (c) 2018, Aakvatech and contributors
// For license information, please see license.txt
cur_frm.add_fetch('property', 'unit_owner', 'property_owner');
cur_frm.cscript.lease_item_add = function(doc, cdt, cdn) {
	if (!doc.lease_customer) {
		return;
	}

	const row = locals[cdt][cdn];
	row.paid_by = doc.lease_customer;
	cur_frm.refresh_field('lease_item');
};

frappe.ui.form.on('Lease', {
	lease_customer: function(frm) {
		if (!frm.doc.lease_customer) {
			return;
		}

		(frm.doc.lease_item || []).forEach((row) => {
			row.paid_by = frm.doc.lease_customer;
		});

		frm.refresh_field('lease_item');
	},
	setup: function(frm) {
		frm.set_query("lease_item", "lease_item", function() {
			return {
				"filters": [
                    ["item_group","=", "Lease Items"],
				]
			};
		});
		frm.set_query("property", function() {
			return {
				"filters": {
                    "company": frm.doc.company,
				},
			};
		});
	},
	refresh: function(frm) {
		cur_frm.add_custom_button(__("Make Invoice Schedule"), function() {
			make_lease_invoice_schedule(cur_frm);
		});
		cur_frm.add_custom_button(__("Generate Pending Invoice"), function() {
			generate_pending_invoice();
		});
		cur_frm.add_custom_button(__("Make Invoice Schedule for all Lease"), function() {
			getAllLease(cur_frm);
		});

        // Add custom buttons for Accounts Receivable and Accounting Ledger
        if (!frm.doc.__islocal) {
            // Add "Accounts Receivable" custom button
            frm.add_custom_button(
                __("Accounts Receivable"),
                function () {
                    frappe.set_route("query-report", "Accounts Receivable", {
                        party_type: "Customer",
                        party: frm.doc.lease_customer,
                    });
                },
                __("View")
            );

            // Add "Accounting Ledger" custom button
            frm.add_custom_button(
                __("Accounting Ledger"),
                function () {
                    frappe.set_route("query-report", "General Ledger", {
                        party_type: "Customer",
                        party: frm.doc.lease_customer,
                    });
                },
                __("View")
            );
        }
	},
	skip_end_date: function(frm) {
		if (frm.doc.skip_end_date) {
			frm.set_df_property('end_date', 'hidden', 1);
		}else{
			frm.set_df_property('end_date', 'hidden', 0);
		}
	},
	onload: function(frm) {
			frappe.realtime.on("lease_invoice_schedule_progress", function(data) {
			if (data.reload && data.reload === 1) {
				frm.reload_doc();
			}
			if (data.progress) {
				let progress_bar = $(cur_frm.dashboard.progress_area).find(".progress-bar");
				if (progress_bar) {
					$(progress_bar).removeClass("progress-bar-danger").addClass("progress-bar-success progress-bar-striped");
					$(progress_bar).css("width", data.progress+"%");
				}
			}
		});
	},
	validate: function(frm) {
		if (frm.doc.skip_end_date) {
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Property Management Settings"
				},
				callback: function(r) {
					if (r.message) {
						let settings = r.message;
						if (settings.make_single_invoice_on_lease && !frm.doc.end_date) {
							frm.clear_table('lease_invoice_schedule');
							$.each(frm.doc.lease_item || [], function(i, row) {
								let invoice_entry = frm.add_child('lease_invoice_schedule');
								invoice_entry.lease_item_name = row.lease_item;
								invoice_entry.rate = row.amount;
								invoice_entry.paid_by = row.paid_by;
								invoice_entry.date_to_invoice = frm.doc.start_date; // Use start date as invoice date
								invoice_entry.qty = 1;
							});
							frm.refresh_field('lease_invoice_schedule');
						}
					}
				}
			});
		}
    }
});

var make_lease_invoice_schedule = function(frm){
	var doc = frm.doc;
	frappe.call({
		method: 		"propms.property_management_solution.doctype.lease.lease.make_lease_invoice_schedule",
		args: {leasedoc: doc.name},
		callback: function(){
			cur_frm.reload_doc();
		}
	});
};

var generate_pending_invoice = function(){
	frappe.call({
		method: "propms.lease_invoice.leaseInvoiceAutoCreate",
		args: {},
		callback: function(){
			cur_frm.reload_doc();
		}
	});
};

var getAllLease = function(){
	frappe.confirm(
		'Are you sure to initiate this long process?',
		function(){
			frappe.call({
				method: "propms.property_management_solution.doctype.lease.lease.getAllLease",
				args: {},
				callback: function(){
					cur_frm.reload_doc();
				}
			});
		},
		function(){
			frappe.msgprint(__("Closed before starting long process!"));
			window.close();
		}
	)
};
