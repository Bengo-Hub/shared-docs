# Idempotency & the Outbox Pattern

## Status: implemented, reusable — but with one catastrophic footgun to know about

`shared/events` implements the full transactional-outbox pattern used fleet-wide: each service writes to its own `outbox_events` table in the **same DB transaction** as the domain write, and a background poller (`poller.go`) publishes those rows to NATS JetStream asynchronously, deleting each row once published ("prune-on-publish"). This guarantees a domain write and its event either both happen or neither does — no dual-write race between "save to DB" and "publish to NATS."

Idempotency on the consuming side is handled by `shared/events/idempotency.go`'s `IdempotencyStore`, backed by a `processed_events` table with composite primary key `(event_id, consumer)`:

- `Claim` — an atomic `ON CONFLICT DO NOTHING` insert, race-safe across replicas. Use this for irreversible side effects (payouts, GL postings) where two replicas processing the same event concurrently would double-execute.
- `AlreadyProcessed` / `MarkProcessed` — a process-then-mark pattern for idempotent-but-cheap-to-check handlers.

## THE OUTBOX ENVELOPE LAW — read this before writing to `outbox_events` by hand

The poller reconstructs the event **solely** from the `outbox_events.payload` column via `FromJSON(payload)` → `Subject()`. The payload column **must hold the full `Event.ToJSON()` envelope** — `id`, `event_type`, `aggregate_type`, `aggregate_id`, `tenant_id`, `payload`, etc. — never just the inner business payload.

If you write a bare business payload into that column (e.g. while seeding test data or writing a one-off recovery script), `FromJSON` parses it into an empty `Event`, `Subject()` resolves to `"."`, the publish to `"."` "succeeds" against no subscribed stream, and prune-on-publish **deletes the row as if it had been delivered — with zero trace, not even a FAILED row.** This isn't a hypothetical edge case: a service whose outbox ever receives a bare-payload row can lose its entire event history silently and unrecoverably — there's no error, no FAILED marker, and no way to detect it after the fact other than noticing that a downstream consumer has stopped seeing that service's events at all.

**If you ever need to insert an outbox row manually (a data-repair script, a backfill), always write the complete envelope, and consider testing it against a non-prod stream first.**

## `aggregate_id` must be a valid UUID

The poller scans `outbox_events.aggregate_id` (varchar) into a `uuid.UUID`. A single non-UUID value in that column jams the **entire poller for that service** — not just the bad row, everything behind it in the queue too. If a service's events stop publishing entirely with no obvious error, check for a non-UUID `aggregate_id` row first.

## NATS subject convention

Subjects are built as `{aggregate_type}.{event_type}` — never pass an event type that already includes the aggregate prefix (`NewEvent("treasury.etims.invoice_transmitted", "treasury", ...)` produces the doubled, dead subject `treasury.treasury.etims.invoice_transmitted`). Pass the bare type (`etims.invoice_transmitted`). Full convention, envelope field names, and durable-consumer gotchas: see [Event Architecture](../architecture/event-architecture.md).

## New consumer checklist

1. Use `shared-events` `QueueSubscribe` (queue-grouped, multi-replica safe) for anything that must survive a rolling deploy without dropping messages — a bare `js.Subscribe`/`conn.Subscribe` is at-most-once and loses messages across replica restarts unless you have a specific, audited reason not to (a few webhook relay paths do, deliberately, to avoid double-POSTing an external endpoint — that's the exception, not the default).
2. If the side effect is irreversible (money movement, external API calls), wrap it in `IdempotencyStore.Claim` before acting, not after.
3. Extend `shared-docs/tools/event-subject-coverage.sh` (a CI-gateable linter that scans all Go backends for published-vs-subscribed NATS subjects) when adding a new event type, so orphan publishes get caught automatically rather than discovered in an incident.
