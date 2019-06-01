// Copyright (c) 2018, Aakvatech and contributors
// For license information, please see license.txt

cur_frm.add_fetch('shift_name', 'outsourcing_category', 'outsourcing_category_name');

frappe.ui.form.on('Outsourcing Attendance', 'shift_name', function(frm, cdt, cdn) {
    var doc = locals[cdt][cdn];
    if (doc.shift_name) {
        frappe.call({
            method: "frappe.client.get",
            args: {
                name: doc.shift_name,
                doctype: "Outsourcing Shift"
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
});

cur_frm.fields_dict['attendance_details'].grid.get_field('person_name').get_query = function(doc, cdt, cdn) {
    var child = locals[cdt][cdn];
    return {
        filters: [
            ['Outsource Contact', 'parent', '=', cur_frm.doc.outsourcing_category_name ],
            ['Outsource Contact', 'status', '=', 'Active' ]
        ]
    }
};

frappe.ui.form.on('Outsourcing Attendance Details', {
	person_name:function(frm,cdt,cdn){
		var row=locals[cdt][cdn];
		var doc=locals['Outsourcing Attendance'][row.parent];
		for(var item in doc.attendance_details){
			if(doc.attendance_details[item].person_name!="" && doc.attendance_details[item].person_name==row.person_name){
				if(doc.attendance_details[item].name!=row.name){
					frappe.model.set_value(cdt,cdn,"person_name","");
					frappe.throw("Person already selected, please select a different person.");
				}
			}
		}
	}
});
