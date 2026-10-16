// Copyright (c) 2018, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Security Attendance', {
    setup(frm) {
        frm.add_fetch('guard_empid', 'employee_name', 'guard_name');
        frm.set_query('guard_empid', 'attendance_details', () => ({
            filters: [['Employee', 'department', 'like', 'Security -%']]
        }));
    }
});
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
