import { beforeEach, describe, expect, it, vi } from "vitest";

import { loadClientScript } from "./load.js";
import { installGlobals, makeFrappe } from "./setup.js";

const POS_JS = "propms/property_management_solution/point_of_sale.js";

function makePosClasses() {
	class ItemCart {
		constructor() {
			this.$customer_section = { append: vi.fn(), find: vi.fn(() => ({})) };
			this.customer_field = { set_value: vi.fn() };
			this.frm = { doc: { items: [{}, {}] }, set_value: vi.fn() };
			this.events = { get_frm: () => this.frm };
		}

		make_customer_selector() {
			this.customer_selector_called = true;
		}
	}
	class Controller {
		constructor() {
			this.frm = { doc: { items: [{}, {}] }, is_dirty: () => false };
			this.checked_out = false;
		}

		async save_and_checkout() {
			this.checked_out = true;
		}
	}
	return { ItemCart, Controller };
}

describe("Point of Sale cost centre patch", () => {
	let frappe;
	let ItemCart;
	let Controller;

	beforeEach(() => {
		frappe = installGlobals(makeFrappe());
		({ ItemCart, Controller } = makePosClasses());
		globalThis.erpnext.PointOfSale = { ItemCart, Controller };
		loadClientScript(POS_JS);
	});

	it("waits for the point-of-sale bundle before patching", () => {
		expect(frappe._required).toContain("point-of-sale.bundle.js");
	});

	it("keeps the stock customer selector working", () => {
		const cart = new ItemCart();
		cart.make_customer_selector();
		expect(cart.customer_selector_called).toBe(true);
	});

	it("adds a non-group Cost Center control to the cart", () => {
		const cart = new ItemCart();
		cart.make_customer_selector();
		const control = frappe.ui.form.make_control.mock.calls[0][0];
		expect(control.df.fieldtype).toBe("Link");
		expect(control.df.options).toBe("Cost Center");
		expect(control.df.get_query()).toEqual({ filters: { is_group: 0 } });
	});

	it("stamps the chosen cost centre on the invoice and every item", () => {
		const cart = new ItemCart();
		cart.make_customer_selector();
		cart.propms_apply_cost_center("Main - _TPC");
		expect(cart.frm.doc.cost_center).toBe("Main - _TPC");
		expect(cart.frm.doc.items.every((item) => item.cost_center === "Main - _TPC")).toBe(true);
	});

	it("looks the customer up from the property behind the cost centre", async () => {
		frappe.call = vi.fn(() => Promise.resolve({ message: { customer: "_Test Tenant" } }));
		const cart = new ItemCart();
		cart.make_customer_selector();
		cart.propms_apply_cost_center("Main - _TPC");
		await new Promise((resolve) => setTimeout(resolve, 0));
		expect(frappe.call.mock.calls[0][0].method).toBe("propms.pos.get_pos_data");
		expect(cart.frm.set_value).toHaveBeenCalledWith("customer", "_Test Tenant");
	});

	it("falls back to the cash customer when no lease is found", async () => {
		frappe.call = vi.fn(() => Promise.resolve({ message: null }));
		const cart = new ItemCart();
		cart.make_customer_selector();
		cart.propms_apply_cost_center("Main - _TPC");
		await new Promise((resolve) => setTimeout(resolve, 0));
		expect(cart.frm.set_value).toHaveBeenCalledWith("customer", "Cash Customer");
	});

	it("re-stamps the cost centre at checkout and still checks out", async () => {
		const controller = new Controller();
		controller.cart = { cost_center_field: { get_value: () => "Main - _TPC" } };
		await controller.save_and_checkout();
		expect(controller.frm.doc.cost_center).toBe("Main - _TPC");
		expect(controller.checked_out).toBe(true);
	});

	it("is applied only once", () => {
		loadClientScript(POS_JS);
		const cart = new ItemCart();
		cart.make_customer_selector();
		expect(frappe.ui.form.make_control).toHaveBeenCalledTimes(1);
	});
});
