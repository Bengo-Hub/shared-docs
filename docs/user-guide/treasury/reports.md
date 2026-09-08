# Reports

Every report below draws from the same underlying ledger, so figures line up across them — a
number never means one thing in the P&L and something else in Cash Flow.

## Choosing a period

Every report (except Balance Sheet, which is always a snapshot **as of** a single date) can be run
against:

- **A date range** — pick any "from" and "to" date directly.
- **A fiscal year** — aligns to your organisation's configured financial year, however it's set up.
- **An accounting period** — a specific month or period within a fiscal year, if your organisation
  uses period-based closing.

Whichever basis you pick, the report's header states the exact range it's showing — worth checking
before reading figures off it, especially near a period boundary.

## Profit & Loss

Two views of the same underlying figures, for different purposes:

**Full statement** — the traditional line-by-line P&L: every revenue and expense account,
Cost of Sales broken out separately from Operating Expenses so Gross Profit reads correctly, down
to Net Income. This is the one to export or hand to an accountant.

**Summary** — a faster read: Revenue, COGS, Gross Profit, Expenses, and Net Profit as headline
figures, a composition chart, and expenses broken down by category and cost center. It also shows
a **reconciliation** against invoice-based figures — useful context if your business takes a mix of
POS/walk-in sales (which post straight to the ledger) and invoiced sales (which post through the
invoicing flow); the two won't always match exactly, and the reconciliation card shows the
variance rather than hiding it. Can additionally be filtered to a single outlet/branch.

## Cash Flow

Starts from Net Profit and reconciles it to the actual change in cash for the period: non-cash
items added back (depreciation), then adjusted for working-capital movements — receivables,
inventory, payables, and VAT — ending in an opening-to-closing cash reconciliation. This answers "why
doesn't our bank balance match our profit" as much as it reports the cash position itself.

## Tax Summary

VAT collected and paid for the selected period, at a glance — the figures you'd pull together for a
tax filing without re-deriving them from the ledger by hand.

## Common Issues

**A figure looks different from what I expected for "this month."** Double-check the exact date
range shown in the report's own header — "this month" can mean a calendar month, a fiscal period,
or a custom range depending on which basis you picked, and they don't always land on the same
boundary.

**P&L Summary's Gross Profit is negative or doesn't match the full statement.** This usually means
your revenue is mostly POS/walk-in (ledger-posted) while costs are mostly from purchases/vendor
bills recorded separately — see the reconciliation card on the Summary view, which is built
specifically to surface this rather than let it look like an error.
