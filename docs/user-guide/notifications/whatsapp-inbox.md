# WhatsApp Inbox

A shared, tenant-wide inbox for the WhatsApp conversations your business has with customers,
separate from the automated notifications covered elsewhere in this guide. Automated notifications
are one-way (order confirmed, invoice sent). The WhatsApp Inbox is where a customer's own message
to your business number shows up, and where your team replies.

> **Direct link:** the **WhatsApp Inbox** entry in the sidebar. It's only visible if you have
> access; see [Before you start](#before-you-start).

## Why this exists, not just WhatsApp Web

A phone number registered on WhatsApp's Cloud API, the way your business's WhatsApp number is
connected (see [Channels & Providers](configuring-channels.md)), can no longer be used through the
regular WhatsApp app or WhatsApp Web. Once a number is set up this way, the only way to see and
reply to messages sent to it is through software built on the same API. That's what this inbox is.
Nothing changes for your *customers*. They still message an ordinary-looking WhatsApp number from
their own phone as normal.

## Conversations list

Every customer who has messaged your WhatsApp number appears here, most recent first: contact
name (or phone number, if unsaved), a preview of the last message, when it arrived, and a status
dot showing whether the 24-hour reply window (below) is still open for that conversation.

Click a conversation to open the full thread and reply.

## The 24-hour reply window

WhatsApp only allows a business to send a **free-form reply** (whatever your staff type) within 24
hours of the customer's *last* message to you. Outside that window, WhatsApp requires a
pre-approved template, the same requirement covered in
[How the channels differ](message-templates.md#how-the-channels-differ). This inbox's composer
doesn't send those, so it disables the reply box entirely once the window closes, with a note
explaining why.

The window resets every time the customer messages you again. There's nothing to do on your end to
"reopen" it.

## Getting notified of a new message

If you have push notifications enabled on this device (see below), a new customer message shows a
real notification. Tap it and it opens straight to that conversation, the same way a real WhatsApp
notification would. Enable it from the banner shown inside the inbox itself the first time you
visit, or later from your browser's own site-notification settings if you dismissed it.

Without push notifications, new messages still show up in the conversations list and the unread
count. You just won't get an alert outside the tab.

## Before you start

Two separate permissions control access, since reading conversations and sending replies are
different levels of trust:

| Permission | Lets you |
|---|---|
| **View WhatsApp Inbox** | See the conversations list and read message threads. |
| **Reply to WhatsApp Inbox** | Additionally send replies. |

Both are granted per role from **My Organization → Team**; see
[Managing Your Organisation](../organisation/managing-your-organisation.md#team). Your account
also needs an active [WhatsApp subscription](whatsapp-subscription-billing.md) and a connected
WhatsApp number, same as any other WhatsApp send; see
[Channels & Providers](configuring-channels.md#why-whatsapp-has-no-shared-fallback).

## Common Issues

**A reply doesn't seem to send.** Check first whether the 24-hour window has closed for that
conversation. A banner above the composer says so, and the input is disabled. That's the most
common reason. If the window is open and it still doesn't go through, confirm your WhatsApp
subscription is active.

**No new-message notification arrived even though a customer messaged.** Push notifications are
per-device and per-browser. Confirm you accepted the prompt on *this* device, and that your
browser/OS notification settings for the site haven't been turned off separately.
