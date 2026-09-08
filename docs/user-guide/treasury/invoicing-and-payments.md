# Invoicing & Payments

## Invoices

An invoice records what a customer owes (line items, tax, discounts, and a due date) and tracks
payment against it as **Draft**, **Sent**, **Partial**, or **Paid**. A partially paid invoice shows
both the total and how much has actually been paid so far, rather than only a binary paid/unpaid
state.

Every invoice has a **public link** the customer can open without logging in. It's the link sent
in the [invoice notification](../notifications/message-templates.md#payments-invoices) and every
[overdue reminder](#automatic-overdue-reminders), and it's where the customer actually pays from.
It also has a downloadable PDF, referenced the same way in reminders as "view your invoice."

## Recording a payment

A payment against an invoice (or an order, or a subscription renewal) can be recorded three ways:

1. **Through the platform's own checkout.** M-Pesa STK push, card (Paystack), or another
   connected gateway. This is the normal path for a customer paying via their invoice's public
   link, and it settles automatically the moment the gateway confirms it.
2. **Cash on delivery**, for orders fulfilled with payment collected at the point of delivery.
   Confirmed once the delivery is completed.
3. **Recorded manually**, for a payment that happened outside the platform entirely: a bank
   transfer, cash handed over in person, or a till payment. Use **Confirm Payment** (or your
   product's equivalent action) and optionally note a reference, the M-Pesa code sighted or a bank
   transaction ID, for the audit trail. This immediately marks the payment as settled and triggers
   the same downstream effects a gateway payment would. The invoice updates, the customer's receipt
   notification sends, and, for a subscription payment, the subscription activates.

Every recorded payment shows up the same way in [Reports](reports.md) and in the customer's own
payment history, regardless of which path it came through.

## Automatic overdue reminders {: #automatic-overdue-reminders }

An unpaid invoice past its due date gets automatic reminder notifications, escalating in tone over
up to three stages as it stays unpaid longer: a gentle nudge first, firmer language as it ages
further, and an urgent final notice. Every reminder, at every stage, carries the same real
**pay-now link and invoice PDF** as the original invoice notification. A customer is never asked to
pay an overdue invoice without a direct way to do it.

## Refunds and failed payments

A refund is processed against the original payment and notifies the customer once it completes,
with the amount and reason. If a payment attempt fails outright (a declined card, a cancelled STK
push), the customer is notified with a direct retry link rather than being left to guess that
anything went wrong. See
[Payments & invoices](../notifications/message-templates.md#payments-invoices) for what these
notifications look like.

## Common Issues

**A customer says they paid but the invoice still shows unpaid.** If they paid through the
platform's own checkout, this settles automatically within moments. Check whether the payment
actually completed on their end first. If they paid another way (bank transfer, cash), it needs
[recording manually](#recording-a-payment). It will never show as paid on its own until someone
confirms it.

**An invoice's public link doesn't work for the customer.** Confirm you're sharing the exact link
from the invoice notification or reminder, not a shortened or retyped version. The link includes a
unique token that must match exactly.
