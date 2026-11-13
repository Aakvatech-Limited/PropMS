// Copyright (c) 2021, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tool Item Record", {
    setup(frm) {
        frm.add_fetch("tool_item_set", "set_name", "set_name");
        frm.set_query("tool_item_set", () => ({filters: {status: "In"}}));
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
