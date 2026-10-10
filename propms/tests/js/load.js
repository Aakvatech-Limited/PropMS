// Executes a desk client script against the mocked globals in setup.js.
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";

const APP_ROOT = path.resolve(import.meta.dirname, "../../..");

export function loadClientScript(relativePath) {
	const source = fs.readFileSync(path.join(APP_ROOT, relativePath), "utf8");
	// v16 evaluates page, report and chart scripts as IIFEs, so nothing a file
	// declares at the top level may leak into the global scope.
	const filename = path.join(APP_ROOT, relativePath);
	vm.runInThisContext(`(function () {\n${source}\n})();`, { filename });
}

export function readClientScript(relativePath) {
	return fs.readFileSync(path.join(APP_ROOT, relativePath), "utf8");
}

export function listClientScripts() {
	const found = [];
	const walk = (dir) => {
		for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
			const full = path.join(dir, entry.name);
			if (entry.isDirectory()) {
				if (entry.name === "node_modules" || entry.name === "js") continue;
				walk(full);
			} else if (entry.name.endsWith(".js")) {
				found.push(path.relative(APP_ROOT, full));
			}
		}
	};
	walk(path.join(APP_ROOT, "propms"));
	return found.sort();
}
