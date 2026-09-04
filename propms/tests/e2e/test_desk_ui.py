"""Browser checks over every propms desk surface.

Skipped unless PROPMS_E2E_BASE_URL is set and playwright is importable::

    PROPMS_E2E_BASE_URL=http://propms-test.localhost:8003 \
    PROPMS_E2E_PASSWORD=admin \
    python -m unittest propms.tests.e2e.test_desk_ui
"""

import os
import unittest

BASE_URL = os.environ.get("PROPMS_E2E_BASE_URL")
USER = os.environ.get("PROPMS_E2E_USER", "Administrator")
PASSWORD = os.environ.get("PROPMS_E2E_PASSWORD", "admin")

try:
	from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - playwright is an optional dev dependency
	sync_playwright = None

# Console noise that says nothing about the app: the dev server has no socket.io.
IGNORED_CONSOLE = (
	"socket.io",
	"Failed to load resource: the server responded with a status of 404",
	# Chrome refuses the unsaved-form prompt when navigating without a gesture.
	"beforeunload",
)

ROUTES = [
	("Lease list", "/desk/lease"),
	("Lease form", "/desk/lease/new"),
	("Property list", "/desk/property"),
	("Property tree", "/desk/property/view/tree"),
	("Property form", "/desk/property/new"),
	("Daily Checklist form", "/desk/daily-checklist/new"),
	("Key Set Detail form", "/desk/key-set-detail/new"),
	("Meter Reading form", "/desk/meter-reading/new"),
	("Outsourcing Attendance form", "/desk/outsourcing-attendance/new"),
	("Security Attendance form", "/desk/security-attendance/new"),
	("Security Attendance Details form", "/desk/security-attendance-details/new"),
	("Tool Item Record form", "/desk/tool-item-record/new"),
	("Property Management Settings", "/desk/property-management-settings"),
	("Maintenance Job Card form", "/desk/issue/new"),
	("Sales Invoice form", "/desk/sales-invoice/new"),
	("Company form", "/desk/company"),
	("Point of Sale", "/desk/point-of-sale"),
	("Workspace", "/desk/property-management-solution"),
	("Report: Lease Information", "/desk/query-report/Lease Information"),
	("Report: Property Status", "/desk/query-report/Property Status"),
	("Report: Rent Invoices Details", "/desk/query-report/Rent Invoices Details"),
	("Report: Subscription Service Report", "/desk/query-report/Subscription Service Report"),
	("Report: Security Deposit", "/desk/query-report/Security Deposit"),
	("Report: Mis-Income Break Up", "/desk/query-report/Mis-Income Break Up"),
	("Report: Debtors Report", "/desk/query-report/Debtors Report"),
	("Report: Invoice Details", "/desk/query-report/Invoice Details"),
	("Report: Utility Invoices", "/desk/query-report/Utility Invoices"),
]


@unittest.skipUnless(BASE_URL and sync_playwright, "PROPMS_E2E_BASE_URL or playwright is missing")
class TestDeskSurfaces(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls._playwright = sync_playwright().start()
		cls.browser = cls._playwright.chromium.launch(channel="chrome", headless=True)
		cls.page = cls.browser.new_context(viewport={"width": 1440, "height": 900}).new_page()
		cls.page.goto(f"{BASE_URL}/login", wait_until="domcontentloaded")
		cls.page.fill("#login_email", USER)
		cls.page.fill("#login_password", PASSWORD)
		cls.page.click("button.btn-login")
		cls.page.wait_for_url("**/desk**", timeout=60000)

	@classmethod
	def tearDownClass(cls):
		cls.browser.close()
		cls._playwright.stop()

	def visit(self, route: str) -> list:
		errors = []

		def on_console(message):
			if message.type == "error" and not any(noise in message.text for noise in IGNORED_CONSOLE):
				errors.append(message.text[:300])

		def on_page_error(exception):
			errors.append(f"PAGEERROR: {exception}"[:300])

		self.page.on("console", on_console)
		self.page.on("pageerror", on_page_error)
		try:
			self.page.goto(BASE_URL + route, wait_until="domcontentloaded", timeout=60000)
			self.page.wait_for_timeout(3000)
		finally:
			self.page.remove_listener("console", on_console)
			self.page.remove_listener("pageerror", on_page_error)
		return errors

	def test_every_desk_surface_loads_without_console_errors(self):
		failures = []
		for label, route in ROUTES:
			errors = self.visit(route)
			if errors:
				failures.append(f"{label} ({route}): {errors}")
		self.assertEqual(failures, [], "desk surfaces reported console errors:\n" + "\n".join(failures))
