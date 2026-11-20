# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt


# import frappe
from .other_methods import get_residential_columns, get_sales_invoice


def execute(filters=None):
	columns, data = [], []
	if filters.get("rental") and filters.get("year"):
		columns = get_residential_columns(filters.get("year"))
		get_sales_invoice(filters, data)

	return columns, data
