# PropMS navigation guide and coverage

This navigation is the resolved backport of PR #107 from `version-15-hotfix` to `version-15`, for Frappe/ERPNext v15. It uses native standard Workspace JSON and the v15 workspace sidebar hierarchy. The newer Frappe v16.50 Sidebar/Dock schema does not apply here. All workspaces belong to the existing Property Management Solution module; no artificial modules or app Desktop registration are added.

## Navigation map

| Workspace | Purpose | Sidebar position | Visibility |
|---|---|---|---|
| Real Estate Management | Properties, tenants, leases, billing, collections and tax reports | Main entry | Underlying DocType/report permissions |
| Property Facilities | Checklists, maintenance, meters, attendance, key/tool custody and operational reports | Child of Real Estate Management | Underlying DocType/report permissions |
| Property Administration | Settings and older manually maintained registers | Child of Real Estate Management | Property Manager or System Manager; document permissions still apply |
| Property Portfolio Dashboard | Existing portfolio KPI cards and charts; retained unchanged by this backport | Child of Real Estate Management | Existing workspace and KPI permissions |
| Property MS | Compatibility entry linking to the main workspace | Hidden by default on new installs | Existing visibility is preserved by Frappe |

## Business-user walkthrough

1. Open **Real Estate Management**. Register properties and units in the Property tree, maintain tenants/owners in Customer, and open Lease to manage terms and its embedded billing schedule. Use available/booked property and active/upcoming/vacating lease queues to plan work.
2. Review lease and occupancy reports, then rent/income reports and collections/tax reports. Report Builder reports open through their native saved-report route; query/script reports use the query-report route.
3. Open **Property Facilities** for daily checklists, maintenance job cards (ERPNext Issue), material requests, meter readings and attendance. Use Key Issue & Return and Tool Issue & Return for custody transactions. Keys in Possession now filters Key Set rather than Tool Item Set.
4. Property Managers and System Managers open **Property Administration** for settings. Apartment Status and Security Deposit Details are kept as legacy registers; neither replaces the live property status or deposit reports.

## Coverage matrix

Every app-owned DocType and Report is accounted for below. Embedded child tables are reached through their parent documents, not standalone lists. Source permissions are recorded here, not changed. All included candidates use the existing module. Primary cards are unique; quick actions deliberately repeat common targets.

