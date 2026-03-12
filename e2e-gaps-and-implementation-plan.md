# E2E Gaps and Implementation Plan

**Last updated:** March 2026  
**Related:** [e2e-gap-analysis.md](./e2e-gap-analysis.md), [auth-ui/docs/e2eTests/](../auth-service/auth-ui/docs/e2eTests/), [ordering-frontend/docs/e2eTests/](../ordering-service/ordering-frontend/docs/e2eTests/)

## Summary

E2E tests (Playwright) exist for auth-ui and ordering-frontend against production. Manual runs confirm login and landing flows work. This doc lists **gaps**, **issues**, and a **plan** to address them.

---

## 1. Playwright / environment

| Gap | Severity | Description |
|-----|----------|-------------|
| Browsers not installed | P1 | First-time run fails with "Executable doesn't exist" until `npx playwright install` is run. |
| CI not wired | P2 | No CI job runs E2E; results are local only. |

**Plan:**

- Document in each app README or E2E README: "Run `npx playwright install` once before first `pnpm test:e2e`."
- Add CI job (e.g. GitHub Actions) that runs `pnpm test:e2e` for auth-ui and ordering-frontend on schedule or on release; publish HTML report as artifact; use env vars for credentials (no hardcoded secrets).

---

## 2. Auth-UI E2E

| Gap | Severity | Description |
|-----|----------|-------------|
| Post-login redirect | Info | Login redirects to `/` (home), not `/dashboard`. Tests updated to assert "away from login" and header/nav. |
| Login form below fold | Fixed | Selectors updated to `getByRole('textbox', { name: /email/i })` etc.; heading to `/sign in\|welcome back/i`. |
| Dashboard when unauthenticated | Pass | `/dashboard` redirects to `/login?return_to=/dashboard` — covered by RBAC spec. |
| **Tenant admin login failed** | **Fixed** | **Root cause:** Auth-api required a tenant slug; auth-ui defaulted to `codevertex` when URL had no `?tenant=`, so tenant-only users got invalid credentials. **Fix (real):** auth-api now resolves the tenant from the user's **primary_tenant_id** in the DB when `tenant_slug` is empty. auth-ui sends empty `tenant_slug` when there is no `?tenant=` in the URL. Tenant users can log in directly at `/login`; E2E uses `/login` with no query. See [sso-integration-guide.md — Login without tenant_slug](./sso-integration-guide.md#login-without-tenant_slug-tenant-resolved-from-users-primary-tenant). |
| **Auth-ui: "Log In" / "Start Free" still show after login** | **Fixed** | **Root cause:** (1) Session cookie was set without `Domain`, so when auth-ui (accounts.*) called sso.* for `/me`, the cookie was not sent (cross-subdomain). (2) useAuth only ran `/me` when we had storeUser or were on a protected route, so on public `/` we never hydrated from session. **Fix:** auth-api sets `Domain=.codevertexitsolutions.com` on the session cookie when request host is *codevertexitsolutions.com* so accounts and sso share the cookie. auth-ui useAuth now always runs `/me` on the client when enabled so we hydrate from session on every page (including `/`). |
| **Ordering-frontend: stays on landing, no authenticated menu after login** | **Fixed** | **Root cause:** After SSO callback we exchange code for tokens and poll ordering-backend `GET /api/v1/{tenant}/auth/me`. If the user is not yet synced (NATS/JIT), we get 404 and eventually set `status: "authenticated"` with no user, so the header still shows unauthenticated. **Fix:** When ordering-backend `/auth/me` fails after retries, we fall back to SSO `GET /api/v1/auth/me` with the access token and map the response to AuthResponse so we set user and show authenticated navbar/dashboard. Same fallback added in `initialize()` when app loads with persisted session but ordering /auth/me fails. |

**Plan:**

- No further auth-ui test changes for current behaviour. If product later redirects to `/dashboard` after login, add assertion for `/dashboard` and "Welcome" text.

---

## 3. Ordering-frontend E2E

| Gap | Severity | Description |
|-----|----------|-------------|
| Base URL includes tenant | Info | baseURL is `.../urban-loft`; tests use `goto('/')` and `goto('/menu')`. Assertions use flexible text (Sign in, menu, cart). |
| SSO login from ordering not covered | Done | E2E `ordering-authenticated-requests.spec.ts` covers full SSO login from ordering → accounts → callback → back; asserts ordering-backend `/auth/me` and `/customers/orders/summary` return 200. |
| **Ordering 401 on GET /auth/me** | **Fixed** | E2E run (March 2026): ordering-backend `GET /auth/me` returned 401. **Fix:** ordering-backend router was skipping auth middleware for any path containing `/auth/`. Protected routes `GET /auth/me` and `POST /auth/logout` must go through auth middleware; skip only webhooks, config, cafes, menu. See `ordering-backend/internal/http/router/router.go` and [ordering-authenticated-requests-e2e.md](../ordering-service/ordering-frontend/docs/e2eTests/ordering-authenticated-requests-e2e.md). |
| Subscription gating not covered | P2 | No assertion that subscription-api is called or that EXPIRED → redirect to subscribe. |
| Cart → checkout → payment not covered | P2 | No full flow; depends on ordering-api and treasury. |

**Plan:**

- Add one E2E that starts on ordering-frontend, clicks Sign in, completes login on accounts, and asserts return to ordering (tenant slug in URL, or dashboard).
- When subscription-api is stable: add test or fixture for tenant with EXPIRED subscription and assert redirect to subscribe page.
- Cart/checkout E2E: add after ordering-api and payment flows are stable; can start with "add to cart" and "Open cart" visibility, then extend to checkout and network assertions for payment intent.

