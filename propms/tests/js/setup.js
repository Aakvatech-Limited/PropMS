// Minimal stand-in for the desk globals every propms client script expects.
import { vi } from "vitest";

export function makeFrappe() {
	const frappe = {
		_handlers: {},
		_calls: [],
		_required: [],
		provide(path) {
			path.split(".").reduce((parent, key) => (parent[key] = parent[key] || {}), globalThis);
		},
		ui: {
			form: {
				on(doctype, handlers) {
					frappe._handlers[doctype] = Object.assign(frappe._handlers[doctype] || {}, handlers);
				},
				make_control: vi.fn((options) => ({
					df: options.df,
					value: "",
					get_value() {
						return this.value;
					},
					set_value(value) {
						this.value = value;
						return Promise.resolve();
					},
					set_focus: vi.fn(),
					toggle_label: vi.fn(),
				})),
			},
		},
		call: vi.fn((options) => {
			frappe._calls.push(options);
			if (options.callback) options.callback({ message: undefined });
			return Promise.resolve({ message: undefined });
		}),
		require: vi.fn((asset, callback) => {
			frappe._required.push(asset);
			callback && callback();
		}),
		db: {
			get_value: vi.fn(() => Promise.resolve({ message: {} })),
		},
		model: { set_value: vi.fn() },
		msgprint: vi.fn(),
		throw: vi.fn((message) => {
			throw new Error(message);
		}),
		confirm: vi.fn(),
		set_route: vi.fn(),
		show_alert: vi.fn(),
		user_defaults: {},
		utils: { escape_html: (value) => value },
		treeview_settings: {},
		query_reports: {},
		pages: {},
		dom: { freeze: vi.fn(), unfreeze: vi.fn() },
		datetime: {
			get_today: () => "2026-01-01",
			now_datetime: () => "2026-01-01 00:00:00",
			month_start: () => "2026-01-01",
			month_end: () => "2026-01-31",
			year_start: () => "2026-01-01",
			add_months: (date) => date,
		},
		defaults: {
			get_user_default: () => "",
		},
		session: { user: "Administrator" },
	};
	return frappe;
}

export function makeForm(doc = {}) {
	return {
		doc: Object.assign({ doctype: "Lease", __islocal: 0 }, doc),
		_buttons: [],
		_queries: {},
		_intro: null,
		add_custom_button(label, action, group) {
			this._buttons.push({ label, action, group });
		},
		set_query(fieldname, arg1, arg2) {
			this._queries[fieldname] = arg2 || arg1;
		},
		set_value: vi.fn(),
		set_intro(message, colour) {
			this._intro = { message, colour };
		},
		trigger(event) {
			const handler = globalThis.frappe._handlers[this.doc.doctype][event];
			return handler && handler(this);
		},
		add_child(fieldname) {
			this.doc[fieldname] = this.doc[fieldname] || [];
			const row = {};
			this.doc[fieldname].push(row);
			return row;
		},
		reload_doc: vi.fn(),
		add_fetch: vi.fn(),
		set_df_property: vi.fn(),
		fields_dict: {},
	};
}

export function installGlobals(frappe) {
	globalThis.frappe = frappe;
	globalThis.__ = (text, args) =>
		args ? args.reduce((out, value, index) => out.split(`{${index}}`).join(value), text) : text;
	globalThis.cur_frm = undefined;
	globalThis.erpnext = {
		PointOfSale: {},
		get_presentation_currency_list: () => ["TZS", "USD"],
		utils: {},
	};
	globalThis.moment = (value) => ({ format: () => String(value) });
	globalThis.locals = {};
	globalThis.refresh_field = () => {};
	globalThis.cint = (value) => parseInt(value, 10) || 0;
	globalThis.flt = (value) => parseFloat(value) || 0;
	return frappe;
}
