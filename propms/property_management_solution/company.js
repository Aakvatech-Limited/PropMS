// Copyright (c) 2019, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Company', {
	setup: function(frm) {
		frm.set_query("security_account_code", function() {
			return {
				"filters": [
                    ["company","=", frm.doc.name],
				]
			};
		});
		frm.set_query("default_tax_account_head", function() {
			return {
				"filters": [
                    ["company","=", frm.doc.name],
				]
			};
		});
		frm.set_query("default_tax_template", function() {
			return {
				"filters": [
                    ["company","=", frm.doc.name],
				]
			};
		});
		frm.set_query("default_maintenance_tax_template", function() {
			return {
				"filters": [
                    ["company","=", frm.doc.name],
				]
			};
        });
	},
});
