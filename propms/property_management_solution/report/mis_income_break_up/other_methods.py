from time import strptime
import calendar
from collections import Counter
from ..invoice_details.other_methods import get_sales_invoice
from ..utility_invoices.other_methods import get_utility_sales_invoice

months = []
def get_rentals(filters):
    return_data = []
    if filters.get("year"):

        return_data.append({"income": "RENTAL INCOME"})
        sum_monthly = Counter({})
        tax = {"income":"LESS: W.TAX 10%"}
        net_rent = {"income":"NET RENT RECEIVED"}
        rentals = ["Commercial Rent", "Residential Rent"]
        for i in rentals:
            data = []
            _filters = {'rental': i, 'year': filters.get("year")}
            get_sales_invoice(_filters,data, "Mis Income Break Up", months)
            if len(data) > 0 and len( data[len(data) - 1]) > 0:
                data[len(data) - 1]["total"] = sum(data[len(data) - 1].values()) / len(data[len(data) - 1])

                sum_monthly += Counter(data[len(data) - 1])

                data[len(data) - 1]["income"] = i
                return_data.append(data[len(data) - 1])

        sum_monthly["income"] = "Total Rentals Received"

        return_data.append(sum_monthly)
        return_data.append(tax)
        return_data.append(net_rent)
        for i in sum_monthly:
            tax[i] = float(sum_monthly[i]) * float(0.10)
            net_rent[i] = sum_monthly[i] - tax[i]
    return return_data

def get_rental_maintenance(filters,return_data):

    if filters.get("year"):

        return_data.append({"income": "MAINTENANCE INCOME"})
        sum_monthly = Counter({})

        rentals = ["Commercial Rent", "Residential Rent", "Utility Charges"]
        for ii in rentals:
            data = []
            _filters = {'rental': ii, 'year': filters.get("year"), 'maintenance': 1}
            if ii == "Utility Charges":
                get_utility_sales_invoice(data, "Mis Income Break Up", months)
            else:
                get_sales_invoice(_filters,data, "Mis Income Break Up", months)
            if len(data) > 0 and len( data[len(data) - 1]) > 0:
                data[len(data) - 1]["total"] = sum(data[len(data) - 1].values()) / len(data[len(data) - 1])

                sum_monthly += Counter(data[len(data) - 1])

                data[len(data) - 1]["income"] = ii + " Maintenance" if ii != "Utility Charges" else ii
                return_data.append(data[len(data) - 1])

        sum_monthly["income"] = "Maintenance Total"

        return_data.append(sum_monthly)
        return_data.append({})
    return return_data

def get_columns(filters):
    columns = [{
        "label": "Income",
        "fieldname": "income",
        "fieldtype": "Data",
        "width": 200,
    }]
    month_int_from = int(strptime(filters.get("from"), '%B').tm_mon)
    month_int_to = int(strptime(filters.get("to"), '%B').tm_mon)

    while month_int_from <= month_int_to:
        months.append(calendar.month_name[month_int_from].lower()[:3])
        columns.append({
            "label": calendar.month_name[month_int_from],
            "fieldname": calendar.month_name[month_int_from].lower()[:3],
            "fieldtype": "Currency",
            "width": 180,
        })
        month_int_from += 1
    columns.append({
        "label": "Total",
        "fieldname": "total",
        "fieldtype": "Currency",
        "width": 180,
    })
    return columns