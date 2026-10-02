# Scheduled Jobs and Migrations at Two or More Replicas

Every replica runs every ticker, cron loop and startup task. Without a guard, each scheduled
side effect (an email, an invoice, a charge, an event) happens once per pod, and again after every
restart. This page is the one way to guard them.

## Pick the guard

| Situation | Use |
|---|---|
| A sweep that runs on a timer (renewals, reminders, reconcilers, cleanups) | `sharedcache.ClaimPeriod(ctx, "svc:job", period)` as the first statement of the work function. The first replica to ask in a period wins; every other ask in that period (other pods, restarts, the startup run) gets false. |
| A job that must not overlap itself and may run long | `sharedcache.RunExclusive(ctx, rdb, log, key, ttl, fn)`: owner-token lease renewed every ttl/3; if the lease is lost the job's context is cancelled. |
| A job that must run once per period even when every pod wakes together (hourly backups) | `sharedcache.RunOnce(ctx, rdb, log, sharedcache.PeriodKey(prefix, period), period, fn)`: keeps the key after success so a late replica cannot repeat the period; a failure frees it for a retry. |
| One side effect per business event (notify SLA step X for task T, send the 7-day warning for billing period P, process sale S once) | `sharedcache.ClaimOnce(ctx, key, ttl)`. |
| A worker that picks rows | Claim rows atomically: `UPDATE ... WHERE id IN (SELECT ... FOR UPDATE SKIP LOCKED)` or a conditional state transition (`WHERE status = 'pending'`), and act only on rows you changed. |
| A counter that is read then written | Do the arithmetic in SQL (`count = count + 1 WHERE count < limit`) and check rows affected. |

Call `sharedcache.SetLeaseClient(redisClient)` once at startup. With Redis unconfigured (local
development) the claims always succeed; with Redis configured but unreachable they fail, so a tick
is skipped rather than run on every pod.

## Do not use session advisory locks through PgBouncer

PgBouncer runs in transaction pooling mode. A session `pg_try_advisory_lock` and its unlock can run
on different server connections: the lock leaks (the job silently stops for up to 30 minutes) or a
second pod "acquires" it on the same backend and runs in parallel. Every backup, period-close,
expiry and purge scheduler that used this pattern now uses the leases above.
`pg_advisory_xact_lock` inside a transaction is safe.

## Migrations

Each service's `cmd/migrate` runs from every pod's entrypoint before the server starts. It must:

1. connect with `POSTGRES_MIGRATE_URL` (direct to Postgres, never PgBouncer);
2. hold `pg_advisory_lock(<service key>)` on one pinned connection for the whole run, so pods wait
   for each other instead of racing the same DDL;
3. exit non-zero on failure.

There is no second migration path: the in-app `Schema.Create` calls and flags
(`POSTGRES_RUN_MIGRATIONS`) were removed so the locked binary is the only writer of schema.

## Outbox publishing

`shared-events` claims outbox rows with `FOR UPDATE SKIP LOCKED` (v0.6.2+) and sets `Nats-Msg-Id`
on every JetStream publish (v0.7.0+), so a row republished after a crash is dropped by the server.
Consumers still need idempotency for redeliveries (see [Idempotency & the Outbox
Pattern](idempotency-and-outbox.md)).
