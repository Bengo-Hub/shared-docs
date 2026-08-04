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
| `inventory.purchase_order.received` | arpa + vendors | vendor bill (DR COGS/Inventory / CR AP) + supplier auto-payout; carries `project_id` for cost attribution |
| `inventory.asset.created` | assets `CapitalizationSubscriber` | auto-register capital-allowance asset (linked by `source_asset_id`) + DR Fixed Assets 1750 / CR Asset Clearing 1760 |
| `inventory.asset.disposed` | assets `CapitalizationSubscriber` | retire CA asset + record capital gain/loss (proceeds − WDV) |
| `inventory.asset.depreciation_due` | assets `DepreciationSubscriber` | DR Depreciation 6500 / CR Accum Depr 1700 |
| `erp.payroll.processed` | payroll subscriber | DR Salaries 6000 / CR Net Pay 2400 / CR Statutory 2500 |
| `erp.payroll.reversed` | payroll subscriber | inverse of the above (batch reversal) |
| `erp.expense_claim.approved` | claim subscriber | NON-taxable: DR expense (6100, or 6200 per-diem/mileage) / CR Employee Payable 2600. Taxable → skipped (taxed via payslip) |
| `erp.casual_labor.approved` | claim subscriber | DR Casual Labour 6300 / CR Employee Payable 2600 |

## Projects ↔ finance
- **projects-api owns no expense/budget module** (only project/task/milestone/member/tender). Project
  costs flow through **project-tagged ERP expense claims** + **project-tagged inventory requisitions/
  POs** (both carry `project_id`). Treasury budgets gain `project_id`/`cost_center_id`/`parent_budget_id`
  so a project budget rolls up into the company fiscal-year budget; `BudgetLine.actual_amount` is
  computed from posted ledger transactions (live on read + `POST /budgets/{id}/recompute-actuals`).

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
  approvable `CasualLaborRecord` that posts to GL on approval and can retire an imprest/advance.
- **Payslip reversal**: a payroll batch can be reversed (`reverse` command) → `erp.payroll.reversed`
  → inverse GL journal.

## Platform vs tenant books
- `is_platform_only` on chart-of-accounts AND cost-centers hides platform-internal options from
  tenant users (COA list + all account/cost-center pickers). The platform owner operates as its own
  real tenant (`codevertex`); `566afdf5…` is a reserved namespace for shared global tax codes, NOT a
  books-bearing tenant.

## Conventions for adding a new cross-service posting
1. Emit from the source via the outbox (`events.Publisher.Publish(ctx, tenant, aggregateID, "x.y", payload)`).
2. Add a treasury JetStream consumer that resolves accounts by code, builds balanced lines, and posts
   via `AutoPostJournalEntry` with a deterministic `reference_type`+`reference_id` (idempotent).
3. Seed any new chart-of-accounts codes in `handlers.defaultAccountSeeds` (mark `IsPlatformOnly` only
   if platform-internal).
4. Wire the corresponding UI action (button/form) — every backend workflow has a UX surface.
