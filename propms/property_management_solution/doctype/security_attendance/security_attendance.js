// Copyright (c) 2018, Aakvatech and contributors
// For license information, please see license.txt

cur_frm.add_fetch('guard_empid', 'employee_name', 'guard_name');
frappe.ui.form.on('Security Attendance', 'shift_name', function(frm, cdt, cdn) {
    var doc = locals[cdt][cdn];
    if (doc.shift_name) {
        frappe.call({
            method: "frappe.client.get",
            args: {
                name: doc.shift_name,
                doctype: "Guard Shift"
            },
            callback(r) {
                console.log(r);
                if (r.message) {
                    for (var row in r.message.shift_location) {
                        var child = frm.add_child("attendance_details");
                        frappe.model.set_value(child.doctype, child.name, "position", r.message.shift_location[row].location_name);
                        refresh_field("attendance_details");
                    }
                }
            }
        })
    }
})
cur_frm.fields_dict['attendance_details'].grid.get_field('guard_empid').get_query = function(doc, cdt, cdn) {
    var child = locals[cdt][cdn]
    return {
        filters: [
            ['Employee', 'department', 'like', 'Security -%']
        ]
    }
};