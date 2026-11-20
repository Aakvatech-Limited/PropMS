# Property Management Solution (PropMS)

PropMS is a Frappe and ERPNext v15 app for managing real estate and property operations from inside ERPNext. It adds property records, lease records, lease billing schedules, meter readings, maintenance material billing, security and outsourcing attendance, daily checklists, key and tool custody, print formats, and reports.

The app is published by Aakvatech and is designed for organizations that want property operations to connect directly with ERPNext customers, items, invoices, sales orders, stock, accounts, cost centers, employees, and reports.

## Business Summary

Property operations often sit between leasing, facilities, maintenance, finance, and security teams. PropMS brings those workflows into ERPNext so that property records, lease terms, utility readings, maintenance charges, attendance records, and billing documents can be managed in one system.

The repository shows a strong ERPNext dependency. PropMS uses ERPNext accounting, selling, stock, CRM/support, customer, item, company, cost center, employee, and payment records. It is best understood as an ERPNext property management extension, not a generic standalone property portal.

## Business Problems This App Solves

| Problem | How PropMS Helps |
|---|---|
| Property, lease, and billing details are kept in separate files | Creates Property, Lease, Lease Item, Lease Invoice Schedule, and related DocTypes inside ERPNext |
| Lease billing needs to follow recurring frequencies | Builds invoice schedule rows for monthly, bi-monthly, quarterly, six-month, and annual lease items |
| Lease status and property status need regular review | Includes validations and scheduled jobs for active, upcoming, expired, and off-lease statuses |
| Utility consumption must be billed from meter readings | Links meters and readings to properties, then creates Sales Invoices from submitted readings |
| Maintenance materials need billing or self-consumption tracking | Extends Issue and Material Request flows to create Sales Invoices and Stock Entries |
| Security and outsourced teams need shift attendance records | Adds Guard Shift, Security Attendance, Outsourcing Shift, and Outsourcing Attendance records |
| Managers need property and lease reports | Adds property status, lease information, invoice, debtor, creditor, attendance, tax, and security deposit reports |
| Keys and maintenance tools need custody tracking | Adds Key Set, Key Set Detail, Tool Item Set, and Tool Item Record workflows |

## Who This App Is For

- Property owners, real estate operators, apartment managers, facility managers, and service providers using ERPNext.
- Finance teams that need lease billing, security deposit references, utility invoices, and maintenance charges inside ERPNext.
- Operations teams that need daily property checklists, maintenance material tracking, key/tool custody, and attendance records.
- Implementers building an ERPNext v15 property management rollout.

## Who This App Is Not For

- Teams that do not use Frappe or ERPNext.
- Teams looking for a tenant self-service portal out of the box. No web forms or portal pages were found in this repository.
- Teams looking for payment gateway integration out of the box. Payment gateway integrations were not found in this repository.
- Teams looking for a pure accounting or pure facilities app without property and lease workflows.

## Business Benefits

| Benefit | Business Impact |
|---|---|
| Centralized property and lease records | Reduces dependence on spreadsheets and disconnected trackers |
| ERPNext billing integration | Helps finance create Sales Invoices or Sales Orders from lease schedules and utility readings |
| Property status automation | Gives teams a clearer view of available, booked, on-lease, off-lease, vacating, and renovation properties |
| Maintenance billing support | Helps convert billable maintenance materials into ERPNext Sales Invoices |
| Security and outsourcing attendance | Gives operations teams a structured record of shift attendance |
| Key and tool custody tracking | Improves accountability for physical assets issued to staff or contractors |
| Management reports | Gives managers operational and financial views without leaving ERPNext |

## Before and After

| Before PropMS | With PropMS |
|---|---|
| Lease terms and billing dates are tracked manually | Lease records store dates, parties, billing items, invoice schedules, deposits, and tax settings |
| Utility readings are collected separately from billing | Meter readings can generate linked Sales Invoices |
| Maintenance materials are difficult to reconcile | Issue records can drive Sales Invoices or Stock Entries depending on material status |
| Property availability is updated manually | Lease validation and scheduled tasks update lease and property statuses |
| Attendance for guards or outsourced staff is recorded outside ERPNext | Security and outsourcing attendance become ERPNext records with reports and print formats |
| Key/tool handover is informal | Key and tool records track in, out, lost, returned, and custody details |

