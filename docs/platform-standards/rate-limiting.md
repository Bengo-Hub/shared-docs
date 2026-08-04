# Rate Limiting

## Status: implemented, but duplicated per-service — a real gap worth closing

Rate limiting exists at two layers today, and there's no single shared package for the application-layer piece — that's the gap.

## Layer 1: ingress-level (works well, no action needed)

Every service's ingress has `nginx.ingress.kubernetes.io/limit-rps` and `limit-connections` annotations, tuned per service (e.g. auth-api 20 rps / 100 connections; ordering-backend 50 rps / 200 connections). This is a solid first line of defense against abusive traffic before it even reaches a pod, and doesn't need a shared library — see [DevOps-K8s Ingress & CORS](../architecture/devops-k8s-ingress-cors.md) for the per-service annotation values.

## Layer 2: application-level (implemented twice, independently — should be one shared package)

- **treasury-api** (`internal/http/router/router.go`): `mw.NewRateLimiter(redisClient, log)` → `IPRateLimit(120, time.Minute)`, a flat 120 req/min per IP, with `X-RateLimit-*`/`Retry-After` response headers.
- **notifications-api** (`internal/shared/middleware/ratelimit.go`): a Redis sliding-window limiter keyed `ratelimit:{tenantID}:{feature}:{date}` via `INCR`, enforcing per-tenant/per-feature limits (e.g. `max_emails_per_day` sourced from the JWT's subscription claims — see [Trinity Authorization Pattern](../architecture/trinity-authorization-pattern.md)).
- Both `pos-api` and `inventory-api` also carry an Ent-generated `RateLimitConfig` entity, suggesting DB-configurable per-tenant limits were planned/partially built there too.

These are two genuinely different rate-limiting *shapes* (flat IP-based vs. per-tenant-per-feature sliding window) implemented independently in Go, in two different services, using the same Redis instance. **If you need application-level rate limiting in a new service, don't write a third implementation** — this is the platform's clearest case of a missing shared abstraction. Until `shared/ratelimit` exists, copy the notifications-api sliding-window pattern for per-tenant/per-feature limits (it's the more general of the two) rather than the flat treasury-api one, and consider whether it should be extracted into `shared/httpware` or a new `shared/ratelimit` package as part of the work rather than adding a third copy.

## Recommended next step

Extract a `shared/ratelimit` package from the notifications-api sliding-window implementation (it's the more general of the two shapes), migrate treasury-api's flat IP limiter onto it, and document the resulting single API here. This is tracked as a "must-have" item in the platform best-practices gap analysis.
