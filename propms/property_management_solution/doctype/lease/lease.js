// Copyright (c) 2018, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lease', {
	refresh: function(frm) {
		cur_frm.add_custom_button(__("Make Invoice Schedule"), function() {
			make_lease_invoice_schedule(cur_frm);
		});

	}
});

var make_lease_invoice_schedule = function(frm){
	var doc = frm.doc;
	frappe.call({
		method: 		"propms.property_management_solution.doctype.lease.lease.make_lease_invoice_schedule",
		args: {leasedoc: doc.name},
		callback: function(){
			//cur_frm.reload_doc();
		}
	});
};