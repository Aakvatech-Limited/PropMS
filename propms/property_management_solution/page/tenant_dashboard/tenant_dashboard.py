import frappe
from datetime import datetime, timedelta

@frappe.whitelist()
def get_role_info():
    user = frappe.frappe.session.user
    user_doc = frappe.get_doc('User', user)
    return user_doc

@frappe.whitelist()
def balances():
    user = frappe.session.user
    user_doc = frappe.get_doc('User', user)
    
    today = datetime.today()
    first_day_next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
    last_day_next_month = (first_day_next_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    first_day_next_month = first_day_next_month.date()
    last_day_next_month = last_day_next_month.date()

    leases = frappe.db.get_all('Lease', filters={"property_user": user_doc.full_name}, fields=["name"])

    seen_lease_items_next_month = set()
    seen_lease_items_all_upcoming = set()

    total_rate_next_month = 0
    total_rate_all_upcoming = 0

    currency_next_month = None
    currency_all_upcoming = None

    for lease in leases:
        schedules_next_month = frappe.db.get_all('Lease Invoice Schedule', 
            filters={
                'parent': lease.name, 
                'date_to_invoice': ['between', [first_day_next_month, last_day_next_month]]
            },
            fields=["name", "date_to_invoice", "rate", "lease_item_name", "currency"]
        )

        for schedule in schedules_next_month:
            lease_item_name = schedule.get('lease_item_name')
            if lease_item_name not in seen_lease_items_next_month:
                total_rate_next_month += schedule.get('rate', 0)
                currency_next_month = schedule.get('currency')
                seen_lease_items_next_month.add(lease_item_name)

        schedules_all_upcoming = frappe.db.get_all('Lease Invoice Schedule', 
            filters={
                'parent': lease.name, 
                'date_to_invoice': ['>=', first_day_next_month]
            },
            fields=["name", "date_to_invoice", "rate", "lease_item_name", "currency"]
        )

        for schedule in schedules_all_upcoming:
            lease_item_name = schedule.get('lease_item_name')
            if lease_item_name not in seen_lease_items_all_upcoming:
                total_rate_all_upcoming += schedule.get('rate', 0)
                currency_all_upcoming = schedule.get('currency')
                seen_lease_items_all_upcoming.add(lease_item_name)

    return {
        "upcoming_rent": total_rate_next_month,
        "all_upcoming_rent": total_rate_all_upcoming,
        "lease_item_names": list(seen_lease_items_all_upcoming),
        "currency": currency_next_month,
        "currency2": currency_next_month
    }

@frappe.whitelist()
def payments_history():
    user = frappe.session.user
    user_doc = frappe.get_doc('User', user)

    leases = frappe.db.get_all('Lease', filters={"property_user": user_doc.full_name}, fields=["name"])

    lease_schedules = []

    for lease in leases:
        schedules = frappe.db.get_all(
            'Lease Invoice Schedule', 
            filters={
                'parent': lease.name
            },
            fields=["parent", "date_to_invoice", "rate", "lease_item_name", "currency", "invoice_number"]
        )
        
        for schedule in schedules:
            if schedule.get('invoice_number'):
                lease_schedules.append(schedule)

    return lease_schedules

@frappe.whitelist()
def create_service(service, description, service_date):
    # Throwing service to test if it's received properly
    # frappe.throw(str(service))
    
    user = frappe.session.user  # Fetch the current logged-in user
    user_doc = frappe.get_doc('User', user)
    
    # Create a new 'Service Request' doc
    sq = frappe.new_doc("Service Request")
    sq.property_user = user_doc.full_name  # Assuming this is the user name
    sq.email = user_doc.email
    sq.phone_number = user_doc.mobile_no or user_doc.phone
    sq.address = user_doc.location or ""
    
    # Assign values from the function's arguments
    sq.service = service
    sq.service_date = service_date
    sq.description = description
    
    # Insert and save the new Service Request doc
    sq.insert(ignore_permissions=True)
    sq.save()

    return 'success'
