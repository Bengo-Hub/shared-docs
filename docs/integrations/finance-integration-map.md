# Finance Integration Map (Treasury · Projects · Inventory · ERP)

How financial data flows into the centralized treasury general ledger from the other services,
and how projects, assets, budgets, payroll and expense claims are tied together. All cross-service
posting is **event-driven** (NATS JetStream via the transactional outbox) and **idempotent**
(deterministic `reference_type`+`reference_id` guards on every journal entry).

## Where the General Ledger lives
- Treasury-api owns the GL. Nav (treasury-ui): **Accounting → Chart of Accounts / Journal Entries /
  Vouchers / Trial Balance / Accounting Periods / Cost Centers / Reconciliation / Audit History**.
  There is no separate "General Ledger" page — the GL = Journal Entries (postings) + Trial Balance
  (per-account balances). Reports → Financial Statements renders Balance Sheet / P&L / Cash Flow.
- Double-entry core: `ledger.Service` (`CreateJournalEntry`→submit→approve→post, plus
  `AutoPostJournalEntry` for system entries). Every consumer posts through this one path.

## Accounting correctness invariants
- **Balance sheet** includes a computed **Current Year Earnings** line (revenue − expense to date)
  in equity, so Assets == Liabilities + Equity even before a year-end close. The trial balance also
  reports `equation_balanced` + `current_year_earnings`; the "Books Balanced" badge requires BOTH
  double-entry integrity (ΣDr==ΣCr) AND the accounting equation.
- **Year-end close** (`fyclose`) moves P&L → Retained Earnings (3100); an opt-in scheduler
  (`FYCLOSE_AUTO_ENABLED`) closes the just-ended FY after a grace period.

## Event → GL posting map (all idempotent)
| Source event | Treasury consumer | GL posting |
|---|---|---|
| `pos.sale.finalized` | pos subscriber | DR Cash / CR Revenue / CR VAT |
| `inventory.purchase_order.received` | vendor-bill subscriber | vendor bill (DR COGS/Inventory / CR AP) + supplier auto-payout; carries `project_id` for cost attribution |
| `inventory.asset.created` | assets `CapitalizationSubscriber` | auto-register capital-allowance asset (linked by `source_asset_id`) + DR Fixed Assets 1750 / CR Asset Clearing 1760 |
| `inventory.asset.disposed` | assets `CapitalizationSubscriber` | retire CA asset + record capital gain/loss (proceeds − WDV) |
| `inventory.asset.depreciation_due` | assets `DepreciationSubscriber` | DR Depreciation 6500 / CR Accum Depr 1700 |
| `erp.payroll.processed` | payroll subscriber | DR Salaries 6000 / CR Net Pay 2400 / CR Statutory 2500 |
| `erp.payroll.reversed` | payroll subscriber | inverse of the above (batch reversal) |
| `erp.expense_claim.approved` | claim subscriber | NON-taxable: DR expense (6100, or 6200 per-diem/mileage) / CR Employee Payable 2600. Taxable → skipped (taxed via payslip) |
| `erp.casual_payment.approved` | claim subscriber | DR Casual Labour 6300 / CR Employee Payable 2600 |
| `erp.consultant_voucher.approved` | consultant subscriber | consultant cost with cost center on the GL lines |

> Verified against code 2026-09-28. The casual labour subject is `erp.casual_payment.approved` (ERP schema `CasualPayment`). Claim and casual payment GL lines carry the claim's `cost_center_id` and `project_id`. `erp.payroll.processed` carries `allocations[]` per employee (project and cost centre from `EmployeeProjectAllocation`, the rest on the department cost centre), and treasury splits the salary expense lines by them; liability and bank lines stay unsplit.

## Budget events and commitments

| Event | Consumer | Effect |
|---|---|---|
| `inventory.purchase_order.sent` / `.cancelled` | treasury PO commitment subscriber | opens / releases a budget commitment on the purchase account; bills draw it down, full receipt consumes it |
| `erp.expense_claim.created` / `.updated` / `.deleted` / `.approved` | treasury claim subscriber | opens, updates, releases or consumes the claim's commitment (taxable, non-KES and already booked claims hold nothing) |
| `project.closed` / `project.deleted` | treasury project subscriber | closes approved and active project budgets, cancels drafts, releases open commitments |
| `treasury.budget.approved` | projects-api | sets `Project.budget` (budget at completion) from `planned_cost` |
| `treasury.budget.threshold_crossed` | notifications-api (subscribes to `treasury.>`) | alert once per line per threshold |

