# Payments & Treasury

Every payment taken at the till ends up in Treasury, the platform's shared payment and ledger
layer — not just the sales you record through Treasury directly. This page explains that
connection from the POS side: what happens the moment a sale is paid, how a credit sale is tracked
until it's settled, and where to look when a customer's balance needs checking. For invoicing,
recording a payment made outside the platform, and financial reports (Profit & Loss, Cash Flow,
Tax Summary), see the [Treasury guide](../treasury/index.md) itself.

## How a sale becomes a payment record

Whichever tender is used — cash, card, M-Pesa, or a digital gateway — completing a sale creates a
payment record in Treasury the moment it's confirmed, and Treasury turns that into a receipt-type
invoice automatically. You never create this invoice by hand; it exists so every sale, from
whichever product sold it, shows up consistently in Treasury's reports and in the customer's own
payment history.

- **Cash, Card (PDQ), M-Pesa Code** — recorded immediately; no round trip to a payment gateway is
  needed, since the money was already collected at the till.
- **STK Push, C2B, Paystack, Wallet, and other online gateways** — go through Treasury's own
  payment-gateway handling, the same infrastructure a Treasury-issued invoice's public payment
  link uses. The sale completes automatically the moment the gateway confirms it.

## Credit sales and customer accounts {: #credit-sales-and-customer-accounts }

A credit sale needs a real customer attached first — see
[Attaching a customer](selling-and-checkout.md#attaching-a-customer). Choosing **Credit Sale** (On
Account) at checkout doesn't collect cash — it bills the amount to the customer's account, the
same account balance Treasury tracks for that customer's invoices too.
A customer's credit limit (set in Treasury) is enforced at the point of sale, so a credit sale
that would push them over their limit is rejected rather than silently allowed.

Two related concepts, easy to mix up:

- **Available credit** — how much more the customer can be sold on credit before hitting their
  limit (credit limit minus what they currently owe).
- **Store credit** — money the *business* owes the *customer* (an overpayment, a refund issued as
  credit rather than cash) — a completely separate balance from what they owe you.

When a customer has store credit available, **Apply Credit** appears as a checkout tender to use
it toward the current sale — for full or partial coverage. It can also net against a *new* credit
sale at the moment it's created, so a customer who's owed 5,000 and buys 10,000 on credit ends up
owing only the 5,000 difference, in one step.

Settling what a customer owes — recording a payment against their account balance rather than a
specific sale — is done from Treasury directly; see
[Invoicing & Payments](../treasury/invoicing-and-payments.md#recording-a-payment). Once settled
there, every open sale on their account reflects it automatically.

## Complimentary sales {: #complimentary-sales }

A complimentary (no-charge) sale still records full revenue for the sale, offset by a
Complimentary & Goodwill Expense line — so management reporting shows exactly what was given away,
rather than the sale simply vanishing from the books. Stock is still deducted normally. See
[Approvals & Manager Overrides](approvals-and-overrides.md#complimentary-no-charge-payments) for
the checkout workflow and the manager-approval requirement.

A bill paid partly in cash and partly comped (a split-bill scenario) posts as a single mixed
entry — the cash portion and the comped portion are both reflected accurately, rather than
either being double-counted or lost.

## Refunds

Completing an approved return (see [Selling & Checkout → Returns](selling-and-checkout.md#returns))
issues the refund through Treasury against the original payment, and prints/records a credit note
where your organisation's tax setup requires one. A return that's only been approved but not yet
completed hasn't refunded anything yet — see the three-stage lifecycle in
[Selling & Checkout](selling-and-checkout.md#returns).

## Till-side expenses {: #till-side-expenses }

**Add Expense** on the terminal toolbar (see
[Selling & Checkout](selling-and-checkout.md#add-expense)) posts directly to Treasury — the same
place an expense entered directly in Treasury lands. It shows up immediately in
**Register Details** (the current shift's own summary) and in Treasury's expense reports.

## Where to check a customer's real balance

The **Clients** page (sidebar, under Operations) shows what a specific customer owes and any store
credit they hold, sourced from the same balance Treasury tracks — POS never keeps its own
independent copy of a customer's balance. For a full statement, payment history, or to record a
payment against their account directly, use Treasury's own customer view; see
[Managing Your Organisation](../organisation/managing-your-organisation.md) for how access to
Treasury is granted to a team member.

## Common Issues

**A customer's balance on their receipt doesn't match what Treasury shows.** POS always reflects
Treasury's own balance — if the two look different, check whether a payment was just recorded, or
a credit sale was just edited to both add and remove items in the same save (there can be a brief
delay before both changes are fully reflected everywhere), before assuming something's wrong. If
it's still mismatched after a minute or two, contact your account manager rather than assuming
either figure is simply correct.

**A credit sale was rejected even though the amount looks small.** Check the customer's available
credit, not just the sale amount — a customer already carrying a balance close to their limit can
be pushed over it by a sale that would otherwise be well within a fresh limit.

**Apply Credit isn't showing at checkout for a customer who should have store credit.** Store
credit and "available credit" (credit-limit headroom) are different things — see
[Credit sales and customer accounts](#credit-sales-and-customer-accounts) above. Confirm the
customer genuinely has store credit (from an overpayment or a refund issued as credit), not just
room left on their credit limit.
