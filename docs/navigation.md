# PropMS navigation guide and coverage

This navigation targets `version-16-hotfix` and Frappe v16.50+, checked against the v16.51.0 source. PropMS registers its own Apps-screen entry, ships a standard app Dock and one standard Sidebar for its only module, Property Management Solution. The existing business Workspaces remain the landing content. Frappe v15 branches retain their workspace-based navigation separately.

## App entry, Dock and Sidebar

Open **Apps → Property Management Solution**. The app route opens the actual Real Estate Management workspace (`/desk/real-estate-management`), not a guessed Page. The app logo is a bundled SVG, so no external image request is needed. App entry visibility respects native module visibility; document/report permissions remain separate and unchanged.

| Dock entry | Native target | Behavior |
|---|---|---|
| Property Management | Sidebar: Property Management Solution | Module shell, landing on Home / Real Estate Management |
| Facilities | Workspace: Property Facilities | Facilities landing workspace in the same module shell |
| Portfolio Dashboard | Workspace: Property Portfolio Dashboard | Existing eight cards and six charts |
| Administration | Workspace: Property Administration | Visible only when the user can access the role-restricted workspace |

The Sidebar provides Home, Facilities Operations, Leasing & Billing, Facilities Transactions, Masters, Reports, Dashboards and Administration. It is intentionally curated: full report lists and less-frequent setup masters remain in their workspace cards. Report rows use native Report targets; Frappe attaches the saved report type/reference to route them correctly. No child table or internal log is added.

Files: `propms/dock/propms/propms.json`, `propms/property_management_solution/sidebar/property_management_solution/property_management_solution.json`, `propms/hooks.py`, `propms/navigation.py`, and `propms/public/images/propms.svg`. All five workspace exports are marked `standard=1`, using the v16 field rather than the obsolete `is_standard` field.

## Navigation map

| Workspace | Purpose | Sidebar position | Visibility |
|---|---|---|---|
| Real Estate Management | Properties, tenants, leases, billing, collections and tax reports | Main entry | Underlying DocType/report permissions |
| Property Facilities | Checklists, maintenance, meters, attendance, key/tool custody and operational reports | Child of Real Estate Management | Underlying DocType/report permissions |
| Property Administration | Settings and older manually maintained registers | Child of Real Estate Management | Property Manager or System Manager; document permissions still apply |
| Property Portfolio Dashboard | Existing portfolio cards and charts | Dock and Sidebar / Dashboards | Existing workspace/card/chart permissions |
| Property MS | Compatibility entry linking to the main workspace | Hidden by default on new installs | Existing visibility is preserved by Frappe |

## Business-user walkthrough

1. Open **Real Estate Management**. Register properties and units in the Property tree, maintain tenants/owners in Customer, and open Lease to manage terms and its embedded billing schedule. Use available/booked property and active/upcoming/vacating lease queues to plan work.
2. Review lease and occupancy reports, then rent/income reports and collections/tax reports. Report Builder reports open through their native saved-report route; query/script reports use the query-report route.
3. Open **Property Facilities** for daily checklists, maintenance job cards (ERPNext Issue), material requests, meter readings and attendance. Use Key Issue & Return and Tool Issue & Return for custody transactions. Keys in Possession now filters Key Set rather than Tool Item Set.
4. Property Managers and System Managers open **Property Administration** for settings. Apartment Status and Security Deposit Details are kept as legacy registers; neither replaces the live property status or deposit reports.

## Coverage matrix

Every app-owned DocType and Report is accounted for below. Embedded child tables are reached through their parent documents, not standalone lists. Source permissions are recorded here, not changed. All included candidates use the existing module. Primary cards are unique; quick actions deliberately repeat common targets.

