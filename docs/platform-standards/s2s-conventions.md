# Service-to-Service (S2S) Conventions

## Auth: one shared key, always

All Codevertex microservices share a single S2S API key environment variable: `INTERNAL_SERVICE_KEY`, sent as `X-API-Key: {INTERNAL_SERVICE_KEY}` on every S2S request. Never create per-service variants (`TREASURY_API_KEY`, `INVENTORY_SERVICE_API_KEY`, etc.) — every receiving service validates the incoming key against its own copy of the same shared value. Per-service *URL* env vars (`TREASURY_SERVICE_URL`, `INVENTORY_SERVICE_URL`, ...) are still separate, as expected.

## An API key does not identify a tenant

A valid service key tells the receiving service that the caller is trusted. It does not say which tenant the call is for, so every S2S call names its tenant explicitly: send `X-Tenant-ID` (and ideally `X-Tenant-Slug`) on every request, and never rely on the URL slug or the key alone.

## Subscription checks: use the tenant-scoped endpoint

`GET /api/v1/tenants/{tenantID}/subscription` — **never** the bare `/api/v1/subscription`, which resolves its tenant from JWT claims and will 404 (→ "subscription inactive" → requests blocked) on a pure API-key call with no JWT. Using the bare form on an S2S path with no JWT is a reliable way to silently block otherwise-valid requests.

## Internal DNS, not public hostnames

Intra-cluster S2S calls must use internal ClusterIP DNS (`{service}.{namespace}.svc.cluster.local`), not the public `*.codevertexafrica.com` hostname. A public-hostname round-trip adds real latency (Cloudflare edge + origin TLS handshake) and can cause elevated latency or intermittent timeouts under load on synchronous S2S paths — if a cross-service call that works most of the time occasionally times out, check whether it's routing over the public hostname instead of internal DNS before assuming it's a capacity problem. Auth is the one deliberate exception — auth calls stay on the public hostname because the JWT issuer must match what's embedded in tokens.

## Client structs: two silent-failure modes to watch for

1. **`encoding/json` silently drops fields with no matching struct tag.** A client struct that mirrors another service's response DTO just leaves a field zero-valued (no error) if that DTO grows a field your struct doesn't declare. Periodically diff any S2S client struct against the actual upstream DTO it mirrors.
2. **Case-insensitive tag matching can mask a snake_case/camelCase mismatch.** Go's JSON unmarshal matches field names case-insensitively when no exact tag match exists, so a struct with a wrong-cased or missing tag can "work" for some fields by accident while others end up zero-valued — this compiles and even passes some tests. Verify a new S2S client struct against a real call/response, not just that it compiles.

## Resilience

Wrap outbound S2S calls in `shared/service-client` (circuit breaker + retry + tracing) rather than a raw HTTP client — see [Resilience — Circuit Breakers & Retries](resilience-and-retries.md).
