// Copyright (c) 2018, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on("Key Set Detail", {
    setup(frm) {
        frm.add_fetch("key_set", "set_name", "set_name");
        frm.set_query("key_set", () => ({filters: {status: "In", disabled: 0}}));
    },
    onload(frm) {
        if (frm.doc.returned) {
            frm.set_df_property("returned", "read_only", 1);
        }
    },
    returned(frm) {
        if (frm.doc.returned) {
            frm.set_value("return_date_and_time", frappe.datetime.now_datetime());
            frm.set_df_property("returned", "read_only", 1);
        } else {
            frm.set_value("return_date_and_time", "");
        }
    }
});