| Target | Type | Workspace / group or exclusion reason | Roles with read / report access in source | Source | Sidebar |
|---|---|---|---|---|---|
| Apartment Status | DocType | Included: Property Administration / Legacy Registers | System Manager, Floor Maintenance Supervisor, Maintenance Job in-charge, Maintenance Manager | `propms/property_management_solution/doctype/apartment_status/apartment_status.json` | Via workspace |
| Checklist Checkup Area | DocType | Included: Property Facilities / Masters | System Manager | `propms/property_management_solution/doctype/checklist_checkup_area/checklist_checkup_area.json` | Via workspace |
| Checklist Checkup Area Task | DocType | Embedded child table: Checklist Checkup Area | Parent document | `propms/property_management_solution/doctype/checklist_checkup_area_task/checklist_checkup_area_task.json` | Excluded (see reason) |
| Custom Error Log | DocType | Internal only: diagnostic log; use global search with System Manager | System Manager | `propms/property_management_solution/doctype/custom_error_log/custom_error_log.json` | Excluded (see reason) |
| Daily Checklist | DocType | Included: Property Facilities / Operations | System Manager, Floor Maintenance Supervisor, Maintenance Job in-charge, Maintenance Manager | `propms/property_management_solution/doctype/daily_checklist/daily_checklist.json` | Included |
| Daily Checklist Detail | DocType | Embedded child table: Daily Checklist | Parent document | `propms/property_management_solution/doctype/daily_checklist_detail/daily_checklist_detail.json` | Excluded (see reason) |
| Door | DocType | Embedded child table: no app-owned parent reference; no standalone navigation | Parent document | `propms/property_management_solution/doctype/door/door.json` | Excluded (see reason) |
| Exit | DocType | Included: Real Estate Management / Transactions | System Manager, Property Manager | `propms/property_management_solution/doctype/exit/exit.json` | Included |
| Flooring | DocType | Embedded child table: no app-owned parent reference; no standalone navigation | Parent document | `propms/property_management_solution/doctype/flooring/flooring.json` | Excluded (see reason) |
| Guard Shift | DocType | Included: Property Facilities / Masters | System Manager | `propms/property_management_solution/doctype/guard_shift/guard_shift.json` | Via workspace |
| Guard Shift Location | DocType | Embedded child table: Guard Shift | Parent document | `propms/property_management_solution/doctype/guard_shift_location/guard_shift_location.json` | Excluded (see reason) |
| Insurance | DocType | Included: Real Estate Management / Transactions | System Manager, Property Manager | `propms/property_management_solution/doctype/insurance/insurance.json` | Via workspace |
| Issue Materials Billed | DocType | Embedded child table: ERPNext Issue (custom fields) | Parent document | `propms/property_management_solution/doctype/issue_materials_billed/issue_materials_billed.json` | Excluded (see reason) |
| Issue Materials Detail | DocType | Embedded child table: ERPNext Issue (custom fields) | Parent document | `propms/property_management_solution/doctype/issue_materials_detail/issue_materials_detail.json` | Excluded (see reason) |
| Key | DocType | Embedded child table: no app-owned parent reference; no standalone navigation | Parent document | `propms/property_management_solution/doctype/key/key.json` | Excluded (see reason) |
| Key Set | DocType | Included: Property Facilities / Custody Masters | System Manager | `propms/property_management_solution/doctype/key_set/key_set.json` | Included |
| Key Set Detail | DocType | Included: Property Facilities / Custody Transactions | System Manager | `propms/property_management_solution/doctype/key_set_detail/key_set_detail.json` | Included |
| Lease | DocType | Included: Real Estate Management / Transactions | System Manager, Property Manager | `propms/property_management_solution/doctype/lease/lease.json` | Included |
| Lease Increment Rule | DocType | Embedded child table: Property | Parent document | `propms/property_management_solution/doctype/lease_increment_rule/lease_increment_rule.json` | Excluded (see reason) |
| Lease Invoice Schedule | DocType | Embedded child table: Lease | Parent document | `propms/property_management_solution/doctype/lease_invoice_schedule/lease_invoice_schedule.json` | Excluded (see reason) |
| Lease Item | DocType | Embedded child table: Lease | Parent document | `propms/property_management_solution/doctype/lease_item/lease_item.json` | Excluded (see reason) |
| Meter | DocType | Included: Property Facilities / Masters | System Manager | `propms/property_management_solution/doctype/meter/meter.json` | Included |
| Meter Reading | DocType | Included: Property Facilities / Operations | System Manager, Maintenance Manager, Floor Maintenance Supervisor | `propms/property_management_solution/doctype/meter_reading/meter_reading.json` | Included |
| Meter Reading Detail | DocType | Embedded child table: Meter Reading | Parent document | `propms/property_management_solution/doctype/meter_reading_detail/meter_reading_detail.json` | Excluded (see reason) |
| MultiSelect Item Group | DocType | Embedded child table: Property Management Settings | Parent document | `propms/property_management_solution/doctype/multiselect_item_group/multiselect_item_group.json` | Excluded (see reason) |
| Outsource Contact | DocType | Embedded child table: Outsourcing Category | Parent document | `propms/property_management_solution/doctype/outsource_contact/outsource_contact.json` | Excluded (see reason) |
| Outsourcing Attendance | DocType | Included: Property Facilities / Operations | System Manager, Maintenance Job in-charge, Floor Maintenance Supervisor | `propms/property_management_solution/doctype/outsourcing_attendance/outsourcing_attendance.json` | Included |
| Outsourcing Attendance Details | DocType | Embedded child table: Outsourcing Attendance | Parent document | `propms/property_management_solution/doctype/outsourcing_attendance_details/outsourcing_attendance_details.json` | Excluded (see reason) |
| Outsourcing Category | DocType | Included: Property Facilities / Masters | System Manager | `propms/property_management_solution/doctype/outsourcing_category/outsourcing_category.json` | Via workspace |
| Outsourcing Shift | DocType | Included: Property Facilities / Masters | System Manager | `propms/property_management_solution/doctype/outsourcing_shift/outsourcing_shift.json` | Via workspace |
| Outsourcing Shift Location | DocType | Embedded child table: Outsourcing Shift | Parent document | `propms/property_management_solution/doctype/outsourcing_shift_location/outsourcing_shift_location.json` | Excluded (see reason) |
| Paint | DocType | Embedded child table: no app-owned parent reference; no standalone navigation | Parent document | `propms/property_management_solution/doctype/paint/paint.json` | Excluded (see reason) |
| Property | DocType | Included: Real Estate Management / Masters | System Manager, Floor Maintenance Supervisor, Maintenance Job in-charge, Maintenance Manager, Property Manager | `propms/property_management_solution/doctype/property/property.json` | Included |
| Property Amenity | DocType | Embedded child table: Property | Parent document | `propms/property_management_solution/doctype/property_amenity/property_amenity.json` | Excluded (see reason) |
| Property Management Settings | DocType | Included: Property Administration / Settings | System Manager, Property Manager | `propms/property_management_solution/doctype/property_management_settings/property_management_settings.json` | Via workspace |
| Property Meter Reading | DocType | Embedded child table: Property | Parent document | `propms/property_management_solution/doctype/property_meter_reading/property_meter_reading.json` | Excluded (see reason) |
| Property Unit | DocType | Embedded child table: no app-owned parent reference; no standalone navigation | Parent document | `propms/property_management_solution/doctype/property_unit/property_unit.json` | Excluded (see reason) |
| Security Attendance | DocType | Included: Property Facilities / Operations | System Manager, Maintenance Job in-charge, Floor Maintenance Supervisor | `propms/property_management_solution/doctype/security_attendance/security_attendance.json` | Included |
| Security Attendance Details | DocType | Embedded child table: Security Attendance | Parent document | `propms/property_management_solution/doctype/security_attendance_details/security_attendance_details.json` | Excluded (see reason) |
| Security Deposit Details | DocType | Included: Property Administration / Legacy Registers | System Manager | `propms/property_management_solution/doctype/security_deposit_details/security_deposit_details.json` | Via workspace |
| Tool Item | DocType | Embedded child table: no app-owned parent reference; no standalone navigation | Parent document | `propms/property_management_solution/doctype/tool_item/tool_item.json` | Excluded (see reason) |
| Tool Item Record | DocType | Included: Property Facilities / Custody Transactions | System Manager | `propms/property_management_solution/doctype/tool_item_record/tool_item_record.json` | Included |
| Tool Item Set | DocType | Included: Property Facilities / Custody Masters | System Manager | `propms/property_management_solution/doctype/tool_item_set/tool_item_set.json` | Included |
| Unit Assets | DocType | Embedded child table: Property Unit, Property | Parent document | `propms/property_management_solution/doctype/unit_assets/unit_assets.json` | Excluded (see reason) |
| Unit Type | DocType | Included: Real Estate Management / Masters | System Manager, Property Manager | `propms/property_management_solution/doctype/unit_type/unit_type.json` | Included |
| Creditors Report | Report | Included: Real Estate Management / Collections & Tax Reports | Accounts User, Purchase User, Accounts Manager, Auditor | `propms/property_management_solution/report/creditors_report/creditors_report.json` | Via workspace |
| Customer Report | Report | Included: Real Estate Management / Lease & Occupancy Reports | System Manager, Property Manager | `propms/property_management_solution/report/customer_report/customer_report.json` | Via workspace |
| Debtors Report | Report | Included: Real Estate Management / Collections & Tax Reports | Accounts Manager, Accounts User | `propms/property_management_solution/report/debtors_report/debtors_report.json` | Included |
| Invoice Details | Report | Included: Real Estate Management / Billing & Income Reports | Accounts User, Accounts Manager | `propms/property_management_solution/report/invoice_details/invoice_details.json` | Via workspace |
| Lease Information | Report | Included: Real Estate Management / Lease & Occupancy Reports | No explicit report roles; verify effective access on site | `propms/property_management_solution/report/lease_information/lease_information.json` | Included |
| Mis-Income Break Up | Report | Included: Real Estate Management / Billing & Income Reports | Accounts User, Accounts Manager | `propms/property_management_solution/report/mis_income_break_up/mis_income_break_up.json` | Via workspace |
| Notification Report | Report | Included: Real Estate Management / Lease & Occupancy Reports | System Manager, Property Manager | `propms/property_management_solution/report/notification_report/notification_report.json` | Via workspace |
| Outsourcing Attendance | Report | Included: Property Facilities / Reports & Analytics | System Manager, Maintenance Job in-charge | `propms/property_management_solution/report/outsourcing_attendance/outsourcing_attendance.json` | Included |
| Pending Signed Agreement | Report | Included: Real Estate Management / Lease & Occupancy Reports | System Manager, Property Manager | `propms/property_management_solution/report/pending_signed_agreement/pending_signed_agreement.json` | Included |
| Property Status | Report | Included: Real Estate Management / Lease & Occupancy Reports | System Manager, Property Manager | `propms/property_management_solution/report/property_status/property_status.json` | Included |
| Property Status Report | Report | Included: Real Estate Management / Lease & Occupancy Reports | Property Manager, System Manager | `propms/property_management_solution/report/property_status_report/property_status_report.json` | Via workspace |
| Rent Invoices Details | Report | Included: Real Estate Management / Billing & Income Reports | Accounts Manager, Accounts User | `propms/property_management_solution/report/rent_invoices_details/rent_invoices_details.json` | Included |
| Rent Invoices Details USD | Report | Included: Real Estate Management / Billing & Income Reports | Accounts Manager, Accounts User | `propms/property_management_solution/report/rent_invoices_details_usd/rent_invoices_details_usd.json` | Via workspace |
| Security Attendance Report | Report | Included: Property Facilities / Reports & Analytics | System Manager, Maintenance Job in-charge | `propms/property_management_solution/report/security_attendance_report/security_attendance_report.json` | Included |
| Security Deposit | Report | Included: Real Estate Management / Collections & Tax Reports | Accounts Manager, Accounts User | `propms/property_management_solution/report/security_deposit/security_deposit.json` | Included |
| Self Consumption in Maintenance Job Card | Report | Included: Property Facilities / Reports & Analytics | Floor Maintenance Supervisor, Support Team, Maintenance Manager, Maintenance Job in-charge | `propms/property_management_solution/report/self_consumption_in_maintenance_job_card/self_consumption_in_maintenance_job_card.json` | Via workspace |
| Stamp Duty Paid by Tenant | Report | Included: Real Estate Management / Collections & Tax Reports | System Manager, Property Manager | `propms/property_management_solution/report/stamp_duty_paid_by_tenant/stamp_duty_paid_by_tenant.json` | Via workspace |
| Subscription Service Report | Report | Included: Real Estate Management / Billing & Income Reports | Accounts Manager, Accounts User | `propms/property_management_solution/report/subscription_service_report/subscription_service_report.json` | Via workspace |
| Utility Invoices | Report | Included: Real Estate Management / Billing & Income Reports | Stock Manager, Stock User, Purchase User, Accounts User | `propms/property_management_solution/report/utility_invoices/utility_invoices.json` | Via workspace |
| Withholding Tax Summary on Sales (Properties) | Report | Excluded duplicate: identical SQL query to Withholding Tax Summary on Sales for Properties; existing report retained | Accounts Manager, Accounts User | `propms/property_management_solution/report/withholding_tax_summary_on_sales_(properties)/withholding_tax_summary_on_sales_(properties).json` | Excluded (see reason) |
| Withholding Tax Summary on Sales for Properties | Report | Included: Real Estate Management / Collections & Tax Reports | Accounts Manager, Accounts User | `propms/property_management_solution/report/withholding_tax_summary_on_sales_for_properties/withholding_tax_summary_on_sales_for_properties.json` | Via workspace |