| Target | Type | Workspace / group or exclusion reason | Roles with read / report access in source | Source |
|---|---|---|---|---|
| Apartment Status | DocType | Included: Property Administration / Legacy Registers | System Manager, Floor Maintenance Supervisor, Maintenance Job in-charge, Maintenance Manager | `propms/property_management_solution/doctype/apartment_status/apartment_status.json` |
| Checklist Checkup Area | DocType | Included: Property Facilities / Masters | System Manager | `propms/property_management_solution/doctype/checklist_checkup_area/checklist_checkup_area.json` |
| Checklist Checkup Area Task | DocType | Embedded child table: Checklist Checkup Area | Parent document | `propms/property_management_solution/doctype/checklist_checkup_area_task/checklist_checkup_area_task.json` |
| Custom Error Log | DocType | Internal only: diagnostic log; use global search with System Manager | System Manager | `propms/property_management_solution/doctype/custom_error_log/custom_error_log.json` |
| Daily Checklist | DocType | Included: Property Facilities / Operations | System Manager, Floor Maintenance Supervisor, Maintenance Job in-charge, Maintenance Manager | `propms/property_management_solution/doctype/daily_checklist/daily_checklist.json` |
| Daily Checklist Detail | DocType | Embedded child table: Daily Checklist | Parent document | `propms/property_management_solution/doctype/daily_checklist_detail/daily_checklist_detail.json` |
| Door | DocType | Embedded child table: no app-owned parent reference; no standalone navigation | Parent document | `propms/property_management_solution/doctype/door/door.json` |
| Exit | DocType | Included: Real Estate Management / Transactions | System Manager, Property Manager | `propms/property_management_solution/doctype/exit/exit.json` |
| Flooring | DocType | Embedded child table: no app-owned parent reference; no standalone navigation | Parent document | `propms/property_management_solution/doctype/flooring/flooring.json` |
| Guard Shift | DocType | Included: Property Facilities / Masters | System Manager | `propms/property_management_solution/doctype/guard_shift/guard_shift.json` |
| Guard Shift Location | DocType | Embedded child table: Guard Shift | Parent document | `propms/property_management_solution/doctype/guard_shift_location/guard_shift_location.json` |
| Insurance | DocType | Included: Real Estate Management / Transactions | System Manager, Property Manager | `propms/property_management_solution/doctype/insurance/insurance.json` |
| Issue Materials Billed | DocType | Embedded child table: ERPNext Issue (custom fields) | Parent document | `propms/property_management_solution/doctype/issue_materials_billed/issue_materials_billed.json` |
| Issue Materials Detail | DocType | Embedded child table: ERPNext Issue (custom fields) | Parent document | `propms/property_management_solution/doctype/issue_materials_detail/issue_materials_detail.json` |
| Key | DocType | Embedded child table: no app-owned parent reference; no standalone navigation | Parent document | `propms/property_management_solution/doctype/key/key.json` |
| Key Set | DocType | Included: Property Facilities / Custody Masters | System Manager | `propms/property_management_solution/doctype/key_set/key_set.json` |
| Key Set Detail | DocType | Included: Property Facilities / Custody Transactions | System Manager | `propms/property_management_solution/doctype/key_set_detail/key_set_detail.json` |
| Lease | DocType | Included: Real Estate Management / Transactions | System Manager, Property Manager | `propms/property_management_solution/doctype/lease/lease.json` |
| Lease Increment Rule | DocType | Embedded child table: Property | Parent document | `propms/property_management_solution/doctype/lease_increment_rule/lease_increment_rule.json` |
| Lease Invoice Schedule | DocType | Embedded child table: Lease | Parent document | `propms/property_management_solution/doctype/lease_invoice_schedule/lease_invoice_schedule.json` |
| Lease Item | DocType | Embedded child table: Lease | Parent document | `propms/property_management_solution/doctype/lease_item/lease_item.json` |
| Meter | DocType | Included: Property Facilities / Masters | System Manager | `propms/property_management_solution/doctype/meter/meter.json` |
| Meter Reading | DocType | Included: Property Facilities / Operations | System Manager, Maintenance Manager, Floor Maintenance Supervisor | `propms/property_management_solution/doctype/meter_reading/meter_reading.json` |
| Meter Reading Detail | DocType | Embedded child table: Meter Reading | Parent document | `propms/property_management_solution/doctype/meter_reading_detail/meter_reading_detail.json` |
| MultiSelect Item Group | DocType | Embedded child table: Property Management Settings | Parent document | `propms/property_management_solution/doctype/multiselect_item_group/multiselect_item_group.json` |
| Outsource Contact | DocType | Embedded child table: Outsourcing Category | Parent document | `propms/property_management_solution/doctype/outsource_contact/outsource_contact.json` |
| Outsourcing Attendance | DocType | Included: Property Facilities / Operations | System Manager, Maintenance Job in-charge, Floor Maintenance Supervisor | `propms/property_management_solution/doctype/outsourcing_attendance/outsourcing_attendance.json` |
| Outsourcing Attendance Details | DocType | Embedded child table: Outsourcing Attendance | Parent document | `propms/property_management_solution/doctype/outsourcing_attendance_details/outsourcing_attendance_details.json` |
| Outsourcing Category | DocType | Included: Property Facilities / Masters | System Manager | `propms/property_management_solution/doctype/outsourcing_category/outsourcing_category.json` |
| Outsourcing Shift | DocType | Included: Property Facilities / Masters | System Manager | `propms/property_management_solution/doctype/outsourcing_shift/outsourcing_shift.json` |
| Outsourcing Shift Location | DocType | Embedded child table: Outsourcing Shift | Parent document | `propms/property_management_solution/doctype/outsourcing_shift_location/outsourcing_shift_location.json` |
| Paint | DocType | Embedded child table: no app-owned parent reference; no standalone navigation | Parent document | `propms/property_management_solution/doctype/paint/paint.json` |
| Property | DocType | Included: Real Estate Management / Masters | System Manager, Floor Maintenance Supervisor, Maintenance Job in-charge, Maintenance Manager, Property Manager | `propms/property_management_solution/doctype/property/property.json` |
| Property Amenity | DocType | Embedded child table: Property | Parent document | `propms/property_management_solution/doctype/property_amenity/property_amenity.json` |
| Property Management Settings | DocType | Included: Property Administration / Settings | System Manager, Property Manager | `propms/property_management_solution/doctype/property_management_settings/property_management_settings.json` |
| Property Meter Reading | DocType | Embedded child table: Property | Parent document | `propms/property_management_solution/doctype/property_meter_reading/property_meter_reading.json` |
| Property Unit | DocType | Embedded child table: no app-owned parent reference; no standalone navigation | Parent document | `propms/property_management_solution/doctype/property_unit/property_unit.json` |
| Security Attendance | DocType | Included: Property Facilities / Operations | System Manager, Maintenance Job in-charge, Floor Maintenance Supervisor | `propms/property_management_solution/doctype/security_attendance/security_attendance.json` |
| Security Attendance Details | DocType | Embedded child table: Security Attendance | Parent document | `propms/property_management_solution/doctype/security_attendance_details/security_attendance_details.json` |
| Security Deposit Details | DocType | Included: Property Administration / Legacy Registers | System Manager | `propms/property_management_solution/doctype/security_deposit_details/security_deposit_details.json` |
| Tool Item | DocType | Embedded child table: no app-owned parent reference; no standalone navigation | Parent document | `propms/property_management_solution/doctype/tool_item/tool_item.json` |
| Tool Item Record | DocType | Included: Property Facilities / Custody Transactions | System Manager | `propms/property_management_solution/doctype/tool_item_record/tool_item_record.json` |
| Tool Item Set | DocType | Included: Property Facilities / Custody Masters | System Manager | `propms/property_management_solution/doctype/tool_item_set/tool_item_set.json` |
| Unit Assets | DocType | Embedded child table: Property Unit, Property | Parent document | `propms/property_management_solution/doctype/unit_assets/unit_assets.json` |
| Unit Type | DocType | Included: Real Estate Management / Masters | System Manager, Property Manager | `propms/property_management_solution/doctype/unit_type/unit_type.json` |
| Creditors Report | Report | Included: Real Estate Management / Collections & Tax Reports | Accounts User, Purchase User, Accounts Manager, Auditor | `propms/property_management_solution/report/creditors_report/creditors_report.json` |
| Customer Report | Report | Included: Real Estate Management / Lease & Occupancy Reports | System Manager, Property Manager | `propms/property_management_solution/report/customer_report/customer_report.json` |
| Debtors Report | Report | Included: Real Estate Management / Collections & Tax Reports | Accounts Manager, Accounts User | `propms/property_management_solution/report/debtors_report/debtors_report.json` |
| Invoice Details | Report | Included: Real Estate Management / Billing & Income Reports | Accounts User, Accounts Manager | `propms/property_management_solution/report/invoice_details/invoice_details.json` |
| Lease Information | Report | Included: Real Estate Management / Lease & Occupancy Reports | No explicit report roles; verify effective access on site | `propms/property_management_solution/report/lease_information/lease_information.json` |
| Mis-Income Break Up | Report | Included: Real Estate Management / Billing & Income Reports | Accounts User, Accounts Manager | `propms/property_management_solution/report/mis_income_break_up/mis_income_break_up.json` |
| Notification Report | Report | Included: Real Estate Management / Lease & Occupancy Reports | System Manager, Property Manager | `propms/property_management_solution/report/notification_report/notification_report.json` |
| Outsourcing Attendance | Report | Included: Property Facilities / Reports & Analytics | System Manager, Maintenance Job in-charge | `propms/property_management_solution/report/outsourcing_attendance/outsourcing_attendance.json` |
| Pending Signed Agreement | Report | Included: Real Estate Management / Lease & Occupancy Reports | System Manager, Property Manager | `propms/property_management_solution/report/pending_signed_agreement/pending_signed_agreement.json` |
| Property Status | Report | Included: Real Estate Management / Lease & Occupancy Reports | System Manager, Property Manager | `propms/property_management_solution/report/property_status/property_status.json` |
| Property Status Report | Report | Included: Real Estate Management / Lease & Occupancy Reports | Property Manager, System Manager | `propms/property_management_solution/report/property_status_report/property_status_report.json` |
| Rent Invoices Details | Report | Included: Real Estate Management / Billing & Income Reports | Accounts Manager, Accounts User | `propms/property_management_solution/report/rent_invoices_details/rent_invoices_details.json` |
| Rent Invoices Details USD | Report | Included: Real Estate Management / Billing & Income Reports | Accounts Manager, Accounts User | `propms/property_management_solution/report/rent_invoices_details_usd/rent_invoices_details_usd.json` |
| Security Attendance Report | Report | Included: Property Facilities / Reports & Analytics | System Manager, Maintenance Job in-charge | `propms/property_management_solution/report/security_attendance_report/security_attendance_report.json` |
| Security Deposit | Report | Included: Real Estate Management / Collections & Tax Reports | Accounts Manager, Accounts User | `propms/property_management_solution/report/security_deposit/security_deposit.json` |
| Self Consumption in Maintenance Job Card | Report | Included: Property Facilities / Reports & Analytics | Floor Maintenance Supervisor, Support Team, Maintenance Manager, Maintenance Job in-charge | `propms/property_management_solution/report/self_consumption_in_maintenance_job_card/self_consumption_in_maintenance_job_card.json` |
| Stamp Duty Paid by Tenant | Report | Included: Real Estate Management / Collections & Tax Reports | System Manager, Property Manager | `propms/property_management_solution/report/stamp_duty_paid_by_tenant/stamp_duty_paid_by_tenant.json` |
| Subscription Service Report | Report | Included: Real Estate Management / Billing & Income Reports | Accounts Manager, Accounts User | `propms/property_management_solution/report/subscription_service_report/subscription_service_report.json` |
| Utility Invoices | Report | Included: Real Estate Management / Billing & Income Reports | Stock Manager, Stock User, Purchase User, Accounts User | `propms/property_management_solution/report/utility_invoices/utility_invoices.json` |
| Withholding Tax Summary on Sales (Properties) | Report | Excluded duplicate: identical SQL query to Withholding Tax Summary on Sales for Properties; existing report retained | Accounts Manager, Accounts User | `propms/property_management_solution/report/withholding_tax_summary_on_sales_(properties)/withholding_tax_summary_on_sales_(properties).json` |
| Withholding Tax Summary on Sales for Properties | Report | Included: Real Estate Management / Collections & Tax Reports | Accounts Manager, Accounts User | `propms/property_management_solution/report/withholding_tax_summary_on_sales_for_properties/withholding_tax_summary_on_sales_for_properties.json` |

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