## Typical Use Cases

- Register properties, units, owners, cost centers, meters, amenities, and related assets.
- Create leases with customers, lease dates, recurring billing items, security deposit data, and withholding tax details.
- Generate lease invoice schedules and convert due schedules into Sales Invoices or Sales Orders.
- Submit meter readings and generate utility invoices.
- Track maintenance job materials from Issue records and bill them or consume them internally.
- Record daily checklists for handover, takeover, and routine inspections.
- Manage security guard shifts and outsourced staff attendance.
- Track key sets and tool sets issued to staff, contractors, or security teams.
- Review property, lease, invoice, attendance, debtor, creditor, security deposit, and tax reports.

## Example Business Workflow

1. A property manager creates a Property with company, cost center, owner, unit details, amenities, meters, rent, deposit, and status.
2. The team creates a Lease for that property and customer, adds Lease Items with billing frequency, amount, currency, withholding tax, paid-by customer, and target document type.
3. PropMS generates Lease Invoice Schedule rows based on lease dates, item frequency, invoice start date, and days-to-invoice-in-advance settings.
4. A scheduled job or user action creates Sales Invoices or Sales Orders from due schedule rows.
5. Utility readings are submitted through Meter Reading records, creating Sales Invoices for measured consumption where enabled.
6. Maintenance teams record Issue materials. Billable materials can become Sales Invoices, and self-consumption materials can become Stock Entries.
7. Managers monitor lease status, property status, invoices, attendance, deposits, and tax reports from ERPNext.

## ERPNext Value Addition

PropMS adds property management workflows on top of ERPNext. Repository evidence shows integration with:

| ERPNext Area | Integration |
|---|---|
| Customer and Contact | Lease parties, property users, paid-by customers, unit owners, witnesses |
| Item and Item Group | Lease items, meter types, maintenance materials, damage/security deposit items |
| Sales Invoice | Lease invoices, utility invoices, maintenance invoices, custom lease/job-card fields |
| Sales Order | Optional lease schedule output based on Lease Item document type |
| Material Request and Stock Entry | Maintenance material issue and self-consumption handling |
| Issue | Property-linked maintenance job card behavior and material billing tables |
| Company and Cost Center | Property, invoice, tax, and reporting context |
| Payment Entry and Mode of Payment | Security deposit received and returned references |
| Journal Entry | Security deposit and account-related reporting/customization |
| Employee | Security attendance guard references |
| Supplier | Insurance provider references |

## Stand-alone Value

PropMS is not positioned as a standalone Frappe-only app in this repository. `pyproject.toml` declares both Frappe and ERPNext v15 dependencies, and the code imports ERPNext controllers and references many ERPNext DocTypes. A Frappe-only deployment should be treated as unsupported unless the maintainers confirm otherwise.

## Decision Guide

| Question | Good Fit If Yes |
|---|---|
| Do you run property operations in ERPNext or plan to? | Yes |
| Do you need lease billing connected to Sales Invoices or Sales Orders? | Yes |
| Do you track property availability, lease expiry, deposits, and utility readings? | Yes |
| Do maintenance job cards need material billing or stock consumption? | Yes |
| Do you need guard or outsourced staff attendance records? | Yes |
| Do you need a public tenant portal immediately? | No, this would need separate confirmation or customization |
| Do you need payment gateway integration immediately? | No, this would need separate confirmation or customization |

## Expected Business Outcomes

PropMS can help improve visibility across leasing, billing, maintenance, and property operations. It can reduce duplicate entry between property trackers and ERPNext, make recurring lease billing more consistent, and give managers structured reports for lease, invoice, attendance, deposit, tax, and property status review.

