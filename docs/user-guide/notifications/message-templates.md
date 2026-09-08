# Message Templates

What a customer or staff member actually receives for each kind of notification — with real
examples — and where a payment or invoice link gets attached automatically.

## Why WhatsApp uses fixed templates

Email and SMS can say anything you configure. WhatsApp is different: outside an active
conversation, WhatsApp only allows messages that use a **template pre-approved by Meta** — free-form
text is rejected unless the recipient messaged your business first within the last 24 hours. This is
a WhatsApp platform rule, not a Codevertex Africa limitation, and it's why WhatsApp templates go
through a review step Email and SMS don't need.

Every template below uses **numbered placeholders** (`{{1}}`, `{{2}}`, …) that get filled in with
the real order number, amount, date, and so on when the message sends — you see the finished message,
never the placeholders.

## Order & delivery

**Order placed**
> Urban Loft Cafe: Order #ULC-2291 confirmed! Total: KES 2,450. Estimated delivery: 35 min. Track: cdvtx.co/t/2291

**Order ready**
> Hi Amina, your order #ULC-2299 is ready! View details here: cdvtx.co/o/2299. Thank you for your order!

**Order ready for pickup**
> Hi Amina, your order #ULC-2299 is ready for pickup at Westlands Branch, 5:30 PM today. View details here: cdvtx.co/o/2299. See you soon!

**Order out for delivery**
> Hi Amina, your order #ULC-2299 is out for delivery with James K. (0711223344). Track it here: cdvtx.co/t/2299. Thank you for your order!

**Order delivered**
> Urban Loft Cafe: Your order #ULC-2291 has been delivered! We hope you enjoy it. Share your feedback: cdvtx.co/f/2291

**Order cancelled**
> Hi Amina, your order #ULC-2299 has been cancelled. Reason: Item out of stock. View details here: cdvtx.co/o/2299. We're sorry for the inconvenience.

**Order refunded**
> Hi Amina, your refund of KES 2,450 for order #ULC-2299 has been processed. Reason: Order cancelled by customer. Thank you for your patience!

**Order scheduled**
> Hi Amina, your order #ULC-2299 has been scheduled for 9 Sep, 6:00 PM. Total: KES 3,200. View details here: cdvtx.co/o/2299. Thank you for your order!

**Delivery arriving** *(logistics deliveries)*
> TruLoad: Your delivery is arriving! Order TL-40217. ETA: 12 min. Track here: cdvtx.co/t/40217

## Payments & invoices

Every payment and invoice notification carries a **real, working link** — never just a reference
number with nothing to click through to:

| Notification | Link included |
|---|---|
| Payment received | Order reference (link where the order has one) |
| Payment failed | **Retry payment link** — a direct way to try again, not just "your payment failed" |
| Payment receipt | Receipt reference |
| Invoice sent | **Public invoice link + payment link** — opens the invoice and lets the customer pay directly |
| Invoice overdue reminder | **Payment link** — same link as above, so paying is always one tap away |
| Refund completed | Refund reference |
| **Subscription invoice / renewal notice** | **Public invoice link (PDF) + payment link** — your subscription invoice is never just an amount and a due date; there's always a direct link to view and pay it |

**POS receipt (WhatsApp)**
> Thank you for your purchase, David! Order: POS-88213. Total: KES 1,180. View or download your receipt: cdvtx.co/r/88213

**Payment failed (WhatsApp)**
> Hi Samuel, your payment for order #ULC-3310 was unsuccessful. Please try again here: cdvtx.co/o/3310/pay. Need help? Contact our support team.

**Subscription invoice ready**
> Your subscription invoice INV-260907-014 for KES 42,000 is ready. Due 21 Sep 2026. Pay now: pay.codevertexafrica.com/i/260907014

If you ever receive a payment or invoice notification *without* a link, that's a bug worth reporting
to your account contact — every one of these is meant to carry one.

## Account & security

**OTP verification**
> Your CodeVertex code is 482913. It expires in 10 minutes. Do not share this code with anyone.

**Password reset**
> CodeVertex: Password reset requested for Amina. Your reset code is 71-KTV9. Expires in 15 minutes.

## ISP Billing

The heaviest WhatsApp user on the platform today — subscription welcomes, renewals, expiry
reminders, and payment confirmations, each carrying the exact package name, expiry date, and
(where relevant) renewal Paybill/Account details:

> SkyNet ISP: Hi Peter, your Home 20Mbps subscription expires on 12 Sep (2 days left). Renew via Paybill 400200, Account 0712345678.

## Where this is heading

Order updates and payment results (shown above) now have full WhatsApp coverage, alongside ISP
Billing and the core order/OTP set. Inventory, Library, and HR notifications don't have WhatsApp
templates yet — today they only reach you by Email (and some by SMS). Bringing WhatsApp coverage
to these is in progress; this page will be updated as each one goes live. The full working draft —
every template, its exact wording, and which ones are already live vs. still pending Meta's
approval — is tracked internally and available on request from your account contact.
