# Rate Limiting

Rate limiting exists at two layers: ingress-level, in front of every service, and application-level, within specific services that need finer-grained control.

## Ingress-level

Every service's ingress carries `nginx.ingress.kubernetes.io/limit-rps` and `limit-connections` annotations, tuned per service (for example, auth-api at 20 rps / 100 connections, ordering-backend at 50 rps / 200 connections). This is the first line of defense against abusive traffic, applied before a request even reaches a pod — see [DevOps-K8s Ingress & CORS](../architecture/devops-k8s-ingress-cors.md) for the per-service values.

## Application-level

Application-level rate limiting lives in one shared module — [`github.com/Bengo-Hub/shared-ratelimit`](https://github.com/Bengo-Hub/shared-ratelimit) — with two primitives for two different problems. treasury-api and notifications-api each independently built one of these before the extraction; both now import the shared package instead of maintaining their own copy.

- **`ratelimit.Limiter`** — a Redis sliding-window request limiter (sorted-set log), for abuse throttling by IP or tenant. treasury-api's usage: `ratelimit.NewLimiter(redisClient, log, "treasury")` → `rateLimiter.Middleware(ratelimit.IPKey, 120, time.Minute)` — 120 req/min per IP, with `X-RateLimit-*` response headers and a 429 JSON body on rejection.
- **`ratelimit.Quota`** — a Redis daily usage-quota counter (`INCR`, calendar-day-bucketed key, ~25h expiry), for per-tenant/per-feature metering sourced from the tenant's subscription plan (e.g. `email_notifications_per_day` from the JWT's subscription claims — see [Trinity Authorization Pattern](../architecture/trinity-authorization-pattern.md)). notifications-api's usage: `ratelimit.NewQuota(redisClient)` → `quota.Check(ctx, tenantID, featureKey, limit)`, or `ratelimit.RequireQuota(quota, featureKey, claimsFn)` as middleware.

If you're adding application-level rate limiting to a new service: import `shared-ratelimit` rather than writing a third implementation. Use `Limiter` for abuse/traffic protection (the limit is a fixed config value, not tied to a plan); use `Quota` for plan/feature metering (the limit comes from the caller's subscription tier via JWT claims).
