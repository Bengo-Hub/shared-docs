# Webhooks vs Polling

## Status: webhooks used correctly where it matters; most remaining "polling" is legitimate fallback, not an anti-pattern

## Where webhooks are used (correctly)

treasury-api exposes a no-auth, signature-verification-only `/api/v1/webhooks` route group for both M-Pesa (Daraja callback) and Paystack — see [Payment Workflow](../integrations/payment-workflow.md). Payment status updates flow in via webhook, not polling, as the primary path.

## Where "polling" exists and why it's usually fine

An audit found that most backend polling loops in the fleet are a **legitimate fallback**, not a missed webhook opportunity:

- **M-Pesa reconciler** and the **eTIMS retry worker** poll because the external gateway (Safaricom, KRA) doesn't reliably webhook every state transition — a poller closes the gap for STK pushes or eTIMS transmissions that never got a callback.
- POS's catalog version-poll (`/pos/catalog/version`, ~45s interval) is a deliberate lightweight-freshness-check design, not a missed real-time opportunity — it's cheap, and the terminal is cache-first (IndexedDB) so staleness between polls is invisible to the cashier.

## Where it's a real gap

Real-time push (a WebSocket "wake up and refetch" hub, reusing the existing KDS/print-agent Hub + Redis relay pattern) replaced a naive poll for at least one high-value path: kitchen print-job delivery was intermittently failing because a long-poll got cancelled by a client-side timeout shorter than the server's poll window — the fix was a real-time wake-up socket (`printing.Hub`), not a shorter poll interval. **If you're building a new "check for updates" loop, default to asking whether an existing NATS event already fires for the state change you care about, and push a lightweight "refetch" signal over WebSocket/SSE instead of polling** — only fall back to polling if the upstream truly can't push (an external gateway) or the cost of a short poll interval is genuinely negligible (the catalog-version case).

## Checklist before adding a new poller

1. Does an event already exist for this state change? If yes, subscribe to it (see [Idempotency & the Outbox Pattern](idempotency-and-outbox.md)) instead of polling.
2. Is the thing you're polling an external gateway that doesn't reliably callback? If yes, polling as a fallback (not the primary path) is the right call — document it as such so a future reader doesn't "fix" it into a bug.
3. If you do need a "wake the client up" mechanism, prefer a WebSocket/SSE push over a client polling on a fixed interval, especially for anything latency-sensitive (kitchen tickets, live status).
