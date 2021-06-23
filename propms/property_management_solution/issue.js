frappe.ui.form.on('Issue', {
    validate: (frm) => {
        // frm.trigger("make_row_readonly");
        if (!frm.doc.materials_required) {
            return
        }
        let to_update = [];
        frm.doc.materials_required.forEach((item, idx) => {
            var sle_qty = 0
            frappe.call({
                method: "propms.issue_hook.get_stock_availability",
                args: {
                    item_code: item.item,
                    company: frm.doc.company,
                    is_pos: item.is_pos
                },
                async: false,
                callback: function (r) {
                    if (r.message) {
                        sle_qty = r.message;
                    }
                }
            });
            if (item.material_status === "Bill" || item.material_status === "Self Consumption" && frm.doc.status === "Closed") {
                if (sle_qty < item.quantity) {
                    frappe.throw(__(`Existing stock quantity of item ${item.item} is ${sle_qty} not enough`))
                    return
                }
                let child = frm.add_child("materials_billed");
                child.item = item.item;
                child.quantity = item.quantity;
                child.uom = item.uom;
                child.rate = item.rate;
                child.amount = item.amount;
                child.is_pos = item.is_pos;
                child.material_status = item.material_status;
            }
            else {
                to_update.push(item);
            }
        });
        frm.clear_table("materials_required");
        refresh_field("materials_required");
        to_update.forEach(item => {
            let child = frm.add_child("materials_required");
            child.item = item.item;
            child.quantity = item.quantity;
            child.uom = item.uom;
            child.rate = item.rate;
            child.amount = item.amount;
            child.is_pos = item.is_pos;
            child.material_status = item.material_status;
            refresh_field("materials_required");
        });
        refresh_field("materials_required");

        if (!frm.doc.materials_billed) {
            return
        }
        const sort_list = [];
        frm.doc.materials_billed.forEach((item, idx) => {
            let item_inv_no = Number.MAX_SAFE_INTEGER;
            let item_inv_ser = "";
            if (item.sales_invoice) {
                item_inv_no = +item.sales_invoice.slice(9).replace("-", "");
                item_inv_ser = item.sales_invoice.slice(0, 8);
            }
            sort_list.push({
                idx: idx,
                no: item_inv_no,
                ser: item_inv_ser,
                pos: item.is_pos,
                name: item.name
            });
        });
        const sorted_list = sort_list.sort((a, b) => a.no - b.no);
        const pos_list = [];
        const not_list = [];
        sorted_list.forEach(i => {
            if (i.pos) { pos_list.push(i) }
            else { not_list.push(i) }
        });
        const new_sorted = [].concat(pos_list, not_list);
        new_sorted.forEach((i, idx) => {
            const row = locals["Issue Materials Billed"][i.name];
            row.idx = idx + 1;
        });
        refresh_field("materials_billed");
    },

    refresh: (frm) => {
        frm.trigger("make_pos_readonly");
    },

    onload: (frm) => {
        frm.trigger("make_pos_readonly");
    },

    make_pos_readonly: (frm) => {
        if (!frm.doc.materials_required) {
            return;
        }
        let child = frm.doc.materials_required;
        child.forEach(function (e) {
            $("[data-idx='" + e.idx + "']").find('.btn-open-row').css("pointer-events", "none");
            if (e.material_status === "Self Consumption") {
                $("[data-idx='" + e.idx + "']").find('[data-fieldname = is_pos]').css("pointer-events", "none");
            }
            else {
                $("[data-idx='" + e.idx + "']").find('[data-fieldname = is_pos]').css("pointer-events", "auto");
            }
        });
        refresh_field("materials_required");
    },

    setup: function (frm) {
        frm.set_query('person_in_charge', function () {
            return {
                filters: {
                    'department': ['like', 'Maintenance - %']
                }
            }
        });
        frm.set_query('sub_contractor_contact', function () {
            return {
                filters: {
                    'supplier_group': 'Sub-Contractor'
                }
            }
        });
        frappe.call({
            method: "propms.issue_hook.get_items_group",
            async: false,
            callback: function (r) {
                if (r.message) {
                    let maintenance_item_group = r.message;
                    frm.fields_dict["materials_required"].grid.get_field("item").get_query = function (doc, cdt, cdn) {
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
    property_name: function (frm, cdt, cdn) {
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
                callback: function (r, rt) {
                    if (r.message) {
                        if (r.message.status.toLowerCase() == 'on lease' || r.message.status.toLowerCase() == 'off lease in 3 months') {
                            frappe.call({
                                method: 'frappe.client.get_value',
                                args: {
                                    doctype: 'Lease',
                                    fieldname: ['name', 'customer'],
                                    filters: {
                                        property: frm.doc.property_name,
                                        start_date: ["<=", frappe.datetime.nowdate()],
                                        end_date: [">=", frappe.datetime.nowdate()]
                                    },
                                },
                                async: false,
                                callback: function (r, rt) {
                                    if (r.message) {
                                        frm.set_value("customer", r.message.customer);
                                        refresh_field("customer")
                                    }
                                }
                            });
                        } else {
                            frappe.db.get_value("Property", frm.doc.property_name, "unit_owner", (r) => {
                                frm.set_value("customer", r.unit_owner);
                            });
                        }
                    }
                }
            });
        }
    },
});

frappe.ui.form.on("Issue Materials Detail", "quantity", function (frm, cdt, cdn) {
    var item_row = locals[cdt][cdn];
    item_row.amount = item_row.rate * item_row.quantity;
    refresh_field("materials_required");
});


frappe.ui.form.on("Issue Materials Detail", "rate", function (frm, cdt, cdn) {
    var item_row = locals[cdt][cdn];
    item_row.amount = item_row.rate * item_row.quantity;
    refresh_field("materials_required");
});


frappe.ui.form.on("Issue Materials Detail", "material_status", function (frm, cdt, cdn) {
    var item_row = locals[cdt][cdn];
    var is_pos = $("[data-idx='" + item_row.idx + "']").find('[data-fieldname = is_pos]')

    if (item_row.material_status === "Self Consumption") {
        is_pos.css("pointer-events", "none");
        item_row.is_pos = 0;

    } else {
        is_pos.css("pointer-events", "auto");
    }
    refresh_field("materials_required");
});


frappe.ui.form.on("Issue Materials Detail", "item", function (frm, cdt, cdn) {
    var item_row = locals[cdt][cdn];
    if (!item_row.item) {
        return;
    }
    frappe.call({
        method: "propms.issue_hook.get_item_rate",
        args: {
            item: item_row.item,
            customer: frm.doc.customer,
        },
        async: false,
        callback: function (r) {
            if (r.message) {
                item_row.rate = r.message;
                item_row.amount = item_row.rate * item_row.quantity;
                refresh_field("materials_required");
            }
        }
    });
});
