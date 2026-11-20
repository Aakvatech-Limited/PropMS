# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt


from .other_methods import get_columns, get_rental_maintenance, get_rentals


def execute(filters=None):
	columns, data = get_columns(filters), get_rentals(filters)

	get_rental_maintenance(filters, data)

	return columns, data
