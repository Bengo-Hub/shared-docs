# Message Templates

What a customer or staff member actually receives for each kind of notification, with real
examples for every channel it goes out on, and where a payment or invoice link gets attached
automatically.

## How the channels differ

**Email** is the richest channel: a full branded layout, your logo, and as much detail as the
notification needs. **SMS** and **WhatsApp** are short, single-message texts, built to be read in
a few seconds on a phone. **Push** is shorter still: a title and one line, the kind of banner that
appears on a phone's lock screen.

WhatsApp has one extra rule the others don't: outside an active conversation, it only allows
messages that use a **template pre-approved by Meta**. Free-form text is rejected unless the
recipient messaged your business first within the last 24 hours. That's a WhatsApp platform rule,
not a Codevertex Africa limitation, and it's why WhatsApp templates go through a review step Email
and SMS don't need.

Every template below uses **numbered placeholders** (`{{1}}`, `{{2}}`, …) or named ones
(`{{customer_name}}`, `{{amount}}`) that get filled in with the real order number, amount, date,
and so on when the message sends. You see the finished message, never the placeholders.

## Order & delivery

Order updates send on every channel a customer has contact details for and you've enabled for
that type (see [Choosing which channels a notification uses](configuring-channels.md#choosing-which-channels-a-notification-uses)).
A customer with both an email and a phone number on file, with WhatsApp and SMS both turned on,
gets all three for the same event.

**Order placed**

| Channel | What the customer receives |
|---|---|
| Email | A branded receipt: order number, itemized total, and estimated delivery time. |
| SMS | `Urban Loft Cafe: Order #ULC-2291 confirmed! Total: KES 2,450. Track: cdvtx.co/t/2291` |
| WhatsApp | `Urban Loft Cafe: Order #ULC-2291 confirmed! Total: KES 2,450. Estimated delivery: 35 min. Track: cdvtx.co/t/2291` |

**Order ready / ready for pickup**
> Hi Amina, your order #ULC-2299 is ready! View details here: cdvtx.co/o/2299. Thank you for your order!

**Order out for delivery**
> Hi Amina, your order #ULC-2299 is out for delivery with James K. (0711223344). Track it here: cdvtx.co/t/2299.

**Order delivered**
> Urban Loft Cafe: Your order #ULC-2291 has been delivered! We hope you enjoy it. Share your feedback: cdvtx.co/f/2291

**Order cancelled**
> Hi Amina, your order #ULC-2299 has been cancelled. Reason: Item out of stock. We're sorry for the inconvenience.

**Order refunded**
> Hi Amina, your refund of KES 2,450 for order #ULC-2299 has been processed. Reason: Order cancelled by customer.

**Order scheduled**
> Hi Amina, your order #ULC-2299 has been scheduled for 9 Sep, 6:00 PM. Total: KES 3,200. View details: cdvtx.co/o/2299

**Delivery arriving** *(logistics deliveries)*
> TruLoad: Your delivery is arriving! Order TL-40217. ETA: 12 min. Track here: cdvtx.co/t/40217

Every order state above sends by Email as a full receipt-style message, and by SMS/WhatsApp as the
shorter text shown. **Push** carries the same short text as a phone notification, for customers or
staff using a mobile app, with a tap-through straight to the order.

## Payments & invoices

Every payment and invoice notification carries a **real, working link**, never just a reference
number with nothing to click through to:

| Notification | Link included |
|---|---|
| Payment received | Order reference (link where the order has one) |
| Payment failed | **Retry payment link**, a direct way to try again, not just "your payment failed" |
| Payment receipt | Receipt reference |
| Invoice sent | **Public invoice link + payment link**, opens the invoice and lets the customer pay directly |
| Invoice overdue reminder | **Payment link**, same link as above, so paying is always one tap away |
| Refund completed | Refund reference |
| **Subscription invoice / renewal notice** | **Public invoice link (PDF) + payment link**: your subscription invoice is never just an amount and a due date, there's always a direct link to view and pay it |

**Payment successful**

| Channel | What the customer receives |
|---|---|
| Email | A branded receipt with the amount, order or invoice reference, and a link to view it. |
| SMS | `Hi Amina, your payment of KES 1,180 for order #POS-88213 was successful. Thank you - Urban Loft Cafe` |
| WhatsApp | `Thank you for your purchase, David! Order: POS-88213. Total: KES 1,180. View or download your receipt: cdvtx.co/r/88213` |

**Payment failed**

| Channel | What the customer receives |
|---|---|
| Email | An explanation of what failed, with a **Retry Payment** button. |
| SMS | `Payment for order #ULC-3310 failed. Retry: cdvtx.co/o/3310/pay - Urban Loft Cafe` |
| WhatsApp | `Hi Samuel, your payment for order #ULC-3310 was unsuccessful. Please try again here: cdvtx.co/o/3310/pay. Need help? Contact our support team.` |

**Invoice sent / subscription invoice ready**
> Your subscription invoice INV-260907-014 for KES 42,000 is ready. Due 21 Sep 2026. Pay now: pay.codevertexafrica.com/i/260907014

If you ever receive a payment or invoice notification *without* a link, that's a bug worth
reporting to your account contact. Every one of these is meant to carry one.

## Account & security

OTPs and password resets are SMS and email only, kept deliberately short and free of any link you
could be phished with:

**OTP verification**

| Channel | What the recipient receives |
|---|---|
| Email | The same code, in a plain security-focused layout. |
| SMS | `Your CodeVertex code is 482913. It expires in 10 minutes. Do not share this code with anyone.` |

**Password reset**
> CodeVertex: Password reset requested for Amina. Your reset code is 71-KTV9. Expires in 15 minutes.

## ISP Billing

The heaviest WhatsApp and SMS user on the platform today: subscription welcomes, renewals, expiry
reminders, and payment confirmations, each carrying the exact package name, expiry date, and
(where relevant) renewal Paybill/Account details. Also sent by Email for customers who prefer it.

**Expiry reminder**
> SkyNet ISP: Hi Peter, your Home 20Mbps subscription expires on 12 Sep (2 days left). Renew via Paybill 400200, Account 0712345678.

**Payment received**
> SkyNet ISP: Payment of KES 2,500 received. Thank you Peter. Your Home 20Mbps package is active until 12 Oct.

## WhatsApp Inbox notifications

A new customer reply in the [WhatsApp Inbox](whatsapp-inbox.md) triggers a **push notification**
to staff with WhatsApp Inbox access, so a reply doesn't sit unseen. It's short by design, just
enough to know a customer is waiting:
> Amina Wanjiru: Is the order still on for delivery today?

## Where this is heading

Order updates and payment results (shown above) now have full Email, SMS, and WhatsApp coverage,
alongside ISP Billing and the core order/OTP set. Inventory, Library, and HR notifications don't
have SMS or WhatsApp templates yet; today they only reach you by Email. Bringing those channels to
these notification types is in progress, and this page will be updated as each one goes live.