Outcomes depend on clean master data, agreed lease processes, correct ERPNext accounting setup, and user adoption.

## Screenshots / Visual Walkthrough

Screenshots are not included in this repository. Add screenshots before publishing if this README will be used for sales, marketplace, or client evaluation.

Suggested screenshots:

- Real Estate Management workspace
- Property form
- Lease form with Lease Item and Lease Invoice Schedule tables
- Property Management Settings
- Meter Reading form
- Issue material billing fields
- Property Status and Lease Information reports

## Demo Scenario

1. Create a company, customer, cost center, items for rent and utilities, tax templates, and property settings.
2. Create a Property with status `Available`, cost center, owner, rent, deposit, meters, and amenities.
3. Create a Lease for the property and customer with monthly rent and a utility item.
4. Generate lease invoice schedules.
5. Run lease invoice creation and confirm Sales Invoice or Sales Order output.
6. Submit a Meter Reading and confirm the linked utility invoice.
7. Record a maintenance Issue with billable materials and confirm invoice creation.
8. Review Property Status, Lease Information, Rent Invoice Details, and Debtors Report.

## Implementation Effort

| Area | Effort | Notes |
|---|---:|---|
| App installation on ERPNext v15 | Medium | Requires a working Frappe/ERPNext bench and correct branch/tag |
| Master data setup | Medium | Company, customers, contacts, items, item groups, cost centers, warehouses, tax templates, accounts, employees |
| Lease and billing configuration | Medium | Requires Property Management Settings and lease item frequencies |
| Data migration | Depends | Existing property, lease, customer, and meter data may need mapping |
| Accounting validation | High | Tax, receivable, security deposit, and cost center setup should be reviewed |
| User training | Medium | Property managers, maintenance users, finance users, and supervisors need role-specific training |
| Customization | Depends | Tenant portal, approvals, payment gateways, or extra reports are not evidenced as out-of-the-box |

## What Needs to Be Ready Before Implementation

- ERPNext v15 site with required company and accounting setup.
- Customers, contacts, items, item groups, cost centers, tax templates, warehouses, employees, suppliers, and modes of payment.
- Clear property hierarchy and unit naming rules.
- Lease billing rules, frequencies, currencies, security deposit handling, withholding tax expectations, and invoice schedule policy.
- Maintenance material billing policy, including POS versus non-POS and self-consumption handling.
- Roles and responsibilities for Property Manager, Maintenance Manager, Floor Maintenance Supervisor, Maintenance Job in-charge, and System Manager.
- Migration templates for existing properties, leases, meters, keys, tools, and attendance data if applicable.

## Risks and Considerations

- The app is tightly coupled to ERPNext v15. Confirm compatibility before installing on other major versions.
- The repository has a license mismatch: `LICENSE` says GPL, while `hooks.py` declares MIT.
- `setup.py` references `requirements.txt`, but no `requirements.txt` file was found in this checkout. `pyproject.toml` declares dependencies differently.
- Some workflows create or submit financial and stock documents. Test in a staging site before production use.
- Several notifications exist but are disabled in their JSON definitions.
- Existing README mentions creating a `Property Management Solution` domain. Confirm whether this is still required for current v15 deployments.
- Tenant portal, payment gateway integration, and third-party integrations are not evidenced in the repository and should not be promised without additional work.

## Frequently Asked Business Questions

### Do we need ERPNext?

Yes. The repository declares ERPNext v15 as a dependency and integrates with ERPNext DocTypes and controllers.

### Will this replace ERPNext?

No. It extends ERPNext for property management. ERPNext remains the accounting, billing, stock, customer, employee, and reporting foundation.

### Can it generate invoices?

Yes. The code supports Sales Invoice creation from lease invoice schedules, meter readings, and billable maintenance materials. Lease items can also target Sales Orders.

### Can managers get reports?

Yes. The repository includes reports for property status, lease information, invoices, debtors, creditors, attendance, deposits, withholding tax, subscription services, and maintenance consumption.

