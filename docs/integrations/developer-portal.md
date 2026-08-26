# Developer Portal: Current State and Roadmap

The eTIMS external API (see [eTIMS API Quickstart](etims-api.md)) is the first fully fleshed out
integration built on this pattern: sandbox/production separation, a certification checklist
before go-live, and a real-time prepaid token-bucket billing gate. This page tracks what's
ecosystem-wide today, reusable for any future integration and not just eTIMS, and what's
roadmapped to make it a real multi-service developer portal rather than a per-integration pattern
repeated by hand each time.

## What exists today

**Apply for access.** [accounts.codevertexafrica.com/developer/apply](https://accounts.codevertexafrica.com/developer/apply)
is a public, no-login form where a prospective developer picks exactly one service (Treasury/eTIMS,
Notifications, or SSO/OAuth) and submits contact details plus their self-serve or assisted mode.
This creates an `IntegrationRequest` (`service_access_<service>`) reviewed by a platform admin.
Approving a request with no existing tenant auto-provisions a sandbox `App` scoped to that one
service, a `developer`-role login, and the matching docs-access grant in one pass, so a
prospective developer doesn't separately re-request docs visibility after getting a credential.
Email hosting is deliberately not part of this flow. It's a per-mailbox tenant subscription
product with its own purchase flow (see [Email Hosting](email-hosting.md)), not an
external-developer API surface.

**Credentials.** `App` (auth-api) is the credential every integration issues today, a
GitHub-App-style `bng_app_*` token with scopes, an IP allowlist, and suspend, resume, rotate, and
revoke lifecycle actions. `APIKey`, an older and more hard-gated credential type, still exists but
new integrations should use `App`. A tenant-type `App` is enforced server-side to carry scopes for
exactly one service. A hand-crafted request spanning two service prefixes is rejected, not just
discouraged by the picker UI.

**Environments.** `App.environment` is `sandbox` or `production`, defaulting to `sandbox`. New
credentials always start in sandbox, and a platform admin promotes to production as a manual
review action (`POST /admin/apps/{id}/promote`). For the eTIMS API specifically, a sandbox
credential is now actively enforced downstream, not just a label: treasury-api rejects any
sandbox-credential call that would trigger a real KRA transmission against a tenant that already
has a production-configured device. `EtimsDevice.environment` (sandbox or production, per
registered device) remains a separate, deliberately decoupled axis. Promoting an eTIMS partner's
`App` to production still changes nothing about which KRA environment their devices transmit to;
that's governed by the certification checklist and which `EtimsDevice.environment` they
registered. Promotion also publishes `auth.app.promoted_to_production`, which subscriptions-api
consumes to auto-provision a zero-balance token wallet for the promoted tenant and service (see
the billing entry below). The wallet row exists immediately, though the tenant still has to
subscribe to a plan or top up before their balance is non-zero.

**Billing (eTIMS API).** A real-time, request-blocking prepaid token bucket
(`ApiTokenWallet`/`ApiTokenTransaction` in subscriptions-api, generalized by `service_tag` so a
future integration can reuse the same primitive). Every external API call spends tokens weighted
by what it actually costs to serve, enforced by treasury-api's `ExternalAPIKeyAuth` middleware
before the handler, and therefore before any real KRA call, runs. Calls that turn out not to have
done real work are refunded automatically. Full detail is in [eTIMS API Quickstart](etims-api.md)'s
Pricing section. This replaced an earlier post-paid monthly-overage model that never actually
gated a request in real time.

**Sandbox simulation (eTIMS).** A brand-new developer with a sandbox credential but no real KRA
sandbox TIN yet can use `/external/etims/sandbox/{devices,items,stock-io,sales}` to fake a full
certification pass. It's Redis-backed, expires after 72 hours, is never written to the real
device, item, or invoice tables, and is only reachable until a real device is registered for that
tenant. See [eTIMS API Quickstart](etims-api.md) for the exact flow.

**Developer role.** `developer` is a seedable tenant role, alongside `admin`, `manager`, `member`,
and others, that a tenant admin can grant via the existing team-invite flow, scoped to reaching the
Developer Portal UI without full tenant-admin access. It doesn't currently carry any extra backend
permission beyond that. `App` management itself is tenant-membership-scoped, not role-scoped.

**OAuth clients.** Full Authorization Code plus PKCE flow, with `client_secret_basic` for
confidential clients. There's no `client_credentials` grant yet for pure server-to-server
integrations with no user in the loop.

**Rate limiting.** A tenant's effective requests-per-minute ceiling is resolved from their plan's
`tier_limits_json` first, falling back to a per-service `RateLimitConfig` row, then a hardcoded
default (subscriptions-api `GET /tenants/{id}/rate-limit`). It was built for the eTIMS API, but the
resolver is generic across `service_name`, so any other integration can reuse it as is.

**Certification gate.** eTIMS's sandbox go-live checklist (device initialized, items registered, a
stock movement, a handful of test sales, modeled on KRA's own OSCU certification session) is the
only one that exists. It's implemented entirely inside treasury-api, not as a shared mechanism
another service could plug into.

## What's real today vs. what's scaffolded

Only the eTIMS API has a working scope-checking consumer (`etims:read`/`etims:write` on
treasury-api's `/external/etims/*`). A service-access request for Notifications or SSO is
reviewed, and auto-provisions a credential and docs access the same way, but that credential
currently has no live external endpoint to call yet. That's an honest platform-maturity gap, not
something this request flow hides. Applying still gets a prospective developer a real reviewer
conversation and, once one exists, a head start on the credential.

## Roadmap (documented, not yet built)

- **`client_credentials` OAuth grant.** Pure server-to-server, no user in the loop, for
  integrations that don't need Authorization Code's browser redirect.
- **Generalized certification framework.** Extract the eTIMS go-live checklist pattern, an
  automated check plus a human reviewer, the same two-layer gate KRA itself uses, into something
  any service can register its own checklist against, instead of copy-pasting treasury-api's
  approach per integration. The sandbox-simulation mechanism is eTIMS-specific for the same
  reason. It isn't yet a shared pattern another service could plug into either.
- **Live external endpoints for Notifications and SSO.** The request, credential, and docs-access
  pipeline is ready for these today. What's missing is a real scope-checking consumer on those
  services' own APIs (see "What's real today" above).
- **Dedicated lightweight developer signup.** Partially addressed by the public apply form above,
  but approval still provisions a full business `Tenant` behind the scenes. A solo API developer
  with no interest in the wider SaaS suite still ends up with a `Tenant` record, just one they
  never interact with directly.
- **Self-serve plan picker for an existing tenant's second product.** A brand-new, API-only tenant
  can already self-serve subscribe to `ETIMS_API_BASIC`/`GROWTH`/`SCALE` directly, since
  subscriptions-api's `POST /subscription` is plan-agnostic. What's still manual: an existing
  Codevertex customer, already on a PowerSuite, POS, Duka, or Dawa plan, who also wants external
  API access needs a platform admin to attach the second product via the `ProductSubscription`
  overlay. There's no self-serve UI flow for that case yet.
- **Tenant-facing token wallet UI.** The balance, transactions, top-up, and estimate API is live
  (see the billing entry above and [eTIMS API Quickstart](etims-api.md)), but subscriptions-ui,
  treasury-ui, and the auth-ui Apps & Keys console don't yet surface a wallet-balance widget or
  top-up button. Today a developer has to call the API directly to see their balance.

## Related

- [eTIMS API Quickstart](etims-api.md), the reference implementation this page generalizes from.
