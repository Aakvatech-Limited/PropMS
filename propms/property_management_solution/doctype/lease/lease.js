// Copyright (c) 2018, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lease', {
	setup: function(frm) {
		frm.add_fetch('property', 'unit_owner', 'property_owner');
		frm.set_query("sales_taxes_and_charges_template", () => ({
			filters: { company: frm.doc.company || "", disabled: 0 }
		}));
		frm.set_query("item_tax_template", "lease_item", () => ({
			filters: { company: frm.doc.company || "", disabled: 0 }
		}));
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


		frm.add_custom_button(__("Make Invoice Schedule"), function() {
			make_lease_invoice_schedule(frm);
		}, __("Actions"));
		frm.add_custom_button(__("Generate Pending Invoice"), function() {
			generate_pending_invoice(frm);
		}, __("Actions"));
		frm.add_custom_button(__("Make Invoice Schedule for all Lease"), function() {
			getAllLease(frm);
		}, __("Actions"));
        if (!frm.is_new() && (frm.doc.lease_invoice_schedule || []).some(row => row.invoice_number)) {
            frm.add_custom_button(__("Delete Selected Schedule Invoices"), function() {
                const grid = frm.fields_dict.lease_invoice_schedule.grid;
                const selected = grid.get_selected_children();
                if (!selected.length) {
                    frappe.msgprint(__("Select the schedule rows using the checkboxes in the Lease Invoice Schedule grid."));
                    return;
                }
                const invoices = [...new Set(selected.map(row => row.invoice_number).filter(Boolean))];
                if (!invoices.length) {
                    frappe.msgprint(__("The selected rows have no Sales Invoices."));
                    return;
                }
                if (frm.is_dirty()) {
                    frappe.msgprint(__("Save or discard unsaved Lease changes before deleting invoices."));
                    return;
                }
                frappe.confirm(
                    __("Permanently delete {0} Sales Invoice(s) linked to {1} selected schedule row(s)? Submitted invoices will first be cancelled. This cannot be undone.", [invoices.length, selected.length]),
                    function() {
                        frappe.call({
                            method: "propms.lease_invoice_cleanup.delete_selected_schedule_invoices",
                            args: {lease_name: frm.doc.name, schedule_rows: selected.map(row => row.name)},
                            freeze: true,
                            freeze_message: __("Cancelling and deleting selected Sales Invoices..."),
                            callback: function(r) {
                                if (!r.message) return;
                                const deleted = (r.message.results || []).filter(row => row.status === "deleted");
                                const failed = (r.message.results || []).filter(row => row.status === "failed");
                                const skipped = r.message.skipped || [];
                                const summary = [
                                    __("Deleted: {0}", [deleted.length]),
                                    __("Failed: {0}", [failed.length]),
                                    __("Rows without invoice: {0}", [skipped.length])
                                ];
                                const failures = failed.map(row => frappe.utils.escape_html(row.invoice + ": " + row.reason));
                                frappe.msgprint({
                                    title: __("Lease Invoice Deletion Results"),
                                    indicator: failed.length ? "orange" : "green",
                                    message: summary.join("<br>") + (failures.length ? "<hr>" + failures.join("<br>") : "")
                                });
                                frm.reload_doc();
                            }
                        });
                    }
                );
            }, __("Actions"));
        }


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
				let progress_bar = $(frm.dashboard.progress_area).find(".progress-bar");
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
                                `<a href="/desk/lease/${frm.doc.renewed_from}"><b>${frm.doc.renewed_from}</b></a>`,
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
                            `<a href="/desk/lease/${d.name}"><b>${d.name}</b></a>`,
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
			frm.reload_doc();
			frappe.show_alert({
				message: __("Completed making of invoice schedule."),
				indicator: "green"
			}, 5);
		}
	});
};

var generate_pending_invoice = function(frm){
	frappe.call({
		method: "propms.lease_invoice.leaseInvoiceAutoCreate",
		args: {},
		callback: function(){
			frm.reload_doc();
		}
	});
};

var getAllLease = function(frm){
	frappe.confirm(
		'Are you sure to initiate this long process?',
		function(){
			frappe.call({
				method: "propms.property_management_solution.doctype.lease.lease.getAllLease",
				args: {},
				callback: function(){
					frm.reload_doc();
				}
			});
		},
		function(){
			frappe.msgprint(__("Closed before starting long process!"));
			window.close();
		}
	)
};
