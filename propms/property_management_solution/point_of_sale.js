// Copyright (c) 2019, Aakvatech and contributors
// For license information, please see license.txt

// Adds a Cost Center selector to the Point of Sale cart. Picking a cost centre
// looks up the property's current lease customer and stamps the cost centre on
// the invoice and on every item before checkout.
frappe.provide("propms.point_of_sale");

propms.point_of_sale.patch_pos = function () {
	const ItemCart = erpnext.PointOfSale && erpnext.PointOfSale.ItemCart;
	const Controller = erpnext.PointOfSale && erpnext.PointOfSale.Controller;

	if (!ItemCart || !Controller || ItemCart.prototype.propms_cost_center_patched) {
		return;
	}
	ItemCart.prototype.propms_cost_center_patched = true;

	const make_customer_selector = ItemCart.prototype.make_customer_selector;

	ItemCart.prototype.make_customer_selector = function () {
		make_customer_selector.call(this);
		this.propms_make_cost_center_field();
	};

	ItemCart.prototype.propms_make_cost_center_field = function () {
		this.$customer_section.append(`<div class="propms-cost-center-field"></div>`);

		this.cost_center_field = frappe.ui.form.make_control({
			df: {
				fieldtype: "Link",
				label: __("Cost Center"),
				fieldname: "propms_cost_center",
				options: "Cost Center",
				placeholder: __("Select cost center"),
				get_query: () => ({ filters: { is_group: 0 } }),
				onchange: () => this.propms_apply_cost_center(this.cost_center_field.get_value()),
			},
			parent: this.$customer_section.find(".propms-cost-center-field"),
			render_input: true,
		});
		this.cost_center_field.toggle_label(false);
	};

	ItemCart.prototype.propms_apply_cost_center = function (cost_center) {
		const frm = this.events.get_frm();
		frm.doc.cost_center = cost_center || "";
		(frm.doc.items || []).forEach((item) => {
			item.cost_center = cost_center || "";
		});

		if (!cost_center) {
			return;
		}

		frappe.call({
			method: "propms.pos.get_pos_data",
			freeze: true,
			args: { cost_center: cost_center },
		}).then((r) => {
			const customer = (r.message && r.message.customer) || "Cash Customer";
			this.customer_field && this.customer_field.set_value(customer);
			frm.set_value("customer", customer);
		});
	};

	const save_and_checkout = Controller.prototype.save_and_checkout;

	Controller.prototype.save_and_checkout = async function () {
		const cost_center = this.cart && this.cart.cost_center_field && this.cart.cost_center_field.get_value();
		if (cost_center) {
			this.frm.doc.cost_center = cost_center;
			(this.frm.doc.items || []).forEach((item) => {
				item.cost_center = cost_center;
			});
		}
		return save_and_checkout.call(this);
	};
};

frappe.require("point-of-sale.bundle.js", () => propms.point_of_sale.patch_pos());
