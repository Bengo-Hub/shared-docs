# Monitoring

A live view of every notification your business has sent. Useful for confirming a specific
message actually went out, or spotting a channel that's failing before a customer complains about
never receiving something.

> **Direct link:** **Monitoring** in the sidebar. Visible to your account admin/manager by
> default; see [Before you start](#before-you-start) if you don't see it.

This page always shows your own organisation's activity. There's nothing here from any other
business on the platform, and nothing you do here is visible to them either.

## The overview cards

**Total Messages**, **Delivery Rate**, and **Error Rate**, plus a **Channel Distribution**
breakdown (Email/SMS/WhatsApp/Push), all scoped to the time window selected top-right: **24H** or
**7D**. These are a window into recent activity, not a lifetime total. A quiet 24 hours will show
zeros here even if your account has sent thousands of messages in the past. That's expected, not
a fault. Check the **Live Activity Feed** below (it uses the same selected window) if you're
trying to confirm something specific rather than read a general trend.

## Live Activity Feed

Every individual notification in the selected window, most recent first: which notification type,
which channel, the recipient, its status (**Sent**, **Delivered**, or **Failed**), and when. Filter
by channel or status using the dropdowns above the table, or click any row to see its full detail,
including the exact recipient address or number, useful when confirming *which* customer a message
went to.

## Before you start

Seeing this page requires **notifications:analytics.view** permission on your organisation. Your
account admin and manager roles have it by default; see
[Managing Your Organisation](../organisation/managing-your-organisation.md) if you need it granted
to another role.

## Common Issues

**A message I know was sent isn't showing up.** Check the selected time window (24H vs. 7D) first.
The feed only shows activity inside it, same as the cards above. If it's still missing after
widening the window, confirm which channel it went out on and whether that channel's filter is
active.

**Channel Distribution shows 0 for a channel I know is active.** This reflects real send activity
in the selected window, not whether the channel is *configured*. A correctly connected channel
with no recent traffic will legitimately show 0. See [Channels & Providers](configuring-channels.md)
to confirm configuration itself, separately from this page.