## ERPNext dependency targets

| Target | Primary placement | Reason |
|---|---|---|
| Customer, Contact, Item | Real Estate Management / Masters | Tenants, owners, contacts and billing items referenced by Lease/Property |
| Sales Order, Sales Invoice, Payment Entry | Real Estate Management / Transactions | Lease/utility billing and collections |
| Issue, Material Request | Property Facilities / Operations | Maintenance jobs and materials used by app hooks |

These are dependency-owned records, not new PropMS DocTypes. Their stock ERPNext permissions and site restrictions apply. No employee list is added: attendance already links employees within its document.

## Permissions review

- Ordinary Floor Maintenance Supervisors can read Property, Daily Checklist, Meter Reading and both attendance DocTypes. Their source roles do not grant Lease access, nor all attendance reports. Navigation does not expand their access.
- Maintenance Managers can read Property, Daily Checklist and Meter Reading; their maintenance report role remains in effect. Several facilities masters and custody records are System Manager-only in this repository. They remain unavailable unless site permissions explicitly allow them.
- Property Managers can read Property, Lease, Exit, Insurance, Unit Type and Settings. Finance reports still need their Accounts roles; property management access alone does not grant them.
- System Managers can maintain setup and legacy registers. Finance access is still subject to effective report permissions. Administrator behavior must be tested separately from a user holding System Manager.
- Administration workspace is explicitly role-restricted. No unrestricted URL shortcut to it is placed on the operator landing page. Frappe filters individual DocType/report cards and shortcuts by effective permissions. Facilities cross-link is intentional, and its destination still enforces native permissions.

