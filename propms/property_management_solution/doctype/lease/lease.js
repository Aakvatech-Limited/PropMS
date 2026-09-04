// Copyright (c) 2018, Aakvatech and contributors
// For license information, please see license.txt
cur_frm.add_fetch('property', 'unit_owner', 'property_owner');

frappe.ui.form.on('Lease', {
	setup: function(frm) {
		frm.set_query("lease_item", "lease_item", function() {
			return {
				"filters": [
                    ["item_group","=", "Lease Items"],
				]
			};
		});
		frm.set_query("property_unit", "lease_item", function() {
			return {
				"filters": {
					"company": frm.doc.company,
				}
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
		frm.trigger("custom_set_intro");


		cur_frm.add_custom_button(__("Make Invoice Schedule"), function() {
			make_lease_invoice_schedule(cur_frm);
		}, __("Actions"));
		cur_frm.add_custom_button(__("Generate Pending Invoice"), function() {
			generate_pending_invoice();
		}, __("Actions"));
		cur_frm.add_custom_button(__("Make Invoice Schedule for all Lease"), function() {
			getAllLease(cur_frm);
		}, __("Actions"));

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

            // Add "Renew Lease" custom button
            if (
                ["Active", "Expired"].includes(frm.doc.lease_status) &&
                (frappe.user.has_role("Property Manager") ||
                    frappe.user.has_role("System Manager"))
            ) {
                frm.add_custom_button(
                    __("Renew Lease"),
                    function () {
                        frappe.confirm(__("Are you sure you want to renew this lease?"), function () {
                            frappe.call({
                                method: "propms.property_management_solution.doctype.lease.lease.initiate_lease_renewal",
                                args: {
                                    source_lease_name: frm.doc.name,
                                },
                                freeze: true,
                                freeze_message: __("Initiating Lease Renewal..."),
                                callback: function (r) {
                                    if (r.message) {
                                        frappe.show_alert({
                                            message: __("Lease renewal draft created successfully: {0}", [r.message]),
                                            indicator: "green",
                                        });
                                        frappe.set_route("Form", "Lease", r.message);
                                    }
                                },
                            });
                        });
                    },
                    __("Actions")
                );
            }
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
    },

    custom_set_intro: function (frm) {
        // Show intro banner if this is a renewal lease
        if (frm.doc.renewed_from) {
            frappe.db
                .get_value("Lease", frm.doc.name, ["renewal_initiated_by", "creation"])
                .then((r) => {
                    if (r.message) {
                        let d = r.message;
                        let created_on = moment(d.creation).format("DD-MM-YYYY hh:mm A");

                        frm.set_intro(
                            __("This lease is a renewal of {0}, initiated by {1} on {2}.", [
                                `<a href="/app/lease/${frm.doc.renewed_from}"><b>${frm.doc.renewed_from}</b></a>`,
                                `<b>${d.renewal_initiated_by || __("Unknown")}</b>`,
                                `<b>${created_on}</b>`,
                            ]),
                            "blue"
                        );
                    }
                });
        }

        // Show intro banner if this lease has already been renewed
        frappe.db
            .get_value("Lease", { renewed_from: frm.doc.name }, ["name", "renewal_initiated_by", "creation"])
            .then((r) => {
                if (r && r.message && r.message.name) {
                    let d = r.message;

                    let creation_time = moment(d.creation).format("DD-MM-YYYY hh:mm A");

                    frm.set_intro(
                        __("This lease has been renewed: {0} by {1} on {2}.", [
                            `<a href="/app/lease/${d.name}"><b>${d.name}</b></a>`,
                            `<b>${d.renewal_initiated_by || ""}</b>`,
                            `<b>${creation_time}</b>`,
                        ]),
                        "green"
                    );
                }
            });
    },
});

var make_lease_invoice_schedule = function(frm){
	var doc = frm.doc;
	frappe.call({
		method: 		"propms.property_management_solution.doctype.lease.lease.make_lease_invoice_schedule",
		args: {leasedoc: doc.name},
		callback: function(){
			cur_frm.reload_doc();
			frappe.show_alert({
				message: __("Completed making of invoice schedule."),
				indicator: "green"
			}, 5);
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
