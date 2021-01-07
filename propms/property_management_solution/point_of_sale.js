/* Customized version 2019-12-30 */
/* Added cost_center field */
// POS page js.
try {
	erpnext.pos.PointOfSale = erpnext.pos.PointOfSale.extend({
	});
} catch (e) { //online POS
	class NewPOSCart extends POSCart {
		constructor(wrapper) {
			super(wrapper);
		}
		make() {
			this.make_dom();
			console.log("AakvaERP POS making cost center field")
			this.make_cost_center_field();
			this.make_customer_field();
			this.make_loyalty_points();
			this.make_numpad();
		}
		make_cost_center_field() {
			// console.log("AakvaERP POS making cost center field")
			this.cost_center_field = frappe.ui.form.make_control({
				df: {
					fieldtype: 'Link',
					label: 'Cost Center',
					fieldname: 'cost_center',
					options: 'Cost Center',
					reqd: 0,
					get_query: function () {
						return {
							filters: {
								"is_group": 0
							}
						}
					},
					onchange: () => {
						frappe.call({
							method: "propms.pos.get_pos_data",
							freeze: true,
							args: {
								'cost_center': this.cost_center_field.get_value()
							}
						}).then(r => {
							var pos_customer = "Cash Customer"
							if (r.message) {
								if (r.message.hasOwnProperty('customer')) {
									pos_customer = r.message.customer
								}
							}
							this.customer_field.set_value(pos_customer);
							this.frm.set_value('customer', pos_customer);
							//for(var i = 0; i< r.message.lease_item.length; i++ ){
							//	this.events.on_field_change(r.message.lease_item[i].lease_item);
							//}
						});
					},
				},
				parent: this.wrapper.find('.customer-field'),
				render_input: true
			});
		}
	};
	POSCart = NewPOSCart;

	class PointOfSale extends erpnext.pos.PointOfSale {
		constructor(wrapper) {
			super(wrapper);
		}

		submit_sales_invoice() {
			for (var i = 0; i < this.frm.doc.items.length; i++) {
				console.log("AakvaERP POS ", document.querySelector('input[data-fieldname="cost_center"]').value)
				this.frm.doc.items[i].cost_center = document.querySelector('input[data-fieldname="cost_center"]').value;
			}
			this.frm.doc.cost_center = document.querySelector('input[data-fieldname="cost_center"]').value;
			this.frm.savesubmit()
				.then((r) => {
					if (r && r.doc) {
						this.frm.doc.docstatus = r.doc.docstatus;
						frappe.show_alert({
							indicator: 'green',
							message: __(`Sales invoice ${r.doc.name} created succesfully`)
						});

						this.toggle_editing();
						this.set_form_action();
						this.set_primary_action_in_modal();
					}
				});
		}

	};
	erpnext.pos.PointOfSale = PointOfSale;
}