At the original PR #107 review, the dashboard was a separate proposal. The current `version-15` target already contains Property Portfolio Dashboard, eight Number Cards and six Dashboard Charts. The dashboard workspace is already a child of Real Estate Management and is retained unchanged by this backport. No KPI records, formulas or chart sources are added or modified here. Existing filtered status shortcuts provide operational queues, not financial metrics. No custom Page exports exist in the target.

## Backport conflict resolution

The automatic backport failed because `version-15` retains the older README while PR #107 was authored against the rewritten hotfix README. All navigation files applied cleanly. The resolution preserves the release branch's README and adds only an Application Navigation section and guide link. The guide is adjusted for the target branch and its already-present dashboard. Workflow files are unchanged.

Child tables (including Property Amenity, Lease Item, Lease Invoice Schedule and Lease Increment Rule) are not exposed as editable masters. Custom Error Log stays internal. The nonexistent Withholding Tax Summary DocType is removed from the legacy module configuration; the actual report is linked instead. Duplicate withholding tax reports are retained on disk for compatibility, with one primary navigation link. README is the app help guide; no external-help URL is added to normal operational navigation.

## Migration, verification and rollback

The JSON was authored against the actual Frappe `version-15` Workspace, Workspace Link and Workspace Shortcut schemas and the existing repository exports. It was not exported from a live development site. `public=1`, assigned module, valid saved-report routing, card counts, content block references, filters and target existence were checked statically. No installation hook, fixture sync, permission reset or navigation rewrite patch was added.

