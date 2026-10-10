import frappe
from frappe.tests import IntegrationTestCase

from propms.pos import get_pos_data
from propms.tests.utils import create_lease, create_property, get_cost_center


class TestPointOfSaleData(IntegrationTestCase):
	"""The POS cost centre control resolves its customer through this method."""

	def test_returns_the_lease_behind_a_cost_centre(self):
		name = create_property("_Test POS Property")
		lease = create_lease(name)
		result = get_pos_data(get_cost_center())
		self.assertIsNotNone(result)
		self.assertEqual(result.customer, lease.customer)

	def test_returns_none_for_an_unknown_cost_centre(self):
		self.assertIsNone(get_pos_data("_Test Missing Cost Center"))

	def test_returns_none_when_the_property_has_no_lease(self):
		frappe.db.delete("Lease")
		self.assertIsNone(get_pos_data(get_cost_center()))
