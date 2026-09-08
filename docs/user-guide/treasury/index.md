# Treasury

Invoicing, payments, and financial reporting — Treasury is where money coming in and going out of
your business gets recorded, tracked, and reported on. This guide covers what you do as a tenant
admin or finance user; if you're building against the API directly, see the
[Finance Integration Map](../../integrations/finance-integration-map.md) and
[Payment Workflow](../../integrations/payment-workflow.md) in the Technical Guide instead.

### In this section

- **[Invoicing & Payments](invoicing-and-payments.md)** — creating invoices, the public link
  customers pay from, and how a payment gets recorded — whether it comes through the platform's
  own checkout or was paid another way (bank transfer, cash) and needs reconciling manually.
- **[Reports](reports.md)** — Profit & Loss (full statement and summary), Cash Flow, and Tax
  Summary, and how to pick the period or date range each one covers.

## How Treasury connects to the rest of the platform

Treasury doesn't only handle invoices you create directly here — it's the shared payment and
ledger layer other products post into. A POS sale, an ordering-service checkout, and a subscription
renewal (see [Subscriptions & Billing](../subscriptions-and-billing.md)) all ultimately create a
payment record or invoice in Treasury, which is why its reports reflect revenue from across your
whole business, not just what you entered by hand. When a payment succeeds, the customer's
[notification](../notifications/message-templates.md#payments-invoices) — receipt, invoice link,
or failure notice — is sent automatically.

## Before you start

Treasury access is granted per role from **My Organization → Team** — see
[Managing Your Organisation](../organisation/managing-your-organisation.md#team). What you can see
and do (view-only vs. recording payments vs. approving invoices) depends on the role you've been
given.
