import frappe
from frappe.tests.utils import FrappeTestCase

from propms import uninstall

PROBE_ROLE = "Propms Uninstall Probe Role"
SHARED_ROLE = "Maintenance Manager"


class TestUninstallCleanup(FrappeTestCase):
	"""Cover the cleanup that runs once uninstall-app has deleted the PropMS DocTypes."""

	def tearDown(self):
		frappe.db.delete("Custom DocPerm", {"role": PROBE_ROLE})
		if frappe.db.exists("Role", PROBE_ROLE):
			frappe.delete_doc("Role", PROBE_ROLE, force=True, ignore_permissions=True)
		frappe.db.commit()

	def test_shared_roles_are_not_claimed_as_ours(self):
		"""ERPNext ships Maintenance Manager, so PropMS must not treat it as its own."""
		self.assertNotIn(SHARED_ROLE, uninstall.APP_ROLES)

	def test_app_doctypes_are_read_from_source(self):
		app_doctypes = uninstall._get_app_doctypes()
		self.assertIn("Lease", app_doctypes)
		self.assertIn("Property", app_doctypes)

	def test_role_granted_by_another_app_is_reported_as_granted(self):
		self.assertTrue(uninstall._is_role_still_granted(SHARED_ROLE))

	def test_unreferenced_role_is_disabled_not_deleted(self):
		frappe.get_doc({"doctype": "Role", "role_name": PROBE_ROLE, "desk_access": 1}).insert()
		uninstall.APP_ROLES, original = (PROBE_ROLE,), uninstall.APP_ROLES
		self.addCleanup(setattr, uninstall, "APP_ROLES", original)

		uninstall._disable_app_roles()

		self.assertTrue(frappe.db.exists("Role", PROBE_ROLE), "the Role must survive")
		self.assertEqual(frappe.db.get_value("Role", PROBE_ROLE, "disabled"), 1)

	def test_role_still_granted_stays_enabled(self):
		frappe.get_doc({"doctype": "Role", "role_name": PROBE_ROLE, "desk_access": 1}).insert()
		frappe.get_doc(
			{
				"doctype": "Custom DocPerm",
				"parent": "Property",
				"parenttype": "DocType",
				"parentfield": "permissions",
				"role": PROBE_ROLE,
				"read": 1,
			}
		).insert()
		uninstall.APP_ROLES, original = (PROBE_ROLE,), uninstall.APP_ROLES
		self.addCleanup(setattr, uninstall, "APP_ROLES", original)

		uninstall._disable_app_roles()

		self.assertEqual(frappe.db.get_value("Role", PROBE_ROLE, "disabled"), 0)

	def test_cleanup_is_skipped_while_the_doctypes_still_exist(self):
		"""PropMS is installed here, so the custom fields on core DocTypes are live config."""
		before = frappe.db.count("Custom Field", {"dt": "Issue"})

		uninstall.after_uninstall()

		self.assertEqual(frappe.db.count("Custom Field", {"dt": "Issue"}), before)
		self.assertTrue(frappe.db.exists("DocType", "Lease"))
