import os

import frappe
from frappe.desk.query_report import run as run_query_report
from frappe.tests import IntegrationTestCase
from frappe.utils import add_months, nowdate

from propms.tests import TEST_COMPANY
from propms.tests.utils import create_lease

REPORT_ROOT = "property_management_solution/report"

DEFAULT_FILTERS = {
	"company": TEST_COMPANY,
	"from_date": add_months(nowdate(), -1),
	"to_date": nowdate(),
	"start_date": add_months(nowdate(), -1),
	"end_date": nowdate(),
	"date": nowdate(),
	"year": str(frappe.utils.now_datetime().year),
	"month": "January",
	"from": "January",
	"to": "December",
	"property_type": "%",
	"account": "%",
	"owner_type": "%",
	"service_type": "%",
	"status": "Available",
}

# These reports read Sales Invoice fields owned by csf_tz (TRA control number,
# withholding tax rate). They cannot run on a bench without that app.
CSF_TZ_DEPENDENT = {
	"Withholding Tax Summary on Sales (Properties)",
	"Withholding Tax Summary on Sales for Properties",
}


def app_reports() -> list:
	"""Every Report record shipped by propms, read from its module folder."""
	root = frappe.get_app_path("propms", REPORT_ROOT)
	names = []
	for folder in sorted(os.listdir(root)):
		json_path = os.path.join(root, folder, f"{folder}.json")
		if os.path.isfile(json_path):
			with open(json_path) as handle:
				names.append(frappe.parse_json(handle.read())["name"])
	return names


class TestReports(IntegrationTestCase):
	"""Every shipped report must load and execute on version 16."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.report_names = app_reports()

	def test_reports_are_installed(self):
		missing = [name for name in self.report_names if not frappe.db.exists("Report", name)]
		self.assertEqual(missing, [], f"reports missing from the site: {missing}")

	def test_report_modules_import(self):
		from frappe.core.doctype.report.report import get_report_module_dotted_path

		broken = []
		for name in self.report_names:
			report = frappe.get_doc("Report", name)
			if report.report_type != "Script Report":
				continue
			try:
				frappe.get_attr(get_report_module_dotted_path(report.module, name) + ".execute")
			except Exception as exc:  # noqa: BLE001
				broken.append(f"{name}: {type(exc).__name__}: {exc}")
		self.assertEqual(broken, [], f"script report modules failed to import: {broken}")

	def test_reports_execute(self):
		create_lease("_Test Report Property")
		failures = []
		skipped = []
		for name in self.report_names:
			if name in CSF_TZ_DEPENDENT and "csf_tz" not in frappe.get_installed_apps():
				skipped.append(name)
				continue
			try:
				run_query_report(name, filters=dict(DEFAULT_FILTERS), ignore_prepared_report=True)
			except Exception as exc:  # noqa: BLE001
				failures.append(f"{name}: {type(exc).__name__}: {exc}")
		self.assertEqual(failures, [], "reports failed to execute:\n" + "\n".join(failures))
		self.assertLessEqual(len(skipped), len(CSF_TZ_DEPENDENT))
