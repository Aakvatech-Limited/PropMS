// Copyright (c) 2018, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on("Key Set Detail", "returned", function(frm) {
    if (cur_frm.doc.returned) {
	cur_frm.set_value("return_date_and_time", frappe.datetime.now_datetime());
	cur_frm.set_df_property("returned", "read_only", 1);
    } else {
        cur_frm.set_value("return_date_and_time", "");
    }
});

cur_frm.add_fetch('key_set', 'set_name', 'set_name');

frappe.ui.form.on("Key Set Detail","onload",function(){
	if (cur_frm.doc.returned) {
		cur_frm.set_df_property("returned", "read_only", 1);
	}
});

cur_frm.set_query("key_set", function() {
    return {
        filters: {
            'status': 'In',
            'disabled': 0
        }
    }
});

