# Swagger/OpenAPI Docs Gating

## The pattern: filter by tag, unlock by app secret

Every public-facing Codevertex service's `/v1/docs` (Swagger UI) and `/api/v1/openapi.json` follow the same shape, implemented independently but identically in `treasury-api`, `auth-api`, and `notifications-api` (`internal/http{,api}/handlers/swagger.go` + `swagger_filter.go` in each):

1. **Classify every operation's tag as external or internal** in a small `map[string]bool` at the top of `swagger.go`. External tags are the service's real product surface for outside developers (e.g. treasury's `External eTIMS API`/`Public Payments`/`Health`, auth's `Auth`/`OAuth`/`Discovery`/`Health`, notifications' `Notifications`/`Health`). Everything else — tenant-operational endpoints, platform-admin endpoints — is internal by default.
2. **`filterSpecToTags(spec, allowed)`** (pure, unit-tested, identical in all three services) returns a shallow copy of the spec with `paths` filtered to only operations carrying an allowed tag. Both the full and external-only specs are computed once at startup and cached — every request is a map lookup, never a re-parse.
3. **The docs page's own token bar** — not Swagger UI's built-in Authorize dialog — is what actually unlocks anything. Paste an app secret (`bng_app_...`, or a plain `bng_...` developer key), and the page's own JS `fetch()`s `/api/v1/openapi.json` with it as `X-API-Key`, both for the initial spec load and via `requestInterceptor` on every subsequent "Try it out" call. Swagger UI's own Authorize dialog only ever affects `Try it out`, never the initial (unauthenticated) spec fetch — using a plain `url:` loader there would never unlock anything.
4. **`OpenAPIJSON` resolves the secret server-side and is the sole source of truth.** It reports its decision back via two response headers the docs page reads to drive its badges: `X-Docs-View: internal|external` and `X-Docs-Environment: sandbox|production|none`. The client never decides trust on its own.

## Why an app secret, not a JWT

Earlier versions of this pattern (treasury-api's first cut) let staff paste their session JWT to unlock the internal view. Replaced fleet-wide after user feedback: a JWT is too long to comfortably copy-paste into a docs page. An app secret is short, and — because `App.app_type` already distinguishes `platform` (cross-tenant S2S/staff) from `tenant` — it doubles as the credential for the sandbox/production badge too, so one paste box drives both unlocks instead of needing two different mechanisms.

## The two independent unlocks, and what actually decides each

Both come from one call to `shared-auth-client`'s `APIKeyValidator.ValidateAPIKeyFull` (already published, no per-service reimplementation needed) — or, for auth-api specifically, an in-process equivalent (`APIKeyHandler.ResolveAnyToken`), since auth-api validating a secret against itself over HTTP would be a pointless round-trip:

- **Internal/full spec visibility** — `result.Roles` contains `"superuser"`, which `ValidateAppToken`/`resolveAPIKeyToken` in auth-api only ever sets for a **platform-type** App (or a plain developer key created with a non-empty `service` field). A tenant-scoped App's secret, however privileged within its own tenant, never unlocks this — its whole relationship to the API is the external surface.
- **Sandbox/production badge** — `result.Environment`, the App's own `environment` field. This was silently dropped by `shared-auth-client`'s `APIKeyValidationResult` until `v0.12.0` (2026-08-20) — if you're consuming this library and `Environment` always reads empty, check you're on `v0.12.0`+.

No literal second "sandbox server" URL is invented anywhere in `servers[]`. There's only ever been one real host per service; sandbox-vs-production has always been a credential-level distinction enforced by the handlers themselves (see treasury-api's `internal/platform/sandbox` package), not a routing one — the badge reflects that truthfully instead of adding a fake base URL a developer could point real tooling at by mistake.

## Adding this to a new service

1. Classify your spec's tags into `externalDocTags`.
2. Copy `swagger_filter.go` verbatim (it's pure and has no service-specific logic).
3. Copy `swagger.go`'s `renderDocsHTML` verbatim — it only takes a `title` string.
4. Wire `resolveAppSecretOptional` to either a `shared-auth-client` `APIKeyValidator` pointed at `AUTH_SERVICE_URL` (the normal case) or, if you *are* auth-api, the in-process resolver.
5. Add unit tests mirroring `swagger_filter_test.go`/`swagger_privilege_test.go` in any of the three existing services — anonymous → external tags only; invalid secret → external tags only; valid platform secret → full spec; valid tenant secret → external tags + production badge only if `environment=production`.