Budget checks before spend: inventory-api calls `POST /s2s/{tenant}/ap/purchase-budget-check` before sending a PO, and erp-api calls `POST /s2s/{tenant}/budgets/claim-check` before approving a claim. A stop answers 409 `over_budget` (inventory: `OVER_BUDGET`), and approvers can override. Treasury subscribers bind to whichever JetStream stream owns the subject (`platform/events.StreamFor`).

## Projects ↔ finance

Verified against code 2026-09-28.

- **Treasury owns all budgets, including project budgets** (decision 2026-09-27). projects-api's old
  `Budget`, `Expense` and `TimeLog` tables are dropped. projects-api creates, edits and submits its
  project budgets in treasury over S2S (acting as the signed-in user) and reads
  `GET /s2s/{tenant}/budgets/projects/financials?ids=` in one batch per page, then computes earned
  value from its own task estimates and progress (`/financials/projects/{id}`, `/financials/portfolio`).
- Budget actuals are booked KES ledger lines only, grouped by account, cost centre, project and
  month, and matched to the most specific budget line; they agree with the P&L. Details:
  `finance-service/treasury-api/docs/budgets-and-planning.md`.
- Project cost reaches the GL through project-tagged inventory PO bills, ERP claims and casual
  payments, payroll salary lines split by allocation, expenses (`metadata.project_id`) and bill
  purchase legs. Project revenue comes from invoices tagged with `metadata.project_id`.
- Hours: projects-api reads approved and submitted timesheet hours per project from erp-api
  (`GET /hrm/attendance/timesheets/project-hours`) for utilisation. erp-api reports a payroll month's
  gross pay by project (`GET /hrm/payroll/labour-cost`) with the same split payroll posts.
- There is no historic backfill: postings made before the dimensions existed stay undimensioned.

## Assets & capital allowances
- Inventory-api owns the fixed-asset register; treasury owns the financial side. An inventory asset
  auto-creates a treasury **capital-allowance** row (`source_asset_id`, `asset_account_id`); KRA class
  defaults to `UNCLASSIFIED` until set in the Tax → Capital Allowances tab. Maintenance/insurance are
  expensed (opex), not capitalised; disposal computes the capital gain/loss for tax.

## Expense claims & tax treatment (KRA)
- One reimbursement system: ERP `ExpenseClaim` (with `project_id`, `cost_center_id`, `claim_type`,
  `taxable`). **Non-taxable** reimbursements are paid via treasury **AP** (Employee Payable 2600),
  never through payroll gross → they don't inflate PAYE. **Taxable** amounts (per-diem/mileage excess
  over KRA caps — KES 2,000→10,000/day from 2025-07-01; AA mileage rate; taxable allowances) feed the
  payroll engine's `TaxableAllowances` lane for PAYE. Non-cash benefits: taxable excess over the
  KES 3,000/month de-minimis (opt-in `NonCashAsTaxable`).
- **Casual/subcontracted labour** (e.g. a PM/consultant paying casual workers) is a documented,
  approvable ERP `CasualPayment` that publishes `erp.casual_payment.approved`, posts to GL on approval
  and can retire an imprest/advance.
- **Payslip reversal**: a payroll batch can be reversed (`reverse` command) → `erp.payroll.reversed`
  → inverse GL journal.

## Platform vs tenant books
- `is_platform_only` on chart-of-accounts AND cost-centers hides platform-internal options from
  tenant users (COA list + all account/cost-center pickers). The platform owner operates as its own
  real tenant (`codevertex`); a separate reserved tenant ID exists purely as a namespace for shared
  global tax codes, and is NOT a books-bearing tenant.

## Conventions for adding a new cross-service posting
1. Emit from the source via the outbox (`events.Publisher.Publish(ctx, tenant, aggregateID, "x.y", payload)`).
2. Add a treasury JetStream consumer that resolves accounts by code, builds balanced lines, and posts
   via `AutoPostJournalEntry` with a deterministic `reference_type`+`reference_id` (idempotent).
3. Seed any new chart-of-accounts codes in `handlers.defaultAccountSeeds` (mark `IsPlatformOnly` only
   if platform-internal).
4. Wire the corresponding UI action (button/form) — every backend workflow has a UX surface.