Local validation passed: complete inventory classification (45 DocTypes and 21 reports), 20 unique report links with the duplicate accounted for, shortcut filter fields and Select values, content references, nonempty card counts, dependency target existence, Python AST/module-menu execution, Ruff lint/format, `git diff --check`, and the repository's pre-commit checks on all changed files, including Frappe Semgrep Security Rules.

After deploying this branch, run `bench --site <development-site> migrate` and clear cache. Standard workspaces import through Frappe's normal synchronization. Frappe v15 compares non-DocType file timestamps: an existing workspace modified more recently than the exported standard may be preserved. Review such site-specific pages through Workspace Manager; do not force-reset customized workspaces. Frappe also preserves existing `is_hidden` values when importing: hide the old Property MS entry through Workspace Manager if it remains visible. Its existing route and document identity are retained. Private user workspaces are untouched.

There is no bench/site in the authoring environment. Migration, rendered layout, ordinary-user and manager route opening, mobile readability, icon rendering, effective report permissions, and CI must be checked on a v15 development site before production use. In particular, confirm the new child workspaces appear for facilities staff and the administration workspace is restricted; verify all Report Builder links and the filtered queues.

Rollback by reverting this commit and migrating. Restore site-customized pages from a backup if they were manually changed. Newly created Property Facilities and Property Administration records may remain after reverting exports; a Workspace Manager can hide them. Existing Property MS and Real Estate Management routes are not renamed or deleted.

Upstream source references:

- https://github.com/frappe/frappe/blob/version-15/frappe/desk/doctype/workspace/workspace.json
- https://github.com/frappe/frappe/blob/version-15/frappe/desk/doctype/workspace/workspace.py
- https://github.com/frappe/frappe/blob/version-15/frappe/desk/doctype/workspace_link/workspace_link.json
- https://github.com/frappe/frappe/blob/version-15/frappe/desk/doctype/workspace_shortcut/workspace_shortcut.json
- https://github.com/frappe/frappe/blob/version-15/frappe/desk/desktop.py
- https://github.com/frappe/frappe/blob/version-15/frappe/modules/import_file.py
