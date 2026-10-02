# Rate Limiting

Rate limiting runs at two layers: the ingress in front of every service, and inside each service
through one shared module, `github.com/Bengo-Hub/shared-ratelimit`.

## Ingress level

Every service's ingress carries `nginx.ingress.kubernetes.io/limit-rps` and `limit-connections`
annotations (for example auth-api 20 rps / 100 connections). These counters live in each
ingress-nginx pod, so they are a coarse first line against floods, not an exact limit. See
[DevOps-K8s Ingress & CORS](../architecture/devops-k8s-ingress-cors.md) for the per-service values.

## Application level

Every Go service uses `shared-ratelimit` (v0.2+). There are no local limiters left in the fleet.

### Algorithm: GCRA in Redis

`Limiter` uses GCRA (generic cell rate algorithm) through `github.com/go-redis/redis_rate/v10`.
GCRA is the token bucket expressed as one timestamp per key: it allows a burst up to `Burst`
requests after an idle period, then `Limit` per `Window` on average. The whole check-and-consume
step is one Lua script that Redis runs atomically on its own clock, so every replica of a service
shares one exact limit with one round trip and one small key per subject.

| Algorithm | Why it is not used |
|---|---|
| Fixed window `INCR` | Allows twice the limit across a window edge. Still fine for daily quotas (see `Quota`). |
| Sliding window log (sorted set) | Exact, but one entry per request and three round trips; v0.1 also checked and recorded in separate calls, so parallel requests on different pods all passed. |
| Sliding window counter | Close approximation, but no burst allowance. |
| Leaky bucket as a queue | Delays requests instead of answering 429, wrong for an API. |

A concurrency test in the module runs 200 parallel requests through four limiter instances (four
pods) sharing one Redis at a limit of 50 and asserts exactly 50 pass.

### Client IP

`ratelimit.ClientIP` takes `X-Real-IP`, which ingress-nginx sets from `CF-Connecting-IP` (it only
trusts that header from Cloudflare's ranges), then `CF-Connecting-IP`, then the peer address.
`X-Forwarded-For` is never trusted: Cloudflare appends to whatever the client sent, so its first
entry is attacker-controlled. Mount `ratelimit.TrustedRealIP` instead of chi's `middleware.RealIP`,
which copies client-sent `True-Client-IP`/`X-Forwarded-For` into `RemoteAddr`.

### Usage

```go
limiter := ratelimit.NewLimiter(redisClient, log, "myservice")

// General per-IP limit. Mount it AFTER CORS so a 429 still carries CORS headers.
r.Use(limiter.Middleware(ratelimit.IPKey, 300, time.Minute))

// Login, PIN, OTP: per IP and per target identifier.
r.With(limiter.MiddlewareWith(ratelimit.CompositeKey(ratelimit.IPKey, accountKey),
    ratelimit.Options{Name: "login-ip-acct", Limit: 10, Window: 15 * time.Minute})).Post("/login", h)

// Outside HTTP (provider send budgets, workers):
ok, retryAfter := limiter.Allow(ctx, "smtp", ratelimit.Options{Name: "email-provider", Limit: 200, Window: time.Hour}, 1)
```

Tenant or user keys must come from verified claims (`ratelimit.ValueKey`), never a raw header:
anyone can send `X-Tenant-ID` and spend another tenant's allowance.

### Behavior

| Topic | Behavior |
|---|---|
| Headers | `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`; on 429 also `Retry-After` and `{"error":"rate limit exceeded",...}`. |
| Exempt by default | WebSocket upgrades, `Accept: text/event-stream`, `/healthz`, `/readyz`, `/livez`, `/health`, `/ready`, `/live`, `/metrics`. Kubelet probes share a node IP and must never get a 429. Add more with `Options.Skip` (pos-api skips its payment-status and catalog-version polls). |
| Redis down | Each pod falls back to an in-process bucket allowing `Limit / ExpectedReplicas` (default 2), bounded to 10,000 keys, so throttling continues without blocking real users. |
| Memory | GCRA keys expire when the bucket refills. Redis runs `allkeys-lru`. |

### Daily quotas

`Quota` meters plan features per tenant per UTC day (limit from JWT claims). One Lua call
increments, keeps the 25 hour TTL and rolls back on rejection. `CheckN(n)` is all-or-nothing for a
batch, so a send to 20 recipients either fits today's quota or consumes nothing.

## Brute-force protection

| Flow | Protection |
|---|---|
| auth-api login | Per IP (60/min), per IP and account (10 per 15 min), per account across IPs (30/hour). |
| auth-api one-time codes (OTP, email verify) | Atomic compare-and-consume; the 5th wrong guess destroys the code. Sends capped at 5 per 10 minutes. |
| pos-api, inventory-api PIN | 8 per IP per minute on PIN routes; pos counts PIN failures with an SQL increment and locks the member. |
| library-api PIN and card identify | 10 per IP per minute. |
| ticketing public tickets | 5 per IP per hour, 10 per email per day. |
| marketflow-ai public chat | 15 per IP and 100 per tenant per minute. |

## Non-Go services

TruLoad (.NET) uses ASP.NET's built-in rate limiter, per pod, behind the ingress limit. It runs after
authentication so every policy partitions per signed-in user, or per client IP (`X-Real-IP`) for
anonymous calls; the `auth` policy (per IP, no queue) covers login, 2FA, password and SSO
endpoints. Limits come from the database settings and an admin reload applies at once.

ISPBilling (FastAPI) keeps its counters in Redis (`app/core/rate_limit.py`, one atomic Lua call per
hit, so the limit holds across replicas). Credential endpoints (admin login, onboarding codes,
hotspot login, voucher redeem, PPPoE login) get two layers: per client IP at
`RATE_LIMIT_REQUESTS` per `RATE_LIMIT_WINDOW`, kept generous because hotspot customers often share
one public IP, and per account or email at 10 per 5 minutes. `RATE_LIMIT_ENABLED=false` turns it
off; a Redis outage lets requests through.
