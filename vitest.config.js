import { defineConfig } from "vitest/config";

export default defineConfig({
	test: {
		environment: "jsdom",
		include: ["propms/tests/js/**/*.test.js"],
		setupFiles: ["propms/tests/js/setup.js"],
		coverage: {
			provider: "v8",
			include: ["propms/**/*.js"],
			exclude: ["propms/tests/js/**"],
			reporter: ["text", "json-summary"],
		},
	},
});
