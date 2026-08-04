# Caching

## Status: implemented, reusable — use this instead of a bespoke cache

`shared/cache` provides a generic Redis-backed cache-aside helper, `Aside[T]`, with `GetOrSet`, `Invalidate`, and `InvalidatePattern` (SCAN+DEL, safe for wildcard invalidation), plus a `Key()` namespacing helper so cache keys stay consistent across services. It's backed by `github.com/redis/go-redis/v9` against the single shared `redis-master-0` instance in `infra`.

There's a companion `shared/cache/tenant.go` for tenant-specific caching (e.g. auth-api's tenant branding cache, read by every downstream service via `cache.GetTenantDetails()` rather than each service storing its own copy of branding data — see [Cross-Service Data Ownership](../architecture/cross-service-data-ownership.md)).

## Standard TTL tiers

Three named tiers, pick the one that matches your data's volatility rather than inventing a new duration:

| Tier | TTL | Use for |
|---|---|---|
| `TTLReference` | 5 min | Slow-changing reference data (tenant branding, catalog metadata) |
| `TTLModerate` | 1 min | Data that changes a few times a session (subscription/feature gates) |
| `TTLOperational` | 30 sec | Fast-changing operational state |

## Before writing a new cache

1. Check whether the data you want to cache is already cached upstream (e.g. tenant branding — don't re-cache what `cache.GetTenantDetails()` already provides).
2. Use `Aside[T]` rather than hand-rolling a `redis.Get`/`redis.Set` pair — it gets the get-or-set race and error handling right once, for everyone.
3. Always set an `InvalidatePattern` path for anything that changes via an event (e.g. invalidate `tenant:<slug>` on `auth.tenant.updated`) — a cache with no invalidation path is a slow-motion bug waiting for a support ticket about "stale data."

## Known gap

Redis runs as a single replica (`redis-master-0`) in prod with no HA/replica — a Redis restart currently means every service's cache cold-starts simultaneously. Not urgent (all cached data is a projection of a source of truth elsewhere, never the only copy), but worth knowing before assuming Redis is always warm.
