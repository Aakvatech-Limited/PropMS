# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from .other_methods import get_columns
from .other_methods import get_rentals
from .other_methods import get_rental_maintenance
def execute(filters=None):
	columns, data = get_columns(filters), get_rentals(filters)

	get_rental_maintenance(filters,data)

	return columns, data
