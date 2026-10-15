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
frappe.ui.form.on("Daily Checklist", {
    setup(frm) {
        frm.set_query("job_card", "daily_checklist_detail", () => ({
            filters: [["Issue", "docstatus", "in", [0, 1]]]
        }));
    }
});
