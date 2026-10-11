# Approvals

Every service that needs sign-off on something (a payout, a purchase order, a stock adjustment, a
credit note, a quote) runs it through one approval engine inside that service. Workflows never keep
their own "approved by" columns or approve endpoints. The engine has the same shape in every service,
so rules, inboxes and audit read the same way across the platform.

## The shape

| Part | What it holds |
|---|---|
| Rule | A module (the workflow), an amount band (`min_amount`, optional `max_amount`) and ordered steps, each naming the role that approves it. The most specific band wins (highest minimum). |
| Request | One per object sent for approval: module, object id and reference, amount snapshot, the rule used, status (`pending`, `approved`, `rejected`, `cancelled`) and the current step. Submitting again cancels the object's earlier pending request. |
| Action | One per step: the step's role, its decision, who decided and when, and a comment. |
| Decision | Approvers act on the current step in order. The request is approved after the last step and rejected the moment any step is rejected. A step is claimed with a compare-and-set on its pending state, so two approvers deciding at once cannot both win. |

## Where it lives

| Service | Engine | Modules today |
|---|---|---|
| treasury-api | `internal/modules/approvals` (rule steps and actions as tables; delegation, OTP, payout policy per flow) | invoices, expenses, payouts, journals, budgets, vendor bills, credit and debit notes, quotations |
| inventory-api | `internal/modules/approvals` (rule steps and actions as tables) | purchase orders, requisitions, stock adjustments, write-offs, stock counts, transfers, manufacturing, assets |
| maskani-api | `internal/modules/approvals` (rule steps and request actions as JSON on the row; inbox `/approvals`, rules `/approvals/rules`) | credit notes, waivers, manual payment verification, work order quotes; restructure, vendor bill, refund, deposit deduction, remittance and write-off as those flows land |

## How a workflow uses it

1. Register defaults and a decision hook at startup (maskani: `SetDefault(module, steps...)` and
   `OnDecision(module, hook)`). The default applies when no rule matches an amount; a module
   without a default needs no approval below its rules.
2. When the object is created, call `Submit` with the module, object id, reference, amount and
   (where the service scopes by site) the property or outlet.
3. Approve and reject through the engine (`Act`, or maskani's `Decide`, which also runs the hook).
   The hook applies the outcome: book the payment, raise the credit note, release the work.
4. Lists of the workflow's own records show each row's latest request beside it, fetched in one
   query for the page (never one query per row).

## Rules every engine keeps

- Separation of duties: the person who submitted an object never decides it. Maskani also lets one
  person decide only one step of a request.
- Roles, not people: steps name role codes; administrators may act on any step.
- Alerts: whoever can act on the waiting step is told (maskani publishes `approval.pending` to the
  holders of the step's role; permission steps are announced by the workflow's own event).
- Inbox "waiting for me" is a SQL filter, not a scan: maskani keeps the waiting step's approver on
  the request (`current_approver`) and indexes it.
- Sign-offs that carry no amount and no money (publishing a document template, running a billing
  period without missing readings) may stay outside the engine, but record who acted.