### Can existing spreadsheet data be migrated?

Likely, but the repository does not include migration scripts for external spreadsheets. Migration should be planned using Frappe data import or a custom migration script.

### Does it include a tenant portal?

No tenant portal implementation was found in this repository. It can be considered a customization requirement.

---

## Key Features

- Property master with tree structure, company, cost center, owner, rent, security deposit, status, amenities, assets, and meters.
- Lease records with lease parties, dates, statuses, lease items, invoice schedules, deposits, late payment interest, withholding tax, and witnesses.
- Lease invoice schedule generation and Sales Invoice or Sales Order creation.
- Daily lease status updates and property status updates for active, expired, and off-lease periods.
- Optional property-level lease increment rules for future lease item amount versions.
- Meter reading capture and utility invoice generation.
- Maintenance job card extensions on Issue, including property, customer, materials required, materials billed, Sales Invoice, POS, Stock Entry, and self-consumption behavior.
- Security and outsourcing attendance workflows with reports and print formats.
- Key and tool custody tracking.
- Workspaces for `Property MS` and `Real Estate Management`.
- Print formats for attendance, daily checklist, property tax invoice, payment entry voucher, outsourcing attendance, and security attendance.
- Custom fields and property setters created through install and migrate hooks.

## Compatibility

| Component | Evidence |
|---|---|
| Frappe | `>=15.0.0,<16.0.0` in `pyproject.toml` |
| ERPNext | `>=15.0.0,<16.0.0` in `pyproject.toml` |
| Python | `>=3.10` in `pyproject.toml` |
| App version | `15.2.1` in `propms/__init__.py` |
| Package name | `propms` |
| App title | `Property Management Solution` |

## App Mode

`ERPNext required`

This conclusion is based on `pyproject.toml`, ERPNext imports, and the app's use of ERPNext DocTypes such as Sales Invoice, Sales Order, Material Request, Stock Entry, Issue, Customer, Item, Company, Cost Center, Payment Entry, Journal Entry, Employee, Supplier, and Purchase Invoice.

## Installation

Install this app on a Frappe/ERPNext v15 bench site.

```bash
bench get-app https://github.com/aakvatech/PropMS.git --branch <v15-branch-or-tag>
bench --site your-site.local install-app propms
bench --site your-site.local migrate
```

For a local development bench:

```bash
bench new-site propms.local
bench --site propms.local install-app erpnext
bench get-app https://github.com/aakvatech/PropMS.git --branch <v15-branch-or-tag>
bench --site propms.local install-app propms
bench --site propms.local migrate
```

Replace `<v15-branch-or-tag>` with the maintained branch or tag for this repository. This checkout appears to be a v15 hotfix version, but the exact public branch name should be confirmed before publishing.

## Configuration

1. Open `Property Management Settings`.
2. Set the default company.
3. Configure security deposit item, damage charge item, and security deposit payment type.
4. Configure invoice start date.
5. Decide whether lease schedules should be generated only up to tomorrow or through the next month.
6. Decide whether Sales Orders or Sales Invoices created from leases should be auto-submitted.
7. Configure maintenance item groups, self-consumption customer, maintenance invoice submission, and stock entry submission.
8. Configure Company defaults used by the app, including default tax templates, maintenance tax template, tax account head, and security account code.
9. Create or confirm required master data: Customers, Contacts, Items, Item Groups, Cost Centers, Warehouses, Employees, Suppliers, Modes of Payment, and Tax Templates.
10. Confirm whether the ERPNext domain named `Property Management Solution` is still required for this version.

## Usage

### Property Setup

Create Property records for buildings, units, or managed spaces. Use parent properties for hierarchy, and maintain company, cost center, owner, type, rent, security deposit, status, amenities, assets, and meters.

### Lease Management

Create Lease records with property, customer, lease dates, lease status, lease items, security deposit fields, withholding tax policy, and notice periods. Lease items define billing frequency, amount, currency, paid-by customer, invoice item group, and whether the schedule creates Sales Invoices or Sales Orders.

