# SRDD fact-check checklist (verify against the local Codevertex repos)

The SRDD was drafted in a cloud session that could reach **this `shared-docs` repository only**, not the service codebases under `D:\Projects\Codevertex\`. The ecosystem facts it states come from:
- `docs/architecture/`
- `docs/integrations/`
- `internal/platform-standards/`
- `processa-integration/architecture/`

Confirm each item below against the service code, then either tick it or correct the SRDD and rebuild the PDF.

Status key:
- **Documented:** stated in shared-docs, so only confirm it still matches the code.
- **Conflict:** shared-docs disagrees with itself.
- **Assumed:** not found in shared-docs; inferred or proposed.
- **Extension:** new work the SRDD requires from a Codevertex service.

| # | SRDD claim | SRDD § | Status | Where to check locally | ✓ |
|---|---|---|---|---|---|
| 1 | OIDC endpoints `GET /api/v1/authorize`, `POST /api/v1/token`, `POST /api/v1/auth/refresh`, `GET /api/v1/auth/me`, `/.well-known/openid-configuration`; RS256 JWKS; 15 min access and 7 day refresh tokens | 14, 31.2 | Documented | `auth-service/auth-api` router, token config | ☐ |
| 2 | OIDC client registration by seed (`cmd/seed/main.go`) with `/{tenant}/auth/callback` and `/auth/callback`; `aelia-ui` as a public PKCE client | 14, 19.2 | Documented | `auth-api/cmd/seed/main.go` | ☐ |
| 3 | Staff MFA can be asserted to relying parties (`amr`/`acr` claim) so AELIA can enforce MFA for admin roles | 31.2, REG-08 | **Assumed** | auth-api JWT claims struct and MFA flow; if absent, list it as an auth-api extension | ☐ |
| 4 | `auth.user.created` and `auth.user.login` are published on plain NATS, not JetStream | 15.1, 23.2 | Documented | auth-api event publisher | ☐ |
| 5 | Notifications send endpoint `POST /{tenantId}/notifications/messages`, `Idempotency-Key` (24 h), `202 {status, requestId}` | 14, 24 | Documented | notifications-api handlers | ☐ |
| 6 | Notifications production host is `notificationsapi.codevertexafrica.com` | 24 | **Conflict** | shared-docs has both `notificationsapi.` (integration guide, CORS doc) and `notifications.` (microservice architecture domain table); check devops-k8s ingress | ☐ |
| 7 | Notifications can consume `aelia.>` and render `aelia/*` templates through its gating registry | 14, 23.3 | Documented pattern | notifications-api consumer registry | ☐ |
| 8 | Subscriptions S2S `GET /api/v1/tenants/{tenantId}/subscription`; `GetEntitlements` / `ConsumerHasFeature` S2S calls | 14, 24 | Partly documented (path of `GetEntitlements` not documented) | subscriptions-api routes, `shared-service-client` | ☐ |
| 9 | Consumer-scoped plans keyed `aelia:brand:{id}` (brand plans without auth tenants) | 14, 20.1 | **Extension** | subscriptions-api consumer model; otherwise use the `builtin.plans` adapter | ☐ |
| 10 | AELIA tenant can hold a **Treasury-only** entitlement (no wider ERP) | Decisions D5, 14 | Assumed | subscriptions plan catalogue: is there a treasury-only plan code? | ☐ |
| 11 | Treasury payment intents `POST /api/v1/{tenant}/payments/intents` (`source_service` required), `/initiate`, `/confirm-manual`, `/check-status`; pay page and `TreasuryPaymentModal` | 14, 33.2 | Documented | treasury-api payments module | ☐ |
| 12 | Treasury S2S **payout API** (`POST /api/v1/{tenant}/payouts` with idempotency key) callable by other services | 33.3 | **Extension** (shared-docs only says "S2S: disburse payout") | treasury-api payouts module | ☐ |
| 13 | Payout engine payee types include riders, suppliers, staff and equity holders; add `creator` | 33.3 | From the feasibility report | treasury-api payee-type enum | ☐ |
| 14 | Service-charge split exists (platform vs tenant); extend to a three-way split | 14, 33.3 | Documented (two-way) plus **Extension** | treasury `service_charge_amount` / `net_amount` logic | ☐ |
| 15 | Paystack transaction **split codes** supported on the funding leg | 33.1, 33.2 | **Assumed** | treasury Paystack gateway (`internal/modules/gateways/paystack.go`) | ☐ |
| 16 | Tenant-owned Paystack config (`/gateways/paystack/config`, `metadata.collected_by`) usable for AELIA's merchant account | 33.1 | Documented | treasury gateway config | ☐ |
| 17 | Event names `treasury.payment.succeeded/failed`, `treasury.payout.completed`, `treasury.refund.completed`, `treasury.etims.*`; **payout failure event name** | 23.2 | Documented except the payout-failure subject | treasury `shared-events` publishers; run `tools/event-subject-coverage.sh` | ☐ |
| 18 | Treasury approvals of payouts require OTP (`428` without code) | 21.1, 31.2 | Documented (POS QA history) | treasury approval middleware | ☐ |
| 19 | MarketFlow Vera agent-run API usable by AELIA with its own tool set, scoped to the AELIA tenant | 14, 17.1 | **Assumed** interface | marketflow-ai agent runtime | ☐ |
| 20 | MarketFlow social connect covers Facebook Pages and TikTok business only (ads scopes), not Instagram or YouTube | 14 | From the feasibility report | marketflow social-connect module | ☐ |
| 21 | Stack versions: Go 1.26, chi v5, Ent v0.14.5, Atlas v1.1.0, Next.js 16.2, React 19.2, Tailwind v4 | 12.3 | Documented (processa doc) | any current Go service `go.mod`, ui `package.json` | ☐ |
| 22 | Shared libs `shared-auth-client`, `shared-service-client` (gobreaker 5 failures, 10 s timeout), `shared-events` (outbox, `processed_events`), `httpware`, `cache` `Aside[T]`, `shared-ratelimit`, `pagination`; `@bengo-hub/shared-ui-lib` `SSOLoginModal` and `TreasuryPaymentModal` | 12.3, 15.1 | Documented | shared libs repos | ☐ |
| 23 | Middleware order: rate limit → auth → `RequireActiveSubscriptionForMutationsWithGrace` → JIT → context → permission | 21 | Documented | `shared-auth-client` | ☐ |
| 24 | devops-k8s generic chart `charts/app`, `apps/{svc}/{app.yaml,values.yaml}`, `replicaCount: 2`, PDB, HPA; cert-manager `letsencrypt-prod`; `fleet-health-watcher` alerting | 36, 37 | Documented | `devops-k8s` | ☐ |
| 25 | MinIO available for AELIA media (`aelia-media-{env}` bucket) with server-side encryption | 12.2, 20.1 | Assumed configuration | devops-k8s MinIO setup | ☐ |
| 26 | Production hosts `app.<aelia-domain>` and `api.<aelia-domain>` | 19.2, 36.1 | **Placeholder** | AELIA to confirm the registered domain | ☐ |

When an item changes the SRDD:
1. Edit `AELIA-Creator-Commerce-System-Requirements-and-Design.md`.
2. Run `npm run charts` if requirement tags changed.
3. Run `npm run build`.
4. Commit the updated markdown and PDF together.
