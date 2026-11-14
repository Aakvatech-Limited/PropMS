frappe.ui.form.on('Journal Entry Account', {
	property_name: function(frm, cdt, cdn) {
		if (!frm.doc.property_name || !frm.doc.cost_center) return;
		frappe.call({
			method: "propms.property_status_utils.get_current_property_lease",
			args: {property_name: frm.doc.property_name},
			callback: function(r) {
				// Never auto-assign tenants for facility-management-only properties.
				if (r.message && r.message.customer) {
					frappe.model.set_value(cdt, cdn, "party", r.message.customer);
				}
			}
		});
	}
});
