// Copyright (c) 2018, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lease', {
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
