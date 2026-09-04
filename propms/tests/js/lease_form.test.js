import { beforeEach, describe, expect, it, vi } from "vitest";

import { loadClientScript } from "./load.js";
import { installGlobals, makeForm, makeFrappe } from "./setup.js";

const LEASE_JS = "propms/property_management_solution/doctype/lease/lease.js";

describe("Lease form script", () => {
	let frappe;

	beforeEach(() => {
		frappe = installGlobals(makeFrappe());
		globalThis.cur_frm = makeForm();
		loadClientScript(LEASE_JS);
	});

	it("registers handlers on the Lease form", () => {
		expect(Object.keys(frappe._handlers.Lease)).toEqual(
			expect.arrayContaining(["setup", "refresh", "custom_set_intro"])
		);
	});

	it("restricts lease items to the Lease Items group", () => {
		const frm = makeForm();
		frappe._handlers.Lease.setup(frm);
		expect(frm._queries.lease_item()).toEqual({
			filters: [["item_group", "=", "Lease Items"]],
		});
	});

	it("scopes the property picker to the lease company", () => {
		const frm = makeForm({ company: "_Test Property Company" });
		frappe._handlers.Lease.setup(frm);
		expect(frm._queries.property().filters.company).toBe("_Test Property Company");
	});

	it("adds the three Actions buttons on refresh", () => {
		const frm = makeForm();
		globalThis.cur_frm = frm;
		frappe._handlers.Lease.refresh(frm);
		const actions = frm._buttons.filter((button) => button.group === "Actions").map((b) => b.label);
		expect(actions).toEqual([
			"Make Invoice Schedule",
			"Generate Pending Invoice",
			"Make Invoice Schedule for all Lease",
		]);
	});

	it("adds the report buttons only for a saved lease", () => {
		const saved = makeForm({ __islocal: 0, lease_customer: "_Test Tenant" });
		globalThis.cur_frm = saved;
		frappe._handlers.Lease.refresh(saved);
		const views = saved._buttons.filter((button) => button.group === "View").map((b) => b.label);
		expect(views).toEqual(["Accounts Receivable", "Accounting Ledger"]);

		const unsaved = makeForm({ __islocal: 1 });
		globalThis.cur_frm = unsaved;
		frappe._handlers.Lease.refresh(unsaved);
		expect(unsaved._buttons.filter((button) => button.group === "View")).toHaveLength(0);
	});

	it("routes the Accounts Receivable button at the lease customer", () => {
		const frm = makeForm({ lease_customer: "_Test Tenant" });
		globalThis.cur_frm = frm;
		frappe._handlers.Lease.refresh(frm);
		frm._buttons.find((button) => button.label === "Accounts Receivable").action();
		expect(frappe.set_route).toHaveBeenCalledWith("query-report", "Accounts Receivable", {
			party_type: "Customer",
			party: "_Test Tenant",
		});
	});

	it("calls the schedule builder with the lease name", () => {
		const frm = makeForm({ name: "_Test Property-00001" });
		globalThis.cur_frm = frm;
		frappe._handlers.Lease.refresh(frm);
		frm._buttons.find((button) => button.label === "Make Invoice Schedule").action();
		expect(frappe._calls[0].method).toBe(
			"propms.property_management_solution.doctype.lease.lease.make_lease_invoice_schedule"
		);
		expect(frappe._calls[0].args).toEqual({ leasedoc: "_Test Property-00001" });
	});

	it("links the renewal banner at a /desk route", async () => {
		frappe.db.get_value = vi.fn(() =>
			Promise.resolve({ message: { renewal_initiated_by: "a@b.c", creation: "2026-01-01" } })
		);
		const frm = makeForm({ name: "L-2", renewed_from: "L-1" });
		globalThis.cur_frm = frm;
		frappe._handlers.Lease.custom_set_intro(frm);
		await new Promise((resolve) => setTimeout(resolve, 0));
		expect(frm._intro.message).toContain("/desk/lease/L-1");
		expect(frm._intro.message).not.toContain("/app/");
	});
});