### Lease Billing

Use the Lease form or scheduled jobs to generate Lease Invoice Schedule rows. Due schedules can be converted into Sales Invoices or Sales Orders and written back to the schedule row.

### Utility Billing

Create Meter and Meter Reading records. When Meter Reading is submitted, the app can create Sales Invoices for readings that are not marked `Do not create invoice`.

### Maintenance Billing

Use ERPNext Issue records with PropMS custom fields. Maintenance materials can be marked for billing or self-consumption. The app can create Sales Invoices, POS invoices, or Stock Entries depending on the material status and settings.

### Operations and Attendance

Use Daily Checklist, Security Attendance, and Outsourcing Attendance records for operational follow-up. Use the provided reports and print formats for review and documentation.

## Modules and DocTypes

| Area | DocTypes | Purpose |
|---|---|---|
| Property setup | Property, Property Unit, Unit Type, Apartment Status, Property Amenity, Unit Assets, Security Deposit Details | Property hierarchy, unit characteristics, assets, amenities, deposits, and status |
| Lease management | Lease, Lease Item, Lease Invoice Schedule, Lease Increment Rule, Exit | Lease lifecycle, billing items, schedules, future increments, and exits |
| Billing and utilities | Meter, Property Meter Reading, Meter Reading, Meter Reading Detail | Meter registration, reading capture, and utility invoicing |
| Maintenance operations | Daily Checklist, Daily Checklist Detail, Checklist Checkup Area, Checklist Checkup Area Task, Issue Materials Detail, Issue Materials Billed, Custom Error Log | Routine checks, issue materials, maintenance billing, and error tracking |
| Security | Guard Shift, Guard Shift Location, Security Attendance, Security Attendance Details | Guard shift setup and attendance |
| Outsourcing | Outsourcing Category, Outsource Contact, Outsourcing Shift, Outsourcing Shift Location, Outsourcing Attendance, Outsourcing Attendance Details | Outsourced workforce categories, shift setup, and attendance |
| Custody tracking | Key Set, Key, Key Set Detail, Tool Item Set, Tool Item, Tool Item Record | Keys and tools in, out, lost, returned, and assigned |
| Setup helpers | Property Management Settings, MultiSelect Item Group, Door, Flooring, Paint | App settings and child tables used by property records |

## ERPNext Integration Details

| ERPNext DocType or Area | PropMS Behavior |
|---|---|
| Sales Invoice | Lease, meter reading, and maintenance billing flows can create invoices; custom fields add lease, lease item, job card, and lease information |
| Sales Order | Lease schedules can create Sales Orders when Lease Item document type is set to Sales Order |
| Material Request | Custom `sales_invoice` field and hooks for maintenance material billing |
| Issue | Custom property, customer, contractor, material required, material billed, feedback, and defect fields |
| Stock Entry | Created for maintenance self-consumption materials when configured |
| Company | Custom fields for property management tax and security account setup |
| Item | Custom `reading_required` field and use as lease items, meter types, and maintenance materials |
| Journal Entry Account | Client script adds property status visibility through linked lease behavior |
| Payment Entry | Lease security deposit received and returned references |
| Customer and Contact | Lease customers, owners, POS customer, property user, witnesses, and contact links |
| Employee | Guard attendance details |
| Supplier | Insurance provider |
| Purchase Invoice | Used by Creditors Report |

## Custom Fields and Fixtures

Custom fields are stored as JSON under `propms/patches/custom_fields/custom_fields_json` and are applied by `propms.utils.create_custom_fields.execute` during install and migrate.

| Target | Examples |
|---|---|
| Issue | Property Name, Person in Charge, Sub Contractor, Materials Required, Materials Billed, Customer Feedback, Defect Found |
| Issue Materials Detail | Material Request link |
| Material Request | Sales Invoice link |
| Material Request Item | Material Request data field |
| Sales Invoice | Lease, Lease Item, Job Card, Lease Information section |
| Company | Default tax template, default maintenance tax template, tax account head, security account code |
| Item | Reading Required |
| Quotation | Cost Center |
| Property | Territory |

