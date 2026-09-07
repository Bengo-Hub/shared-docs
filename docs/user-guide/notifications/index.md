# Notifications

How your customers and staff hear from your business — order updates, payment receipts, OTPs,
overdue reminders, delivery alerts — across Email, SMS, WhatsApp, and push. This guide covers what
you can configure yourself as a tenant admin: which channels are active, your own WhatsApp number,
and which notification types go out on which channel.

If you're building against the notifications API directly, you want the
[Notifications REST API](../../integrations/notifications-rest-api-integration.md) reference in the
Technical Guide instead — this page is for the Settings screens.

### In this section

- **[Channels & Providers](configuring-channels.md)** — connecting your own Email, SMS, and
  WhatsApp sender so messages go out under your own brand, WhatsApp's specific requirements, and
  choosing which channel(s) each notification type uses.
- **[Message Templates](message-templates.md)** — what a customer actually receives for each kind
  of notification, with real examples, and where a payment or invoice link gets attached
  automatically.

## The channels, in short

| Channel | Sender identity | If you haven't configured your own |
|---|---|---|
| **Email** | Your own SMTP/Brevo sender, or the platform's | Falls back to the platform's shared sender — messages still send, just not from your own domain. |
| **SMS** | Your own Africa's Talking account, or the platform's shared shortcode | Falls back to the platform's shared shortcode automatically. |
| **WhatsApp** | Your own WhatsApp Business number only | **Does not fall back.** WhatsApp messages simply won't send until you connect your own number — see [why](configuring-channels.md#why-whatsapp-has-no-shared-fallback). |
| **Push** | Platform-managed (mobile app notifications) | Always on where the app supports it — nothing to configure. |

## Before you start

You'll need **billing:manage** permission on your organisation to change provider settings (your
account admin has this by default — see [Managing Your Organisation](../organisation/managing-your-organisation.md)
if you need it granted). WhatsApp additionally requires an active WhatsApp subscription on your
account, on top of a connected number — see [Channels & Providers](configuring-channels.md).

## More guides coming

This section currently covers channel setup and templates. A guide to the notification-preferences
screen itself (turning individual notification types on/off, and — as channel selection is extended
to actually route between channels rather than only toggle email — picking which channel each type
uses) will be added once that work ships; see the Technical Guide's
[Notifications REST API](../../integrations/notifications-rest-api-integration.md) doc for the
current state if you need it sooner.
