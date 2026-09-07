# Channels & Providers

Settings → Providers is where you connect your own Email, SMS, and WhatsApp sender, and where you
can send a live test message to confirm it works.

## Email

Connect SMTP (any mailbox — Gmail, Zoho, your own domain) or Brevo. Fields:

| Field | Notes |
|---|---|
| SMTP Host / Port | Port 465 = SSL, port 587 = STARTTLS. Most providers use one of these two. |
| Username / Password | Your mailbox credentials. |
| From Address | What recipients see as the sender. |

If you don't connect your own, email still sends — from the platform's shared sender.

## SMS

Connect your own Africa's Talking account (username, API key, Sender ID). If you don't, SMS still
sends — through the platform's shared shortcode.

## WhatsApp

Connect via **Connect WhatsApp Number** (a guided popup through Meta — no copying tokens by hand)
where available, or ask your account contact to set your **Phone Number ID** manually as a fallback.

### Why WhatsApp has no shared fallback

Unlike Email and SMS, WhatsApp doesn't have a "platform default" you'll silently fall back to.
Two things are required before any WhatsApp message will send for your account:

1. **An active WhatsApp subscription** — a small monthly plan sized to your expected message
   volume (see [Subscriptions & Billing](../subscriptions-and-billing.md)).
2. **Your own connected WhatsApp Business number.**

This is deliberate, not a gap: a WhatsApp Business number carries your business's own verified
identity and message history — there's no equivalent to a "shared shortcode" that would make sense
for it. If either requirement isn't met, WhatsApp sends for your account simply don't go out (every
other channel keeps working normally) rather than silently going out under someone else's number.

### Testing a connection

Once connected, use **Test Connection**: leave the recipient blank to just verify your credentials
(checks your number's status with Meta, no message sent), or enter a real phone number to send an
actual test message and confirm delivery end to end.

## Choosing which channel(s) a notification uses

Each notification type (order confirmed, invoice sent, OTP, and so on) can be turned on or off per
channel from your notification preferences. Today, most notification types are wired to send on one
primary channel (usually email); as WhatsApp and SMS templates roll out for more notification types
(see [Message Templates](message-templates.md)), this becomes a genuine choice — which channel(s) a
given type actually reaches will expand type by type as its templates go live on each channel, not
all at once.