Property setters are stored under `propms/patches/property_setter/property_setter_json` and are applied by `propms.utils.create_property_setter.execute`. They adjust list views, filters, field options, field requirements, default print formats, and quick-entry behavior for ERPNext and PropMS DocTypes.

The repository does not use `fixtures` in `hooks.py`; the hook comments state that custom fields and property setters are now managed through JSON files and utility functions.

## Permissions

Roles found in DocType permissions:

- System Manager
- Property Manager
- Maintenance Manager
- Floor Maintenance Supervisor
- Maintenance Job in-charge

Property Manager has access to key property and lease setup records. Maintenance roles have access to checklists, meter readings, property visibility, and attendance records. System Manager has broad administrative access.

## Reports and Dashboards

Workspaces:

| Workspace | Purpose |
|---|---|
| Property MS | Legacy-style property workspace with masters, documents, settings, and analytics links |
| Real Estate Management | v15 workspace with property, lease, utility, key/security, outsourcing, monitoring, and report cards |

Reports included:

| Report | Type | Reference |
|---|---|---|
| Creditors Report | Query Report | Purchase Invoice |
| Customer Report | Report Builder | Lease |
| Debtors Report | Query Report | Sales Invoice |
| Invoice Details | Script Report | Sales Invoice |
| Lease Information | Query Report | Lease |
| Mis-Income Break Up | Script Report | Sales Invoice |
| Notification Report | Report Builder | Lease |
| Outsourcing Attendance | Query Report | Outsourcing Attendance |
| Pending Signed Agreement | Report Builder | Lease |
| Property Status | Query Report | Lease |
| Property Status Report | Report Builder | Lease |
| Rent Invoices Details | Script Report | Sales Invoice |
| Rent Invoices Details USD | Script Report | Sales Invoice |
| Security Attendance Report | Query Report | Security Attendance |
| Security Deposit | Query Report | Journal Entry |
| Self Consumption in Maintenance Job Card | Query Report | Issue |
| Stamp Duty Paid by Tenant | Report Builder | Lease |
| Subscription Service Report | Query Report | Sales Invoice |
| Utility Invoices | Script Report | Sales Invoice |
| Withholding Tax Summary on Sales (Properties) | Query Report | Sales Invoice |
| Withholding Tax Summary on Sales for Properties | Query Report | Sales Invoice |

## APIs

The repository exposes several whitelisted methods for form scripts and server actions. Important examples include:

| Module | Methods |
|---|---|
| `propms.auto_custom` | Lease date helpers, checklist creation, journal entry creation, meter lookup, previous reading lookup, meter invoice creation, latest active lease lookup |
| `propms.lease_invoice` | Create lease invoice or sales order, get due date, get cost center, run or enqueue lease invoice auto-create |
| `propms.lease_invoice_schedule` | Generate lease invoice schedules |
| `propms.issue_hook` | Get item rate, get configured item groups, get stock availability |
| `propms.pos` | Get POS data by cost center |
| `propms.utils.create_custom_fields` | Export selected custom fields |
| `propms.property_management_solution.doctype.lease.lease` | Get all leases and create lease invoice schedules from a lease |
| `propms.property_management_solution.doctype.property.property` | Tree add-node and get-children helpers |

Review permissions and input validation before exposing these methods broadly.

## Hooks and Events

Install and migration hooks:

- `after_install`: creates custom fields and property setters from JSON.
- `after_migrate`: re-applies custom fields and property setters from JSON.

Client scripts:

- POS page: `property_management_solution/point_of_sale.js`
- Sales Invoice: `property_management_solution/sales_invoice.js`
- Journal Entry Account: `property_management_solution/journal_entry_account.js`
- Issue: `property_management_solution/issue.js`
- Company: `property_management_solution/company.js`

Document events:

