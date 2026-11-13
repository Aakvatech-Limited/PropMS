// Copyright (c) 2018, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on("Security Attendance Details", {
    setup(frm) {
        frm.set_query("guard_empid", () => ({
            filters: {department: ["like", "Security -%"]}
        }));
    }
});
