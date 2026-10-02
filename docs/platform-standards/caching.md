# Caching

## Status: implemented, reusable. Use these instead of a bespoke cache.

`github.com/Bengo-Hub/cache` (`shared/cache`) has every caching building block the fleet uses:

| Need | Use | Bounded by |
|---|---|---|
| Shared read cache seen by every pod | `GetOrSet` (Redis cache-aside) | Redis `maxmemory 3gb` + `allkeys-lru`; every key has a TTL |
| Expensive aggregate (dashboards, reports) | `GetOrSetStale` (stale-while-revalidate) | same; TTL = fresh + stale window |
| Per-pod cache (API keys, settings, templates, clients) | `NewLocal[K, V](maxEntries, ttl)` | hard entry cap, least recently used evicted, expired entries purged |
| Redis client | `NewRedis(ctx, RedisConfig)` | pool, 500 ms read/write timeouts |

There is also `shared/cache/tenant.go` for tenant branding (`cache.GetTenantDetails()`): do not
re-cache what it already provides. See [Cross-Service Data Ownership](../architecture/cross-service-data-ownership.md).

## Standard TTL tiers

| Tier | TTL | Use for |
|---|---|---|
| `TTLReference` | 5 min | Slow-changing reference data (tenant branding, catalog metadata) |
| `TTLModerate` | 1 min | Data that changes a few times a session (subscription/feature gates) |
| `TTLOperational` | 30 sec | Fast-changing operational state, dashboard aggregates |

## How entries are added, expire, get evicted and invalidated

- **Add.** `GetOrSet` reads Redis; on a miss it fetches and writes `SET key value EX ttl`. Concurrent
  misses for one key in a pod share one fetch (single-flight), run on a context detached from the
  first caller so one cancelled request cannot fail the others. Values over 1 MB are returned but
  not cached, so one huge report cannot push thousands of hot keys out.
- **Expire.** Redis drops keys at their TTL.
- **Evict under pressure.** Redis runs `maxmemory-policy allkeys-lru`: when full it evicts the least
  recently used keys of any kind. Everything built on it tolerates that (a lost cache key is a miss,
  a lost lease ends the job, rate-limit state falls back per pod), which is why every key must carry
  a TTL and stay small.
- **Invalidate.** `Invalidate(ctx, keys...)` deletes keys (and their stale-while-revalidate copies).
  `InvalidatePattern(ctx, "inv:items:<tenant>:*")` walks with `SCAN` and frees with `UNLINK`.
- **Per-pod caches.** A `Local` cache on one pod cannot be cleared from another pod by itself. When a
  write must take effect everywhere at once, publish a [Broadcaster](realtime-fanout.md) message and
  `Delete` in its handler (pos-api's outlet-setting and maintenance caches, every service's API-key
  cache on revocation). Keep the TTL as the backstop.

Never hand-roll `map` + mutex caches: they only skip expired entries on read and never remove them,
so they grow with every distinct key (the auth-client API-key cache also had no lock and could crash
a pod with "concurrent map writes"; fixed in auth-client v0.15.0).

## Dashboard aggregates

Heavy aggregate endpoints use `GetOrSetStale` with `TTLOperational`. The key must carry every
dimension the result depends on: tenant, outlet filter, the user when an own-records RBAC scope
applies, and the requested window (a date, not `now`, for "today so far"). pos-api's dashboard
summary is the reference: a cashier's own figures are never served to a manager.

## Media (images, logos, documents)

Uploaded media is cached at three layers, closest to the user first:

1. **Device.** Each PWA's service worker loads `sw-media.js` (canonical copy:
   `shared-ui-lib/pwa/sw-media.js`): a bounded cache (400 files) for images from our APIs' `/media/`
   tree and `/_next/image`. It fetches in CORS mode so entries are not opaque (opaque entries are
   padded by megabytes of quota) and never stores `no-store` or `private` responses.
2. **Edge.** Cloudflare caches image extensions by default and honors the origin headers below.
3. **Origin.** `httpware.StaticMedia` serves `/media/*`:
   - fingerprinted names (UUID or long hash, as every upload handler writes) get
     `public, max-age=31536000, immutable`; other names `public, max-age=86400,
     stale-while-revalidate=604800`; a strong ETag makes revalidation a 304;
   - `Access-Control-Allow-Origin: *` so service workers can store them;
   - no directory listings, no dotfiles, no path escapes; a sandbox CSP for SVG/HTML/XML;
   - `MediaOptions.Private` marks sensitive trees `private, no-store` (logistics KYC uploads,
     every hospital patient photo); those are never cached anywhere but the browser session.

Upload handlers must always write a new, unique file name; never overwrite a file in place under
an immutable name. library-api overwrites covers in place, so it serves them with
`Immutable: false`.

## Before writing a new cache

1. Check whether the data is already cached upstream.
2. Use `GetOrSet`/`GetOrSetStale`/`Local` rather than a hand-rolled `Get`/`Set` pair or map.
3. Give anything that changes through an event an invalidation path.
4. Treat cached data as a projection, never the only copy.
