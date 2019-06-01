// Copyright (c) 2018, Aakvatech and contributors
// For license information, please see license.txt

cur_frm.set_query("guard_empid", function() {
    return {
        "filters": {
            "department": ["like", "Security - "]
        }
    }
});