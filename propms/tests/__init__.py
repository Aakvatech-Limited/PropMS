import frappe

TEST_COMPANY = "_Test Property Company"
TEST_ABBR = "_TPC"


def get_test_company() -> str:
	"""Company every propms test writes against."""
	if frappe.db.exists("Company", TEST_COMPANY):
		return TEST_COMPANY
	return frappe.defaults.get_defaults().get("company") or frappe.get_all("Company", pluck="name")[0]