## Dashboards, help and exclusions

Property Portfolio Dashboard already exists on this branch with eight Number Cards and six Dashboard Charts. It is linked from Dock and Sidebar; its data definitions are retained. There is no separate Dashboard document or custom Page to invent. Existing status shortcuts remain operational queues. This change does not alter KPI formulas, source fields, filters, currencies or chart controllers.

Child tables (including Property Amenity, Lease Item, Lease Invoice Schedule and Lease Increment Rule) are not exposed as editable masters. Custom Error Log stays internal. The nonexistent Withholding Tax Summary DocType is removed from the legacy module configuration; the actual report is linked instead. Duplicate withholding tax reports are retained on disk for compatibility, with one primary navigation link. README is the app help guide; no external-help URL is added to normal operational navigation.

## Migration, verification and rollback

These files were authored against the pinned Frappe v16.51.0 Dock, Dock Item, Sidebar, Sidebar Item and Workspace schemas/controllers. They were not exported from a live site. No fixture sync, navigation reset, document-permission rewrite or new installation hook is added. The app has one module and its Dock includes that module's authoritative Sidebar. Administration is a typed Workspace target, not an unrestricted URL; Frappe's reach checks gate it by the existing workspace roles.

Deploy the PR on `version-16-hotfix`, then run `bench --site <site> migrate` and `bench --site <site> clear-cache`. Refresh the browser and open Apps → Property Management Solution. Confirm the module, Facilities and Dashboard entries appear. For a Property Manager/System Manager, also check Administration. For an ordinary facilities user, check their allowed DocType/report entries and confirm Administration is absent. A Workspace Manager may inspect Manage Dock if an existing site/user arrangement hides an entry. This change preserves those arrangements; it does not reset them to force visibility.