---

## 4. Artifacts and docs

| Gap | Severity | Description |
|-----|----------|-------------|
| Screenshots in repo | Low | Screenshots/traces live in `playwright-report/` and `test-results/` (gitignored). Docs link to these paths; no committed screenshots. |
| Network/console in docs | Done | Docs describe how to open trace (network, console); real run results note key requests (e.g. GET /api/v1/auth/me 200). |

**Plan:**

- Optional: CI uploads `playwright-report` to internal artifact store and posts link in PR comment. No change to local paths.

---

## 5. Other UIs (treasury, pos, notifications, subscriptions, inventory, logistics, rider-app)

| Gap | Severity | Description |
|-----|----------|-------------|
| No E2E yet | Addressed | Playwright E2E (smoke: SSO login + landing) added to treasury-ui, pos-ui, notifications-ui, subscriptions-ui, inventory-ui, logistics-ui, rider-app. Each has `playwright.config.ts`, `e2e/sso-login-and-landing.spec.ts`, and `docs/e2eTests/README.md`. Production base URLs per [sso-integration-guide.md](sso-integration-guide.md) (e.g. books, pricing, riderapp). |
| Login flow alignment | Addressed | [login-flow-contract.md](login-flow-contract.md) defines canonical signatures and platform vs tenant scope. Logistics-ui aligned to `redirectToSSO(returnTo?, tenant?)` and `handleSSOCallback(code, callbackUrl, tenantSlug?)`; notifications-ui and subscriptions-ui support optional `tenant`; treasury/pos/inventory pass `tenant` into `buildAuthorizeUrl` so token is minted for the correct org. Seed updated: logistics-ui has tenant-pattern redirect URIs. |

**Plan:**

- Run smoke E2E locally for each app (e.g. `pnpm test:e2e` with `BASE_URL` and credentials). Extend to assert no 401 after login (e.g. GET /auth/me or service /me) where applicable.
- Add CI job for all E2E-capable UIs; archive HTML report.

---

## 6. Implementation checklist

- [x] Auth-ui: fix selectors and post-login assertions; document real results and artifact paths.
- [x] Ordering-frontend: document real results and artifact paths.
- [x] Add e2e-gaps-and-implementation-plan.md (this file).
- [x] **E2E real UX:** Auth-ui tests use only email+password (no tenant in URL); auth-api resolves tenant from primary_tenant_id. See [sso-integration-guide.md — Uniform SSO integration standard](./sso-integration-guide.md#uniform-sso-integration-standard-all-services).
- [x] **401 and authenticated requests:** Doc [SSO-AUTHENTICATED-REQUESTS-AND-401.md](./SSO-AUTHENTICATED-REQUESTS-AND-401.md) added; ordering-frontend E2E spec `ordering-authenticated-requests.spec.ts` asserts GET /auth/me returns 200 after full SSO login.
- [ ] **Next:** Run `npx playwright install` in auth-ui and ordering-frontend, then run `pnpm test:e2e` and confirm all pass.
- [ ] **Next:** Add CI job for auth-ui and ordering-frontend E2E; archive HTML report.
- [ ] **Backlog:** Ordering-frontend subscription gating E2E when subscription-api is ready.
- [ ] **Backlog:** Cart/checkout/payment E2E when APIs and test data are ready.
- [x] **Smoke E2E for other UIs:** treasury, pos, notifications, subscriptions, inventory, logistics, rider-app have Playwright smoke specs and docs; see [login-flow-contract.md](login-flow-contract.md) and each app's `docs/e2eTests/README.md`.
- [ ] **Backlog:** Per-UI E2E assert no 401 after login (e.g. GET /auth/me) per SSO-AUTHENTICATED-REQUESTS-AND-401.md where service exposes /me.

---

## 7. Backend DTO and frontend type alignment

Frontends must consume backend response keys as returned (camelCase in JSON). Mismatches cause missing profile data or incorrect auth state.

| Service | Status | Notes |
|---------|--------|--------|
| ordering-backend ↔ ordering-frontend | Aligned | AuthResponsePayload / UserResponsePayload use camelCase (accessToken, fullName, tenant_id, tenant_slug). Frontend AuthResponse and UserProfile match. |
| auth-api (SSO) /me | Mapped | ordering-frontend fetchProfileFromSSO maps SSO response (profile.name, roles, permissions) to UserProfile. |
| treasury, pos, subscriptions, inventory, logistics | To audit | Each backend should expose session + user + tenant_id/tenant_slug with camelCase; frontends should define types that match. See [SSO-AUTHENTICATED-REQUESTS-AND-401.md](./SSO-AUTHENTICATED-REQUESTS-AND-401.md). |

---

## References

- [sso-integration-guide.md](./sso-integration-guide.md)
- [login-flow-contract.md](./login-flow-contract.md)
- [SSO-AUTHENTICATED-REQUESTS-AND-401.md](./SSO-AUTHENTICATED-REQUESTS-AND-401.md)
- [TRINITY-AUTHORIZATION-PATTERN.md](./TRINITY-AUTHORIZATION-PATTERN.md)
- [e2e-gap-analysis.md](./e2e-gap-analysis.md)
- Auth-ui E2E: [auth-ui/docs/e2eTests/](../auth-service/auth-ui/docs/e2eTests/)
- Ordering-frontend E2E: [ordering-frontend/docs/e2eTests/](../ordering-service/ordering-frontend/docs/e2eTests/)
