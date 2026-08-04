# N+1 Queries & Preloading

## Status: handled via Ent's generated idioms at hot paths — no shared abstraction needed, but discipline matters

There's no shared "preloading" package on this platform, and none is really needed: every Go service uses [Ent](https://entgo.io/) as its ORM, and Ent's generated query builders already provide the tools to avoid N+1 — the discipline is in using them consistently at hot paths, not in building new infrastructure.

## The pattern: `.IDIn()` for batch loading

Ent's generated `.IDIn(...)` bulk-ID-filter idiom is used extensively across the fleet's hot paths (pos-api's order/payment/booking queries, inventory-api's stock service) to batch-load related entities by a collected set of IDs instead of querying once per row in a loop. If you're writing a new list/report endpoint that needs related data per row (e.g. a line item's product name, a booking's outlet), collect the IDs first and batch-load with `.IDIn()` rather than calling `.Query()` inside a `for` loop.

## A related but distinct footgun: Ent's `Sum()`/`Count()`/aggregate collision

Not N+1, but a similar "found via a real production bug" gotcha: `entgo.io/ent`'s generated `Sum(field)` emits a raw, unaliased `SUM("field")` — fine with one aggregate, but **two or more `Sum()`/`Count()`/`Max()`/`Min()`/`Mean()` calls in the same `Aggregate()`/`GroupBy().Aggregate()` query all collide on the same unaliased column name**, silently dropping data for every aggregate after the first (no compile error, sometimes no runtime error — just missing data in the UI). If a query needs more than one aggregate, use `entsql.As(entsql.Sum(s.C(field)), "alias")` (import `entsql "entgo.io/ent/dialect/sql"`) so each aggregate gets its own column name. See `inventory-api/internal/modules/reports/ingredient_utilization.go`'s `sumAs()` helper for the reference implementation, and [Go Backend — Ent + Atlas Migrations](../architecture/go-backend-ent-atlas-migrations.md) for more Ent-specific gotchas found in production.

## When reviewing a new list/report endpoint

Ask: does this loop over rows and issue a query (or S2S call) per row? If yes, either batch-load via `.IDIn()` (same-service data) or check whether the S2S client already supports a bulk-fetch endpoint before adding a per-row S2S call in a loop — the latter is the same N+1 problem one network hop further out, and is usually more expensive than the DB-level version.
