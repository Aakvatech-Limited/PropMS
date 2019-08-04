// Copyright (c) 2019, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Meter', {
	onload: function(frm) {
    frm.set_query("meter_type", function(){
        return {
            "filters": [
                ["Item","reading_required", "=", "1"]
            ]
        }
    });

	}
});



