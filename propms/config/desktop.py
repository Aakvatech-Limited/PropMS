# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "module_name": "Property Management Solution",
            "category": "Domains",
            "color": "grey",
            "icon": "octicon octicon-home",
            "type": "module",
            "label": _("Property Management"),
            "description": "Property, lease, maintenance jobs, keys and analytics",
        },
    ]
