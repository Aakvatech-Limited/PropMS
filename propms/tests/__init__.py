import frappe

# Skip Frappe's global test_records dependency resolution. ERPNext's
# ItemTaxTemplate test_records reference an Account whose Company
# ("_Test Company") doesn't reliably insert in this app's test bench,
# breaking run-parallel-tests before any real assertion runs. Tests in
# this module set up their own data; declare per-class
# `test_dependencies` if a specific DocType needs seeding.
frappe.flags.skip_test_records = True
