import { beforeEach, describe, expect, it } from "vitest";

import { loadClientScript, readClientScript } from "./load.js";
import { installGlobals, makeForm, makeFrappe } from "./setup.js";

describe("Company form script", () => {
	let frappe;

	beforeEach(() => {
		frappe = installGlobals(makeFrappe());
		globalThis.cur_frm = makeForm();
		loadClientScript("propms/property_management_solution/company.js");
	});

	it("scopes every propms account picker to the company", () => {
		const frm = makeForm({ doctype: "Company", name: "_Test Property Company" });
		frappe._handlers.Company.setup(frm);
		const fields = Object.keys(frm._queries);
		expect(fields).toEqual([
			"security_account_code",
			"default_tax_account_head",
			"default_tax_template",
			"default_maintenance_tax_template",
		]);
		for (const field of fields) {
			expect(frm._queries[field]().filters).toEqual([["company", "=", "_Test Property Company"]]);
		}
	});
});

describe("Sales Invoice form script", () => {
	let frappe;

	beforeEach(() => {
		frappe = installGlobals(makeFrappe());
		globalThis.cur_frm = makeForm();
		loadClientScript("propms/property_management_solution/sales_invoice.js");
	});

	it("clears the customer when no cost centre is set", () => {
		const frm = makeForm({ doctype: "Sales Invoice", cost_center: "" });
		frappe._handlers["Sales Invoice"].property_name(frm, "Sales Invoice", "SI-1");
		expect(frappe.model.set_value).toHaveBeenLastCalledWith("Sales Invoice", "SI-1", "customer", "");
	});

	it("looks up the property status before the lease customer", () => {
		const frm = makeForm({ doctype: "Sales Invoice", cost_center: "Main - _TPC" });
		frappe._handlers["Sales Invoice"].property_name(frm, "Sales Invoice", "SI-1");
		expect(frappe._calls[0].args.doctype).toBe("Property");
		expect(frappe._calls[0].args.fieldname).toBe("status");
	});
});

describe("Property tree view settings", () => {
	let frappe;

	beforeEach(() => {
		frappe = installGlobals(makeFrappe());
		loadClientScript("propms/property_management_solution/doctype/property/property_tree.js");
	});

	it("points at the app's own tree endpoints", () => {
		const settings = frappe.treeview_settings.Property;
		expect(settings.get_tree_nodes).toBe(
			"propms.property_management_solution.doctype.property.property.get_children"
		);
		expect(settings.add_tree_node).toBe(
			"propms.property_management_solution.doctype.property.property.add_node"
		);
	});

	it("names the new-node field after the DocType's autoname field", () => {
		const settings = frappe.treeview_settings.Property;
		const nameField = settings.fields.find((field) => field.fieldtype === "Data");
		expect(nameField.fieldname).toBe("name1");
	});
});

describe("Issue form script", () => {
	it("formats the stock shortage message with placeholders, not interpolation", () => {
		const source = readClientScript("propms/property_management_solution/issue.js");
		expect(source).toMatch(/__\("Existing stock quantity of item \{0\} is \{1\}/);
	});
});
