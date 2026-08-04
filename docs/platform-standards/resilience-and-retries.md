# Resilience — Circuit Breakers & Retries

## Status: implemented, reusable — this is one of the platform's strongest existing patterns

`shared/service-client` wraps every outbound HTTP call between services in a circuit breaker (`sony/gobreaker`) and an exponential-backoff retry (`cenkalti/backoff/v4`), plus OpenTelemetry tracing spans around every call. Use this for any new S2S HTTP client rather than a raw `net/http` client — it gets the failure-handling right once.

## Defaults

- **Circuit breaker:** trips after 5 consecutive failures by default (configurable `MaxRequests`, `Interval`, `TimeoutCB`, `ReadyToTrip`).
- **Retry:** 100ms initial interval, 5s max interval, 30s max elapsed time, 2.0 backoff multiplier, 0.5 randomization factor. Retries on 5xx and network errors; does **not** retry other errors (`backoff.Permanent` wraps them) — a 4xx from a well-behaved upstream won't be retried into a thundering herd.
- **Tracing:** every call gets a span via `otel.Tracer("shared-service-client")` with `http.method`/`http.url`/`service.name` attributes and error/status recording — this is also the platform's primary source of cross-service request correlation today (see [Observability](observability.md) for the bigger picture, including the gap this doesn't cover).

## When to use this vs. plain `net/http`

Any call from one Codevertex service to another (S2S) should go through `shared/service-client`. Calls to third-party APIs (Paystack, M-Pesa Daraja, KRA/GavaConnect) have historically used per-integration clients with their own retry/backoff logic (see the KRA eTIMS docs for that integration's specific self-healing counter/retry behavior) — there's no strong reason not to route those through `shared/service-client` too if you're writing a new one, but check the existing pattern for that specific gateway first since some (eTIMS) have gateway-specific retry semantics that don't map cleanly onto a generic backoff.

## What this doesn't give you

Circuit breakers and retries handle *transient* failure. They don't make an operation idempotent — if your S2S call has a side effect (creates a record, moves money), a retried request needs its own idempotency key handling on the receiving end. See [Idempotency & the Outbox Pattern](idempotency-and-outbox.md) and [S2S Conventions](s2s-conventions.md).
