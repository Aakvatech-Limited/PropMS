# PropMS v15 Frappe Cloud audit remediation — dry-run and release gate

## Change order

1. PR #120 (Query Builder conversions) and replacement PR #122 (remaining code-audit corrections) are merged into `version-15-hotfix`. PR #121 was automatically closed after its former base branch was removed.
2. Verify PR #123 (USD invoice date alias) and PR #124 (lease date boundary and meter history) are merged and record the final hotfix SHA.
3. Run an isolated staging dry-run before any production deployment, then rerun the Frappe Cloud Marketplace security/correctness scan on the final code.
4. Separately update the publisher-managed Marketplace metadata, links and genuine screenshots in the Frappe Cloud listing editor.

## Dry-run safety

**Never execute a migration on the production site as the first test.** Make a current backup (database and files) and rehearse against a clone of production in a restricted staging environment with email, scheduler, webhooks, and external payment integrations disabled. Keep the pre-upgrade commit SHA and backup IDs.

### Staging procedure

1. Record the current app revisions, installed versions, site configuration, `bench doctor` status, and scheduler state.
2. Restore the production backup to an isolated staging site running **Frappe/ERPNext v15** and the same other installed apps. Ensure any sensitive data is appropriately protected.
3. Checkout the candidate merged v15 hotfix SHA in staging, install Python dependencies, then run `bench --site <staging-site> migrate`.
4. Confirm custom fields and property setters are loaded, stable on a second migrate, and no unexpected records change.
5. Verify the following with **synthetic** draft/sample data first:
    - Lease creation, renewal, transitions from Upcoming to Active and Expired; scheduler transactions commit only at framework transaction boundaries.
    - Invoice schedule creation, rent/utility invoice reports, payment/currency calculations, reporting month/date boundaries.
    - Maintenance Issue Materials: create Stock Entry / Sales Invoice, confirm material reference links, failure rollback and no partial saves.
    - Property status updates (including leases ending in the next 3 months), property-unit assignments, and leases without end dates.
    - Meter selection/query filters, prior reading retrieval, initial meter fallback and reading differences.
    - Form behaviour: Lease action buttons, property forms, Key Set Detail, Tool Item Record, daily checklist, security and outsourcing attendance.
    - Check permissions as a non-System-Manager user and compare expected records before/after scheduler runs.
6. Run the app's available tests and CI hooks against the exact commit; re-run the Frappe Cloud scanner and record each of the 86 original finding IDs.
7. Verify that old QUnit scaffold removals have not removed real tests (removed files were dummy assertions only). If tests are still required, implement meaningful Frappe v15 test coverage before release.

### Release acceptance gate

- CI: Pre-commit, Ruff, No Raw SQL, Semantic Commits, and Semgrep Security all green.
- Frappe Cloud scan: zero unreviewed security findings; correctness findings cleared or explicitly justified.
- Operational checks: same values and row counts for rent reports and invoice schedules before/after on a representative fixed dataset.
- Transaction checks: no partial stock entries, invoices, or leases after an intentionally failed request.
- Marketplace listing: no install instructions in long description; real screenshots and support/privacy policy URLs configured.
- Backups verified; rollback ownership, decision window and recovery procedure approved.

### Production change window

During an approved change window after successful staging validation: back up and verify restorability, deploy the exact reviewed commit, migrate, smoke-test, then re-enable scheduled jobs and integrations. If any critical control fails, halt and restore the tested previous revision and backup using the organization's recovery process. Do not silently attempt downgrade migrations on live data.

## Audit mapping

The source audit contains **86 Semgrep code findings**: 6 SQL formatting, 4 file traversal reviews, 3 manual commits, 71 deprecated `cur_frm` references, 2 functional-programming warnings. PR #120 addresses SQL queries; stacked PR #121 addresses the remaining warnings. A fresh Marketplace report is required before marking scanner closure.

Separate Marketplace listing warnings: long description contains installation commands, screenshots absent, and links warning despite `missing_links: []` in report.
