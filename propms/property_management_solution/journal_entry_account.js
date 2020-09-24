frappe.ui.form.on('Journal Entry Account', {
    property_name: function(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "party", "");
	if (frm.doc.cost_center) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Property",
                    fieldname: "status",
                    filters: {
                        name: frm.doc.cost_center
                    },
                },
                callback: function(r, rt) {
                    if (r.message) {
                        if (r.message.status == "On Lease") {
                            frappe.call({
                                method: "frappe.client.get_value",
                                args: {
                                    doctype: "Lease",
                                    fieldname: "customer",
                                    filters: {
                                        property: frm.doc.cost_center
                                    },
                                },
                                callback: function(r, rt) {
                                    if (r.message) {
                                        frappe.model.set_value(cdt, cdn, "party", r.message.customer);
                                    }
                                }
                            });
                        }
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "party", "");
        }
    }
})