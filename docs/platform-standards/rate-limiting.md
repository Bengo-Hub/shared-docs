# Rate Limiting

Rate limiting exists at two layers: ingress-level, in front of every service, and application-level, within specific services that need finer-grained control.

## Ingress-level

Every service's ingress carries `nginx.ingress.kubernetes.io/limit-rps` and `limit-connections` annotations, tuned per service (for example, auth-api at 20 rps / 100 connections, ordering-backend at 50 rps / 200 connections). This is the first line of defense against abusive traffic, applied before a request even reaches a pod — see [DevOps-K8s Ingress & CORS](../architecture/devops-k8s-ingress-cors.md) for the per-service values.

## Application-level

Two existing patterns, depending on what you need:

- **Flat per-IP limiting** (treasury-api, `internal/http/router/router.go`): `mw.NewRateLimiter(redisClient, log)` → `IPRateLimit(120, time.Minute)` — a flat request-per-minute cap per IP, with `X-RateLimit-*`/`Retry-After` response headers.
- **Per-tenant, per-feature limiting** (notifications-api, `internal/shared/middleware/ratelimit.go`): a Redis sliding-window limiter keyed `ratelimit:{tenantID}:{feature}:{date}` via `INCR`, enforcing limits sourced from the tenant's subscription plan (e.g. `max_emails_per_day` from the JWT's subscription claims — see [Trinity Authorization Pattern](../architecture/trinity-authorization-pattern.md)).

If you're adding application-level rate limiting to a new service, the sliding-window, per-tenant/per-feature pattern is the more generally useful of the two — follow that shape unless you specifically need a flat per-IP limit.
