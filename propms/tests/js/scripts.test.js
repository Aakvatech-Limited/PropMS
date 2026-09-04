import { beforeEach, describe, expect, it } from "vitest";

import { listClientScripts, loadClientScript, readClientScript } from "./load.js";
import { installGlobals, makeForm, makeFrappe } from "./setup.js";

const APP_SCRIPTS = listClientScripts();
// v16 evaluates report, page and chart scripts as IIFEs, so anything these
// files declare at the top level no longer reaches the global scope.
const IIFE_SCRIPTS = APP_SCRIPTS.filter(
	(file) => file.includes("/report/") || file.endsWith("point_of_sale.js")
);

describe("client script inventory", () => {
	it("finds every shipped script", () => {
		expect(APP_SCRIPTS.length).toBeGreaterThan(0);
	});
});

describe("every client script", () => {
	beforeEach(() => {
		installGlobals(makeFrappe());
	});

	it.each(APP_SCRIPTS)("%s is syntactically valid", (file) => {
		expect(() => new Function(readClientScript(file))).not.toThrow();
	});

	it.each(APP_SCRIPTS)("%s uses /desk routes, not the removed /app prefix", (file) => {
		expect(readClientScript(file)).not.toMatch(/["'`]\/app\//);
	});

	it.each(APP_SCRIPTS)("%s does not translate an interpolated template literal", (file) => {
		expect(readClientScript(file)).not.toMatch(/__\(`[^`]*\$\{/);
	});

	it.each(APP_SCRIPTS)("%s does not use the removed offline POS API", (file) => {
		const source = readClientScript(file);
		expect(source).not.toMatch(/erpnext\.pos\.PointOfSale/);
		expect(source).not.toMatch(/\bPOSCart\b/);
		expect(source).not.toMatch(/\.extend\(\{/);
	});
});

describe("scripts evaluated as IIFEs", () => {
	beforeEach(() => {
		installGlobals(makeFrappe());
	});

	it.each(IIFE_SCRIPTS)("%s runs wrapped in an IIFE without a global", (file) => {
		expect(() => loadClientScript(file)).not.toThrow();
	});
});

describe("every script executes against the desk globals", () => {
	beforeEach(() => {
		installGlobals(makeFrappe());
		// Desk form scripts run with a current form in scope; the browser sweep
		// confirmed frappe sets cur_frm before it evaluates them.
		globalThis.cur_frm = makeForm();
		globalThis.cur_frm.fields_dict = new Proxy(
			{},
			{
				get: () => ({ grid: { get_field: () => ({}) } }),
			}
		);
	});

	it.each(APP_SCRIPTS)("%s runs without throwing", (file) => {
		expect(() => loadClientScript(file)).not.toThrow();
	});
});