| DocType | Event | Handler |
|---|---|---|
| Issue | validate | `propms.issue_hook.validate` |
| Property | validate | `propms.property_increment.validate_property_increment_settings` |
| Material Request | validate, on_update, on_change | `propms.auto_custom.makeSalesInvoice` |
| Sales Order | validate | `propms.auto_custom.validateSalesInvoiceItemDuplication` |
| Key Set Detail | on_change | `propms.auto_custom.changeStatusKeyset` |
| Meter Reading | on_submit | `propms.auto_custom.make_invoice_meter_reading` |

## Background Jobs

Scheduled events:

| Schedule | Method | Purpose |
|---|---|---|
| Daily long | `propms.property_management_solution.doctype.lease.lease.update_lease_statuses` | Updates system-controlled lease statuses |
| Daily | `propms.auto_custom.statusChangeBeforeLeaseExpire` | Marks properties as off-lease in 3 months when applicable |
| Daily | `propms.auto_custom.statusChangeAfterLeaseExpire` | Marks properties available when no active lease remains |
| Daily | `propms.property_increment.run_property_increment_engine` | Creates future lease item versions based on property increment rules |
| Cron `00 00 * * *` | `propms.lease_invoice_schedule.make_lease_invoice_schedule` | Generates lease invoice schedule rows when settings allow it |
| Cron `00 12 * * *` | `propms.lease_invoice.enqueue_lease_invoice_auto_create` | Enqueues lease invoice creation on the long queue |

## Developer Setup

```bash
bench get-app https://github.com/aakvatech/PropMS.git --branch <v15-branch-or-tag>
bench --site your-site.local install-app propms
bench --site your-site.local migrate
```

Run tests from a bench that has ERPNext and PropMS installed:

```bash
bench --site your-site.local run-tests --app propms
```

Developer notes:

- The app package is `propms`.
- Module name is `Property Management Solution`.
- Python target is 3.10 or newer.
- Ruff configuration is present in `pyproject.toml`.
- DocType tests exist under several DocType folders, but test completeness should be reviewed before relying on them as production coverage.

## Project Structure

```text
propms/
  hooks.py
  auto_custom.py
  issue_hook.py
  lease_invoice.py
  lease_invoice_schedule.py
  property_increment.py
  utils/
    create_custom_fields.py
    create_property_setter.py
  patches/
    custom_fields/custom_fields_json/
    property_setter/property_setter_json/
  property_management_solution/
    doctype/
    report/
    workspace/
    notification/
    print_format/
```

## Migration Notes

- Custom fields and property setters are reapplied on migration through `after_migrate`.
- `patches.txt` is empty in this checkout.
- Existing production sites should test field and property setter changes in staging before migration.
- Data migration from spreadsheets or another property system is not included and should be planned separately.

## Upgrade Guide

1. Back up the site and database.
2. Pull the correct PropMS branch for your ERPNext major version.
3. Run `bench --site your-site.local migrate`.
4. Review custom fields and property setters after migration.
5. Validate lease schedules, invoice generation, meter invoice generation, and maintenance billing in staging.
6. Review scheduled jobs and background workers.

## Uninstallation

Use normal Frappe app removal only after confirming operational and accounting impact:

```bash
bench --site your-site.local uninstall-app propms
```

Custom fields, property setters, financial documents, stock documents, and property records created while using the app may remain or may require manual cleanup depending on the site's data state. Take a backup first.

## Troubleshooting

| Issue | Check |
|---|---|
| Lease schedules are not created | Confirm `Property Management Settings`, invoice start date, lease status, lease dates, and scheduler settings |
| Invoices are not created | Confirm schedule rows are due, customer exists, company tax template is set, and background workers are running |
| Meter invoices are not created | Confirm Meter Reading is submitted, `Do not create invoice` is not checked, and the property has an active lease/customer |
| Maintenance invoices fail | Confirm company maintenance tax template, item rates, customer, cost center, warehouse, and POS profile settings |
| Property status looks incorrect | Review active leases, lease dates, skip end date, scheduled jobs, and manual statuses |
| Install fails through `setup.py` | This checkout lacks `requirements.txt`; prefer v15 bench/pyproject installation and confirm packaging with maintainers |

