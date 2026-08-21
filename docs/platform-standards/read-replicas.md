# Read Replicas

## Status: implemented, opt-in per endpoint — narrow scope today, reusable pattern

A Postgres streaming replica (`postgresql-replica`, in `infra`) exists primarily as an HA standby, but a handful of specific, heavy, staleness-tolerant read endpoints route to it instead of the primary via a dedicated PgBouncer alias. This is an **opt-in, per-endpoint** pattern, not a general read/write split — most traffic still goes through the primary, and that's deliberate: only route an endpoint here once it's actually shown to be a heavy, latency-insensitive read.

## The pattern

1. **PgBouncer alias.** `devops-k8s/manifests/databases/pgbouncer.yaml` defines a `<service>_ro` database alias pointed at `postgresql-replica.infra.svc.cluster.local` instead of the primary `postgresql.infra.svc.cluster.local` — same dbname, different upstream host, its own (smaller) `pool_size`.
2. **Config field.** The service's `PostgresConfig` gets a `ReadOnlyURL string` field (`envconfig:"POSTGRES_READONLY_URL"`), left empty by default. Empty is the default in every environment that hasn't explicitly set it, including local dev.
3. **Wiring in `app.go`.** A second Ent client (`readOrmClient`) is opened against `ReadOnlyURL` only if it's set; if the replica connection fails at startup, the failure is logged and swallowed, not fatal — the service falls back to using the primary client for that traffic, identical to before the read client existed. This fallback-by-default design means wiring the field into a service's `values.yaml` (via an `optional: true` `secretKeyRef`) is safe to deploy before the corresponding secret key is ever populated.
4. **Wiring in the handler/service.** Only the specific heavy read path calls `SetReadClient(readOrmClient)` (or is passed the read client directly) — everything else on that service, including any single-row detail lookup that happens to share the same function, stays on the primary. See `inventory-api/internal/modules/items/service.go`'s `ListItems` (routes its multi-row catalog-search branch to the read client, but a `?id=` single-item lookup deliberately stays on the primary — same function, different Ent client, chosen deliberately in code, not automatically) and its companion test, `read_replica_routing_test.go`, for the reference implementation and the reasoning for that split.

## Where this is live today

| Service | Endpoint | Alias |
|---|---|---|
| `inventory-api` | `ListItems` catalog search/list (POS terminal, Add Sale, catalog browse) | `inventory_ro` |
| `pos-api` | All-Sales list/export | `pos_ro` |
| `treasury-api` | AR/AP aging reports, customer/vendor statement, bank-reconciliation unmatched-lines list (`arpa`/`reconciliation` modules' `SetReadClient`) | `treasury_ro` |

## Before routing a new endpoint to the read replica

- Confirm the endpoint is read-only, high-volume or high-latency-cost, and tolerant of the replica's (normally sub-second) streaming lag — never route anything that reads-after-write in the same request, or anything financial/authoritative that must reflect the primary at the instant of the read.
- Add the `<service>_ro` alias to `pgbouncer.yaml` if one doesn't already exist for your service, sized well below the alias's own connection budget (see the `inventory_ro`/`pos_ro` pool-size comments in that file for the reasoning and a real incident where an undersized pool queued behind another service's S2S timeout).
- Follow the same three-step wiring above — config field → optional secret-backed env var → explicit opt-in at the one call site — rather than making the read client the service's default Ent client.
- The replica is a **PostgreSQL streaming replica with no automatic failover** — a manual-promotion runbook exists for the primary-down case, but the replica itself is not a load-scaling cluster and shouldn't be treated as one for capacity planning.
