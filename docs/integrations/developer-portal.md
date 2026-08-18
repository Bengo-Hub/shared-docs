# Developer Portal — Current State & Roadmap

The eTIMS external API (see [eTIMS API Quickstart](etims-api.md)) is the first fully-fleshed-out
integration built on this pattern — sandbox/production separation, a certification checklist
before go-live, usage-based billing. This page tracks what's ecosystem-wide (reusable for any
future integration, not just eTIMS) today, and what's roadmapped to make it a real multi-service
developer portal rather than a per-integration pattern repeated by hand each time.

## What exists today

- **Credentials**: `App` (auth-api) is the credential every integration issues today — GitHub-App-style
  `bng_app_*` tokens with scopes, an IP allowlist, and suspend/resume/rotate/revoke lifecycle
  actions. `APIKey` (older, hard admin-gated) still exists but new integrations should use `App`.
- **Environments**: `App.environment` (`sandbox`/`production`, default `sandbox`) — new credentials
  always start in sandbox; a platform admin promotes to production as a manual review action
  (`POST /admin/apps/{id}/promote`). No per-service certification automation yet outside eTIMS —
  see Roadmap below.
- **Developer role**: `developer` is a seedable tenant role (alongside `admin`/`manager`/`member`/etc.)
  a tenant admin can grant via the existing team-invite flow, scoped to reaching the Developer
  Portal UI without full tenant-admin access. It doesn't currently carry any extra backend
  permission beyond that — `App` management itself is tenant-membership-scoped, not role-scoped.
- **OAuth clients**: full Authorization Code + PKCE flow, `client_secret_basic` for confidential
  clients. No `client_credentials` (pure server-to-server, no user) grant yet.
- **Rate limiting**: a tenant's effective requests/minute ceiling is resolved from their plan's
  `tier_limits_json` first, falling back to a per-service `RateLimitConfig` row, then a hardcoded
  default (subscriptions-api `GET /tenants/{id}/rate-limit`) — built for the eTIMS API, but the
  resolver is generic across `service_name`, so any other integration can reuse it as-is.
- **Certification gate**: eTIMS's sandbox go-live checklist (device initialized, items registered,
  a stock movement, a handful of test sales — modeled on KRA's own OSCU certification session) is
  the only one that exists. It's implemented entirely inside treasury-api, not as a shared
  mechanism another service could plug into.

## Roadmap (documented, not yet built)

- **`client_credentials` OAuth grant** — pure S2S, no user in the loop, for integrations that
  don't need Authorization Code's browser redirect.
- **Generalized certification framework** — extract the eTIMS go-live checklist pattern
  (automated check + human reviewer, same two-layer gate KRA itself uses) into something any
  service can register its own checklist against, instead of copy-pasting treasury-api's
  approach per integration.
- **Dedicated lightweight developer signup** — today, getting a credential still means an
  existing tenant admin (or platform admin) creating one for you inside a full business
  `Tenant`. A solo API developer with no interest in the wider SaaS suite has no lighter path in.
- **Usage-based plan picker wired to entitlements** — subscriptions-service already has a working
  self-serve plan/subscribe/upgrade UI; wiring an API-only tenant's chosen plan directly into
  their `App`'s entitlements (rather than the current manual admin-driven plan assignment) closes
  the loop on true self-serve for API products beyond eTIMS.

## Related

- [eTIMS API Quickstart](etims-api.md) — the reference implementation this page generalizes from.