Standard workspaces are imported through native v16 synchronization and customized through Frappe's separate customization layer. Review any site-specific arrangements before deployment. The hidden Property MS compatibility page retains its document identity. The bundled SVG needs the ordinary app asset symlink; if assets are unavailable after deployment, rebuild app assets through the site's normal build process.

Local validation covers JSON schemas, target existence, one Sidebar per module, complete Dock module coverage, workspace `standard` flags, report routing metadata, child-table exclusions, duplicate identities, app hook/asset paths and the app visibility function. Ruff and repository pre-commit checks are run on changed files. No live bench/site is available: migration, rendered layout, actual role visibility, icon rendering and browser navigation must still be verified on a v16.50+ development site. Do not claim these are live-site exports or runtime-tested records.

Rollback by reverting the PR and migrating. Native orphan cleanup removes app-shipped Dock/Sidebar records without their files. Site/user customization layers are not reset by this change. Workspace document identities are retained.

Upstream source references:

- https://github.com/frappe/frappe/blob/v16.51.0/frappe/desk/doctype/dock/dock.json
- https://github.com/frappe/frappe/blob/v16.51.0/frappe/desk/doctype/dock/dock.py
- https://github.com/frappe/frappe/blob/v16.51.0/frappe/desk/doctype/sidebar/sidebar.json
- https://github.com/frappe/frappe/blob/v16.51.0/frappe/desk/doctype/sidebar/sidebar.py
- https://github.com/frappe/frappe/blob/v16.51.0/frappe/desk/doctype/workspace/workspace.json
- https://github.com/frappe/frappe/blob/v16.51.0/frappe/boot.py
