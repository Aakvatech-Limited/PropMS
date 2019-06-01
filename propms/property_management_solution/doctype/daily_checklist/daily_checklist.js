// Copyright (c) 2018, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Daily Checklist', 'area', function(frm, cdt, cdn) {
    var doc = locals[cdt][cdn];
    if (doc.area) {
        frappe.call({
            method: "frappe.client.get",
            args: {
                name: doc.area,
                doctype: "Checklist Checkup Area"
            },
            callback(r) {
                console.log(r);
                if (r.message) {
                    for (var row in r.message.task) {
                        var child = frm.add_child("daily_checklist_detail");
                        frappe.model.set_value(child.doctype, child.name, "checklist_task", r.message.task[row].task_name);
                        refresh_field("daily_checklist_detail");
                    }
                }
            }
        })
    }
})
cur_frm.fields_dict['daily_checklist_detail'].grid.get_field('job_card').get_query = function(doc, cdt, cdn) {
    var child = locals[cdt][cdn]
    return {
        filters: [
            ['Issue', 'docstatus', '=', '0'],
            ['Issue', 'docstatus', '=', '1']
        ]
    }
};