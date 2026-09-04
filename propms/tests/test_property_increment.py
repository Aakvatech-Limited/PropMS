import frappe
from frappe.tests import IntegrationTestCase, UnitTestCase
from frappe.utils import add_months, nowdate

from propms.property_increment import (
	_apply_increment,
	_round_amount,
	run_property_increment_engine,
	validate_property_increment_settings,
)
from propms.tests.utils import create_item, create_lease, create_property


class TestIncrementMath(UnitTestCase):
	def test_percent_increment(self):
		self.assertEqual(_apply_increment(1000, "Percent", 10, "Round", 2), 1100.0)

	def test_amount_increment(self):
		self.assertEqual(_apply_increment(1000, "Amount", 250, "Round", 2), 1250.0)

	def test_round_mode(self):
		self.assertEqual(_round_amount(10.567, "Round", 1), 10.6)

	def test_ceil_mode(self):
		self.assertEqual(_round_amount(10.51, "Ceil", 1), 10.6)

	def test_floor_mode(self):
		self.assertEqual(_round_amount(10.59, "Floor", 1), 10.5)

	def test_none_mode_keeps_precision(self):
		self.assertEqual(_round_amount(10.5678, "None", 2), 10.5678)

	def test_unknown_mode_falls_back_to_round(self):
		self.assertEqual(_round_amount(10.567, "Bogus", 1), 10.6)


class TestIncrementValidation(IntegrationTestCase):
	def make_property(self, **rule):
		item = create_item("_Test Increment Item")
		doc = frappe.get_doc("Property", create_property("_Test Increment Property"))
		doc.enable_auto_increment = 1
		doc.auto_create_lease_items_for_months = 24
		doc.increment_effective_from = nowdate()
		doc.set("lease_increment_rules", [])
		doc.append(
			"lease_increment_rules",
			{
				"lease_item": item,
				"increment_every": 1,
				"increment_uom": "Year",
				"increment_type": "Percent",
				"increment_value": 10,
				"rule_effective_from": nowdate(),
				"is_active": 1,
				**rule,
			},
		)
		return doc

	def test_valid_settings_pass(self):
		doc = self.make_property()
		validate_property_increment_settings(doc)

	def test_zero_horizon_rejected(self):
		doc = self.make_property()
		doc.auto_create_lease_items_for_months = 0
		with self.assertRaises(frappe.ValidationError):
			validate_property_increment_settings(doc)

	def test_missing_rules_rejected(self):
		doc = self.make_property()
		doc.set("lease_increment_rules", [])
		with self.assertRaises(frappe.ValidationError):
			validate_property_increment_settings(doc)

	def test_bad_uom_rejected(self):
		doc = self.make_property(increment_uom="Week")
		with self.assertRaises(frappe.ValidationError):
			validate_property_increment_settings(doc)

	def test_bad_increment_type_rejected(self):
		doc = self.make_property(increment_type="Ratio")
		with self.assertRaises(frappe.ValidationError):
			validate_property_increment_settings(doc)

	def test_zero_increment_value_rejected(self):
		doc = self.make_property(increment_value=0)
		with self.assertRaises(frappe.ValidationError):
			validate_property_increment_settings(doc)

	def test_disabled_property_skips_validation(self):
		doc = self.make_property()
		doc.enable_auto_increment = 0
		doc.auto_create_lease_items_for_months = 0
		validate_property_increment_settings(doc)


class TestIncrementEngine(IntegrationTestCase):
	def test_engine_appends_future_lease_item_version(self):
		item = create_item("_Test Engine Item")
		name = create_property("_Test Engine Property")
		prop = frappe.get_doc("Property", name)
		prop.enable_auto_increment = 1
		prop.auto_create_lease_items_for_months = 24
		prop.increment_effective_from = nowdate()
		prop.increment_rounding_mode = "Round"
		prop.increment_rounding_precision = 2
		prop.set("lease_increment_rules", [])
		prop.append(
			"lease_increment_rules",
			{
				"lease_item": item,
				"increment_every": 1,
				"increment_uom": "Year",
				"increment_type": "Percent",
				"increment_value": 10,
				"rule_effective_from": add_months(nowdate(), 12),
				"is_active": 1,
			},
		)
		prop.save()

		lease = create_lease(
			name,
			item=item,
			start_date=nowdate(),
			end_date=add_months(nowdate(), 36),
		)
		run_property_increment_engine()
		lease.reload()
		amounts = sorted(row.amount for row in lease.lease_item)
		self.assertGreater(len(lease.lease_item), 1)
		self.assertIn(1100.0, amounts)

	def test_engine_is_idempotent(self):
		run_property_increment_engine()
		before = frappe.db.count("Lease Item")
		run_property_increment_engine()
		self.assertEqual(before, frappe.db.count("Lease Item"))