## Security

- No guest web endpoints were found during repository review.
- Several whitelisted methods exist and should be reviewed for permission expectations.
- Financial and stock document creation should be tested with role permissions and accounting controls.
- Role access is defined in DocType JSON files and should be aligned with each organization's internal controls.
- Custom fields and property setters modify standard ERPNext behavior, so review them before production rollout.

## Repository Evidence Reviewed

| File or Area | Evidence Found |
|---|---|
| `pyproject.toml` | App name, Python requirement, Frappe and ERPNext v15 dependencies |
| `setup.py` | Package metadata and Aakvatech author details; references missing `requirements.txt` |
| `propms/__init__.py` | App version `15.2.1` |
| `propms/hooks.py` | App metadata, install hooks, document events, scheduler events, client scripts |
| `propms/modules.txt` | Module name `Property Management Solution` |
| `propms/config/property_management_solution.py` | Desk module links for documents, masters, settings, and analytics |
| `propms/property_management_solution/workspace/` | Property MS and Real Estate Management workspaces |
| `propms/property_management_solution/doctype/` | Property, Lease, Meter Reading, Daily Checklist, Attendance, Key, Tool, Settings, and related DocTypes |
| `propms/property_management_solution/report/` | Query, script, and report-builder reports |
| `propms/property_management_solution/print_format/` | Standard print formats for attendance, checklist, payment voucher, tax invoice, and security attendance |
| `propms/property_management_solution/notification/` | Email notification definitions for checklist and attendance documents, disabled by default |
| `propms/patches/custom_fields/` | ERPNext custom fields for Issue, Sales Invoice, Company, Material Request, Item, Quotation, and Property |
| `propms/patches/property_setter/` | ERPNext and PropMS field/property customizations |
| `propms/auto_custom.py` | Maintenance invoice, meter invoice, lease helper, journal entry, key status, and property status helper methods |
| `propms/lease_invoice.py` | Lease invoice or sales order creation and background enqueueing |
| `propms/lease_invoice_schedule.py` | Scheduled lease invoice schedule generation |
| `propms/property_increment.py` | Property-level lease increment validation and scheduled engine |
| `propms/issue_hook.py` | Issue material billing, stock entry, POS invoice, self-consumption, item rate, and stock availability logic |
| `LICENSE` and `hooks.py` | License mismatch requiring confirmation |

## To Confirm Before Publishing

- Exact public branch or tag name for ERPNext v15 installation.
- Correct license: `LICENSE` says GPL, while `hooks.py` says MIT.
- Whether a `Property Management Solution` ERPNext domain still needs to be created manually.
- Whether `setup.py` should still reference `requirements.txt`.
- Supported deployment assumptions for scheduler workers and long queue workers.
- Whether notifications should remain disabled by default.
- Maintainer support channel and SLA.
- Screenshots, demo site, and sample data.
- Whether tenant portal, payment gateway, external integrations, or approval workflows are planned separately.

## Support and Maintenance

Publisher: Aakvatech  
Email: info@aakvatech.com  
Website: https://aakvatech.com

For production deployments, confirm the maintained branch, support process, and upgrade policy with the maintainers.

## Contributing

Use the standard Frappe development workflow:

1. Create a feature branch.
2. Make focused changes.
3. Run linting and relevant tests.
4. Test installation and migration on a bench site.
5. Submit a pull request with a clear summary and migration notes.

## Versioning

Current repository version: `15.2.1`

Use a branch or tag that matches the deployed ERPNext major version. This repository targets Frappe and ERPNext v15.

## License

To confirm before publishing. The `LICENSE` file states `GPL`, while `propms/hooks.py` declares `app_license = "MIT"`.

## Maintainers

- Aakvatech
- info@aakvatech.com
