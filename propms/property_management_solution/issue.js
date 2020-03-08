frappe.ui.form.on('Issue', {
    onload: (frm)=> {
        frm.trigger("make_row_readonly");
    },
    refresh: (frm)=> {
        frm.trigger("make_row_readonly");
    },
    make_row_readonly:(frm)=> {
         // make row read only after invoiced
         let child = frm.doc.materials_required;
         child.forEach(function(e){
             if (e.invoiced === 1){
                 $("[data-idx='"+e.idx+"']").css("pointer-events","none");
                 refresh_field("materials_required")
             }
         });
    },
    setup: function(frm) {
        frm.set_query('person_in_charge', function() {
            return {
                filters: {
                    'department': ['like', 'Maintenance - %']
                }
            }
        });
        frm.set_query('sub_contractor_contact', function() {
            return {
                filters: {
                    'supplier_group': 'Sub-Contractor'
                }
            }
        });
        frappe.call({
            method: "propms.issue_hook.get_items_group",
            async: false,
            callback: function(r) {
                if (r.message){
                    let maintenance_item_group = r.message;
                    frm.fields_dict["materials_required"].grid.get_field("item").get_query = function(doc, cdt, cdn) {
                        return {
                            filters: [
                                ["Item", "item_group", "in", maintenance_item_group],
                                
                            ]
                        }
                    }
                }
            }
        });
    },
    property_name: function(frm, cdt, cdn) {
        // frappe.msgprint(__("Testing"))
        frappe.model.set_value(cdt, cdn, 'customer', '');
        if (frm.doc.property_name) {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Property',
                    fieldname: 'status',
                    filters: {
                        name: frm.doc.property_name
                    },
                },
                async: false,
                callback: function(r, rt) {
                    if (r.message) {
                        if (r.message.status == 'On lease' || r.message.status == 'Off Lease in 3 Months') {
                            frappe.call({
                                method: 'frappe.client.get_value',
                                args: {
                                    doctype: 'Lease',
                                    fieldname: 'customer',
                                    filters: {
                                        property: frm.doc.property_name
                                    },
                                },
                                async: false,
                                callback: function(r, rt) {
                                    if (r.message) {
                                        frappe.model.set_value(cdt, cdn, 'customer', r.message.customer);
                                    }
                                }
                            });
                        }
                    }
                }
            });
        }
    },
});

frappe.ui.form.on("Issue Materials Detail", "quantity", function(frm, cdt, cdn) {
    var item_row = locals[cdt][cdn];
        item_row.amount = item_row.rate * item_row.quantity;
        refresh_field("materials_required");
});


frappe.ui.form.on("Issue Materials Detail", "rate", function(frm, cdt, cdn) {
    var item_row = locals[cdt][cdn];
        item_row.amount = item_row.rate * item_row.quantity;
        refresh_field("materials_required");
});

frappe.ui.form.on("Issue Materials Detail", "item", function(frm, cdt, cdn) {
    var item_row = locals[cdt][cdn];
    if (!item_row.item){
        return;
    }
        frappe.call({
            method: "propms.issue_hook.get_item_rate",
            args: {
                item: item_row.item,
                customer: frm.doc.customer,
            },
            async: false,
            callback: function(r) {
                if (r.message) {
                    item_row.rate = r.message;
                    item_row.amount = item_row.rate * item_row.quantity;
                    refresh_field("materials_required");
                }
            }
        });

    
});

