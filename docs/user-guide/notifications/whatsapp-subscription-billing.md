# WhatsApp Subscription & Billing

WhatsApp messaging is billed differently from the rest of the platform. Instead of a top-up wallet
like SMS credits, it's a **monthly subscription with a bundled message quota**. Pick a plan sized
to how many WhatsApp messages your business actually sends in a month.

> **Direct link:** **Billing → WhatsApp** (also reachable via **Manage WhatsApp Subscription** from
> the SMS Credits tab).

## Plans

| Plan | Price | Messages / month |
|---|---|---|
| Basic | KES 500/mo | 100 |
| Standard | KES 1,000/mo | 500 |
| Pro | KES 2,000/mo | Unlimited |

A message counts against your quota when it's actually sent, outbound only. A customer messaging
you doesn't count, and neither does an account-info connection check from
[Test Connection](configuring-channels.md#testing-a-connection). If you're on a metered plan and
reach your monthly limit, further WhatsApp sends pause until the next billing cycle or an upgrade.
Every other channel keeps working normally.

## Subscribing or changing plans

The **Current Subscription** card at the top of the page shows your plan, messages used this
period, when it started, and when it expires. Below it, every available plan is listed side by
side with **Subscribe** on whichever one you want. Picking a new plan while one is already active
renews or upgrades it rather than stacking a second subscription. Payment is handled the same way
as any other platform payment: a checkout window opens for the plan's price, and your subscription
activates as soon as that payment is confirmed.

**Cancel Subscription** stops auto-renewal but doesn't cut you off immediately. You keep access
until the current period's expiry date, shown in the confirmation prompt.

## Without an active subscription

WhatsApp sends for your account simply don't go out until you subscribe. See
[Why WhatsApp has no shared fallback](configuring-channels.md#why-whatsapp-has-no-shared-fallback).
This applies to every WhatsApp send: automated notifications, [WhatsApp Inbox](whatsapp-inbox.md)
replies, and test connections with a real recipient.

## Common Issues

**"no_active_subscription" when sending a real test message.** Exactly what it says. Subscribe to
a plan first, or if you already believe you're subscribed, check **Billing → WhatsApp** for
whether it's actually active or has lapsed.

**I paid outside the in-app checkout and WhatsApp still isn't sending.** A payment made another
way, a bank transfer, cash, or till payment, doesn't activate the subscription automatically.
Contact your account team with your payment reference so it can be reconciled, and your
subscription will activate the same as a normal checkout payment would.
