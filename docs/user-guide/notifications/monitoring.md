# Monitoring

A live view of every notification your business has sent — useful for confirming a specific
message actually went out, or spotting a channel that's failing before a customer complains about
never receiving something.

> **Direct link:** **Monitoring** in the sidebar.

## The overview cards

**Total Messages**, **Delivery Rate**, and **Error Rate**, plus a **Channel Distribution**
breakdown (Email/SMS/WhatsApp/Push), all scoped to the time window selected top-right — **24H** or
**7D**. These are a window into recent activity, not a lifetime total: a quiet 24 hours will show
zeros here even if your account has sent thousands of messages in the past, which is expected, not
a fault — check the **Live Activity Feed** below (it uses the same selected window) if you're
trying to confirm something specific rather than read a general trend.

## Live Activity Feed

Every individual notification in the selected window, most recent first: which notification type,
which channel, the recipient, its status (**Sent**, **Delivered**, or **Failed**), and when. Filter
by channel or status using the dropdowns above the table, or click any row to see its full detail —
including the exact recipient address/number, useful when confirming *which* customer a message
went to.

## Common Issues

**A message I know was sent isn't showing up.** Check the selected time window (24H vs. 7D) first —
the feed only shows activity inside it, same as the cards above. If it's still missing after
widening the window, confirm which channel it went out on and whether that channel's filter is
active.

**Channel Distribution shows 0 for a channel I know is active.** This reflects real send activity
in the selected window, not whether the channel is *configured* — a correctly connected channel
with no recent traffic will legitimately show 0. See [Channels & Providers](configuring-channels.md)
to confirm configuration itself, separately from this page.
