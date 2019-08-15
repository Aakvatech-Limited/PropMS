// Copyright (c) 2019, Aakvatech and contributors
// For license information, please see license.txt
frappe.ui.form.on("Meter Reading", "onload", function(frm) {
	frm.set_query("meter_type", function() {
		return {
			"filters": [
				["Item", "reading_required", "=", "1"]
			]
		}
	});
});
frappe.ui.form.on('Meter Reading Detail', {
	property: function(frm, cdt, cdn) {
		var doc = locals[cdt][cdn]
		console.log(doc.property)
		console.log(cur_frm.doc.meter_type)
		if (doc.property && cur_frm.doc.meter_type) {
			frappe.call({
				method: "propms.auto_custom.get_active_meter_from_property",
				args: {
					'property_id': doc.property,
					'meter_type': cur_frm.doc.meter_type
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, "meter_number", r.message)
					} else {
						frappe.model.set_value(cdt, cdn, "property", "")
						frappe.model.set_value(cdt, cdn, "meter_number", "")
						frappe.model.set_value(cdt, cdn, "previous_meter_reading", 0)
						frappe.throw(_("Meter Does Not Exist For This Type"))
					}
				}
			})
		}
	},
	meter_number: function(frm, cdt, cdn) {
		var doc = locals[cdt][cdn]
		if (doc.meter_number && doc.property && cur_frm.doc.meter_type) {
			frappe.call({
				method: "propms.auto_custom.get_previous_meter_reading",
				args: {
					'meter_number': doc.meter_number,
					'property_id': doc.property,
					'meter_type': cur_frm.doc.meter_type
				},
				callback: function(r) {
					if (r.message) {
						if (r.message["reading_date"]) {
							frappe.model.set_value(cdt, cdn, "previous_reading_date", r.message["reading_date"])
						}
						if (r.message["previous_reading"]) {
							frappe.model.set_value(cdt, cdn, "previous_meter_reading", r.message["previous_reading"])
						}
					}
				}

			})
		}
	},
	current_meter_reading: function(frm, cdt, cdn) {
		var doc = locals[cdt][cdn]
		if (parseFloat(doc.current_meter_reading) <= parseFloat(doc.previous_meter_reading)) {
			frappe.model.set_value(cdt, cdn, "current_meter_reading", '')
			frappe.throw("Current Meter Reading Must Be Greater Than Previous Reading")
		}
		// frappe.msgprint("Current meter reading value is: " + String(doc.current_meter_reading))
		if (doc.current_meter_reading) {
			console.log(parseFloat(doc.current_meter_reading) - parseFloat(doc.previous_meter_reading))
			frappe.model.set_value(cdt, cdn, "reading_difference", parseFloat(doc.current_meter_reading) - parseFloat(doc.previous_meter_reading))
		}
	}
})

cur_frm.fields_dict['meter_reading_detail'].grid.get_field('property').get_query = function(doc, cdt, cdn) {
	return {
		filters:[
			['Property Meter Reading', 'meter_type', '=', cur_frm.doc.meter_type]

		]
	}
}
