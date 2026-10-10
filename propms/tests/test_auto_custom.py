import frappe
from frappe.tests import IntegrationTestCase, UnitTestCase
from frappe.utils import add_days, nowdate

from propms.auto_custom import (
	changeStatusKeyset,
	diff_month,
	get_active_meter_from_property,
	get_cost_center,
	get_item_details,
	get_latest_active_lease,
	get_previous_meter_reading,
	getDateDiff,
	getMonthADD,
	getNumberOfDays,
	statusChangeAfterLeaseExpire,
	statusChangeBeforeLeaseExpire,
	update_property_status,
	validateSalesInvoiceItemDuplication,
)
from propms.tests.utils import create_customer, create_item, create_lease, create_property


class TestDateHelpers(UnitTestCase):
	def test_get_month_add(self):
		self.assertEqual(str(getMonthADD("2026-01-31", 1)), "2026-02-28")

	def test_get_date_diff(self):
		self.assertEqual(getDateDiff("2026-01-10", "2026-01-01"), 9)

	def test_get_number_of_days(self):
		self.assertEqual(getNumberOfDays("2026-02-05"), 28)

	def test_diff_month(self):
		from datetime import datetime

		self.assertEqual(diff_month(datetime(2026, 4, 10), datetime(2026, 1, 10)), 3)

	def test_get_item_details_shape(self):
		rows = get_item_details("Water", 12, "2026-01-01", "2026-01-31")
		self.assertEqual(rows[0]["item_code"], "Water")
		self.assertEqual(rows[0]["qty"], 12)


class TestSalesInvoiceDuplication(IntegrationTestCase):
	def test_duplicate_item_rejected(self):
		doc = frappe.get_doc(
			{
				"doctype": "Sales Order",
				"items": [{"item_code": "A", "name": "row1"}, {"item_code": "A", "name": "row2"}],
			}
		)
		with self.assertRaises(frappe.ValidationError):
			validateSalesInvoiceItemDuplication(doc, "validate")

	def test_distinct_items_pass(self):
		doc = frappe.get_doc(
			{
				"doctype": "Sales Order",
				"items": [{"item_code": "A", "name": "row1"}, {"item_code": "B", "name": "row2"}],
			}
		)
		validateSalesInvoiceItemDuplication(doc, "validate")


class TestLeaseLookups(IntegrationTestCase):
	def test_latest_active_lease(self):
		name = create_property("_Test Lookup Property")
		lease = create_lease(name)
		self.assertEqual(get_latest_active_lease(name), lease.name)

	def test_latest_active_lease_without_lease(self):
		name = create_property("_Test Empty Lookup Property")
		self.assertEqual(get_latest_active_lease(name), "")

	def test_get_cost_center(self):
		name = create_property("_Test Cost Centre Lookup Property")
		self.assertEqual(get_cost_center(name), frappe.db.get_value("Property", name, "cost_center"))


class TestPropertyStatusSchedulers(IntegrationTestCase):
	def test_status_change_before_lease_expire(self):
		name = create_property("_Test Expiry Soon Property")
		create_lease(name, end_date=add_days(nowdate(), 30))
		frappe.db.set_value("Property", name, "status", "On Lease")
		statusChangeBeforeLeaseExpire()
		self.assertEqual(frappe.db.get_value("Property", name, "status"), "Off Lease in 3 Months")

	def test_status_change_after_lease_expire(self):
		name = create_property("_Test Vacated Property")
		create_lease(name, start_date=add_days(nowdate(), -60), end_date=add_days(nowdate(), -1))
		frappe.db.set_value("Property", name, "status", "On Lease")
		statusChangeAfterLeaseExpire()
		self.assertEqual(frappe.db.get_value("Property", name, "status"), "Available")

	def test_update_property_status_marks_leased_property(self):
		name = create_property("_Test Occupied Property")
		lease = create_lease(name, start_date=add_days(nowdate(), -1))
		frappe.db.set_value("Lease", lease.name, "lease_status", "Active")
		frappe.db.set_value("Property", name, "status", "Available")
		update_property_status()
		self.assertEqual(frappe.db.get_value("Property", name, "status"), "On Lease")


class TestKeySet(IntegrationTestCase):
	def make_key_set(self):
		doc = frappe.get_doc(
			{"doctype": "Key Set", "set_name": "_Test Keys", "shelf_no": "S1", "location_no": "L1"}
		)
		doc.insert(ignore_permissions=True)
		return doc

	def test_keyset_status_follows_detail(self):
		key_set = self.make_key_set()
		detail = frappe.get_doc(
			{
				"doctype": "Key Set Detail",
				"key_set": key_set.name,
				"staff_type": "Others",
				"taken_by": "_Test Guard",
				"reason_for_key_taken": "Inspection",
				"returned": 0,
			}
		)
		detail.insert(ignore_permissions=True)
		changeStatusKeyset(detail, "on_change")
		self.assertEqual(frappe.db.get_value("Key Set", key_set.name, "status"), "Out")

		detail.returned = 1
		changeStatusKeyset(detail, "on_change")
		self.assertEqual(frappe.db.get_value("Key Set", key_set.name, "status"), "In")


class TestMeterReading(IntegrationTestCase):
	def make_meter(self, property_name, meter_number="_Test Meter 1"):
		item = create_item("_Test Water", is_stock_item=0)
		meter = frappe.get_doc(
			{"doctype": "Meter", "meter_number": meter_number, "meter_type": item, "status": "Active"}
		)
		meter.insert(ignore_permissions=True)
		prop = frappe.get_doc("Property", property_name)
		prop.append(
			"property_meter_reading",
			{
				"meter_number": meter.name,
				"meter_type": item,
				"installation_date": add_days(nowdate(), -30),
				"initial_meter_reading": 100,
				"invoice_customer": create_customer(),
				"status": "Active",
			},
		)
		prop.save(ignore_permissions=True)
		return meter, item

	def test_active_meter_lookup(self):
		name = create_property("_Test Meter Property")
		meter, item = self.make_meter(name)
		self.assertEqual(get_active_meter_from_property(name, item), meter.name)

	def test_previous_reading_falls_back_to_initial(self):
		name = create_property("_Test Initial Meter Property")
		meter, item = self.make_meter(name, "_Test Meter 2")
		reading = get_previous_meter_reading(meter.name, name, item)
		self.assertEqual(reading["previous_reading"], 100)

	def test_previous_reading_without_meter_returns_zero(self):
		name = create_property("_Test No Meter Property")
		self.assertEqual(get_previous_meter_reading("_Nope", name, "_Nope"), 0)
