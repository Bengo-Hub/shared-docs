# E2E Production Gap Analysis — March 2026

**Last Updated**: March 9, 2026 (audit completed against MVP Production Ready Plan).

## Executive Summary

Production readiness is **blocked by DNS** for auth subdomains (see bengobox-mvp-production-test-report.md). Once DNS is configured for auth and API subdomains, E2E testing can proceed. **Current status**: Backend APIs (ordering, inventory, treasury, logistics, subscriptions, pos) may return 503 if containers are not running; auth-api/auth-ui returning 404 or "Non-existent domain" when DNS is not set.

**Audit Results (March 9, 2026)**: Comprehensive codebase audit completed against MVP Production Ready Plan. Treasury-api has full Paystack/M-Pesa/COD webhook implementation with `source_service` tracking, equity holders/royalties, and payout config. Treasury-ui has platform/tenant routes wired with analytics. Cafe-website admin dashboard has service shortcuts to canonical URLs. Ordering-frontend has E2E customer flow (payment polling, tracking) mostly implemented per sprint-6. See detailed findings below.

## Correct Production Domains (canonical — see plan Part C)

| Service | API domain | UI domain | Notes |
|---------|------------|-----------|--------|
| Treasury | booksapi.codevertexitsolutions.com | books.codevertexitsolutions.com | |
| Cafe website | — | theurbanloftcafe.com | |
| Ordering | orderingapi.codevertexitsolutions.com | ordersapp.codevertexitsolutions.com | |
| Subscription | pricingapi.codevertexitsolutions.com | pricing.codevertexitsolutions.com | |
| Inventory | inventoryapi.codevertexitsolutions.com | inventory.codevertexitsolutions.com | |
| Logistics | logisticsapi.codevertexitsolutions.com | logistics.codevertexitsolutions.com | |
| Auth | sso.codevertexitsolutions.com (API) | accounts.codevertexitsolutions.com | DNS must be configured per bengobox-mvp-production-test-report.md |
| Rider app | — | riderapp.codevertexitsolutions.com | |
| Notifications | notificationsapi.codevertexitsolutions.com | notifications.codevertexitsolutions.com | |
| POS | posapi.codevertexitsolutions.com | pos.codevertexitsolutions.com | |

**Status**: Auth subdomains (auth/authapi) returning "Non-existent domain" until DNS is fixed. Backend 503s indicate containers not running; re-trigger CI deploy. See mvp-critical-path.md for current service state matrix.

## UI Apps Status (updated March 9)

| UI App | Target Domain | Current State |
|--------|---------------|---------------|
| logistics-ui | logistics.codevertexitsolutions.com | SCAFFOLDED (Next.js app with SSO, platform admin, PWA; needs API wiring) |
| inventory-ui | inventory.codevertexitsolutions.com | SCAFFOLDED (Next.js app; needs API wiring) |
| subscriptions-ui | pricing.codevertexitsolutions.com | SCAFFOLDED (Next.js app; needs API wiring) |
| treasury-ui | books.codevertexitsolutions.com | **API-WIRED** (Next.js app with SSO; platform/tenant routes implemented; analytics, gateways, equity pages wired to treasury-api) |
| pos-ui | pos.codevertexitsolutions.com | SCAFFOLDED (Next.js app; needs API wiring) |

devops-k8s values.yaml created for: logistics-ui, inventory-ui, subscription-ui, treasury-ui.

## Critical Code Issues (Fixable Now)

### P0 — Launch Blockers

1. **Auth API down** — sso.codevertexitsolutions.com returns 404 on all endpoints including /.well-known/openid-configuration. This breaks SSO for ALL dependent services.

2. **7 backend APIs returning 503** — ordering, inventory, subscription, pos, logistics, treasury containers are not running. Need restart/redeploy.

3. **ordering-frontend: API URL** — Set `NEXT_PUBLIC_API_URL` in production (e.g. `https://orderingapi.codevertexitsolutions.com/api/v1/`). **Done**: Mock data removed; landing, menu, outlet, menu-discovery use tenant-scoped API (menu/items, menu/categories, cafes, featured). All paths include tenant slug.

4. **ordering-frontend: Landing page route /urban-loft returns 404**

5. **5 admin UIs need API wiring** — logistics-ui, inventory-ui, subscriptions-ui, treasury-ui, pos-ui are scaffolded (Next.js + SSO); must be wired to their backends (see mvp-critical-path.md).

### P1 — High Priority

6. **rider-app domain** — Production host is riderapp.codevertexitsolutions.com (devops-k8s values.yaml; no alternate domains).

7. **cafe-website auth broken** — OIDC depends on SSO being up (P0 #1).

8. **Staff dashboard uses dummy data** — Not connected to real APIs.

### P2 — Medium Priority

9. **PWA install prompts** — **Addressed**: ordering-frontend, rider-app, pos-ui, notifications-ui now re-prompt at least once every 30 minutes if not installed (localStorage dismiss + setInterval).
10. **Menu item images missing (placeholders)**
11. **Font preload warnings**

## Infrastructure Actions Required (DevOps)

1. Fix auth-api deployment (sso.codevertexitsolutions.com returning 404)
2. Restart/redeploy 7 backend services with 503 errors
3. Deploy actual subscription API behind pricingapi domain
4. Configure DNS for riderapp.codevertexitsolutions.com
5. Create devops-k8s configs for 5 new UIs (logistics-ui, inventory-ui, subscriptions-ui, treasury-ui)
6. Verify SSL certificates

## E2E Test Implementation (March 2026)

- **auth-ui:** Playwright E2E added; `auth-ui/e2e/sso-login-flow.spec.ts`, `sso-rbac-permissions.spec.ts`; docs under `auth-ui/docs/e2eTests/`. Run: `cd auth-service/auth-ui && pnpm test:e2e`.
- **ordering-frontend:** Playwright E2E added; `ordering-frontend/e2e/ordering-login-and-landing.spec.ts`, `ordering-workflows.spec.ts`; docs under `ordering-frontend/docs/e2eTests/`. Run: `cd ordering-service/ordering-frontend && pnpm test:e2e`.
- **Logout UX:** treasury-ui, pos-ui, notifications-ui, subscriptions-ui now have profile dropdown with Settings + Logout in header (aligned with cafe-website).

## Working Features Confirmed

- cafe-website: landing page, menu page (216 real items), mobile responsive, PWA manifest
- notifications-api: API docs accessible, health endpoints working
- auth-ui: Landing page loads with service directory
- ordering-frontend: Menu browsing, cart, auth UI work when API is available
- Busia location correctly shown, no Kiambu references

## Resolved / Done

- Menu–inventory SKU linkage (39 items, 7 categories; ordering ↔ inventory aligned).
- Cafe-website: dummy menu and useDummyData removed; menu and landing use only ordering-backend catalog; seed includes image_url per item (paths like /images/menu/…).
- API base URL redirect and OIDC discovery at root for auth-api.
- notifications-ui SSO (fetchProfile from SSO; redirect URIs).
- Rider-app domain in values (riderapp.codevertexitsolutions.com).
- DevOps: UI values.yaml and secret/config fixes.
- 5 admin UIs scaffolded (logistics-ui, inventory-ui, subscriptions-ui, pos-ui, treasury-ui).

## Fixes Applied (March 6, 2026)

- **API base URL routing**: All Go backends (auth-api, subscriptions-api, ordering, inventory, logistics, pos, notifications, treasury) now redirect root `/` to `/v1/docs/` to avoid 404 on base URLs.
- **SSO OIDC discovery**: auth-api serves `/.well-known/openid-configuration` and `/.well-known/jwks.json` at root (in addition to `/api/v1/`) so issuer `https://sso.codevertexitsolutions.com` works for OIDC clients.
- **notifications-ui SSO**: `fetchProfile()` fixed to call SSO `/api/v1/auth/me` instead of notifications API; OAuth seed redirect URIs expanded for all tenant slugs; swagger host typo fixed in notifications-api.
- **Rider-app domain**: values.yaml uses `riderapp.codevertexitsolutions.com` (ingress and NEXT_PUBLIC_APP_URL); only configured domains per values.yaml.
- **DevOps**: inventory-api secret name fixed (`inventory-api-secrets`); treasury-api duplicate autoscaling keys removed; 4 new values.yaml for logistics-ui, inventory-ui, subscription-ui, treasury-ui.
- **503 root cause**: Pods not running; CI/CD has not completed successful deploy (image tags still `latest`). Re-trigger deploy workflow per service to build, push, and sync ArgoCD.

## Ordering–frontend and backend alignment

- **Create order (DONE)**: Backend now exposes `POST /api/v1/{tenant}/orders` accepting `{ outletId, items, deliveryAddress, deliveryNotes, paymentMethod, promoCode? }` (outletId = cafe UUID). Frontend continues to call `POST /{tenant}/orders` with the same payload; ensure `outletId` is the cafe/outlet UUID from the catalog or outlets API (not a slug). Cart + `POST /checkout` remains available for alternative flows.
- **Cafe-website → ordering**: Cafe-website menu and featured items come from ordering-backend catalog. For “Order” actions, link to ordering-frontend (e.g. `ordersapp.codevertexitsolutions.com/urban-loft/menu`) so customers use the same cart/checkout flow and backend orders.

## Ordering–treasury and Paystack

- **Treasury**: Ordering-backend uses `internal/platform/treasury/client.go` for payment intents, M-Pesa STK, and webhooks. Supported providers: M-Pesa, Stripe, Paystack, Flutterwave, Manual. To use Paystack as default: set default payment provider in config/tenant or pass `provider: "paystack"` when creating intents; ensure treasury-api has Paystack configured and webhook URL registered.

## Menu-to-Inventory SKU Linkage (Completed March 6, 2026)

The ordering-backend seed now creates 7 menu categories and 39 menu items with SKUs that match the inventory-service seed 1:1. This enables end-to-end order→inventory flow:

- **SKU is the canonical cross-service reference** per CROSS-SERVICE-DATA-OWNERSHIP.md
- **Ordering-backend seed** (`cmd/seed/main.go`): seeds categories (hot-beverages, cold-beverages, pastries, sandwiches, salads, light-bites, breakfast) and 39 menu items with matching inventory SKUs for tenant "urban-loft" / outlet "Busia"
- **Inventory client** (`internal/platform/inventory/client.go`): already implemented with stock check, reserve, consume, release, and recipe lookup via shared-service-client
- **Inventory Recipe/BOM schema** (`inventory-api/internal/ent/schema/recipe.go`, `recipeingredient.go`): already implemented, links menu item SKU → raw ingredient items
- **All 39 SKUs aligned**: BEV-ESP-001 through BRK-OAT-001 are consistent across ordering-backend menu items, inventory-api items, and inventory balances

## E2E Implementation Audit (March 9, 2026)

### Treasury Service (treasury-api) - COMPLETE

**Paystack Implementation**: 
- ✅ Webhook endpoint `POST /api/v1/webhooks/paystack` with HMAC SHA512 signature verification
- ✅ Events handled: `charge.success`, `charge.failed`, `transfer.success`, `transfer.failed`
- ✅ Payment intents: create, initiate, confirm-manual
- ✅ Auto-generated webhook/callback URLs from `HTTP_PUBLIC_BASE_URL`

**Payout Configuration**:
- ✅ `GET /api/v1/{tenant}/payout/recipient-types` - Returns Paystack-supported types (kepss, mobile_money, mobile_money_business, nuban, ghipss, basa)
- ✅ `GET /api/v1/{tenant}/payout/schedule-types` - Returns schedules (instant, daily, weekly, monthly)
- ✅ `GET/POST /api/v1/{tenant}/payout/config` - Tenant payout configuration
- ✅ `GET /api/v1/{tenant}/payout/history` - Payout records

**Equity/Royalties**:
- ✅ `equity_holders` schema with `holder_type` (shareholder/royalty), `percentage_share`, `source_services`
- ✅ `equity_payouts` schema for tracking payout runs
- ✅ Platform routes for CRUD operations

**Money-by-Source Analytics**:
- ✅ `payment_transactions` has `source_service` field (indexed)
- ✅ `source_service` tracks originating microservice (ordering, subscriptions, pos, logistics, inventory)
- ✅ Analytics endpoints support filtering by `source_service`

### Treasury-UI - WIRED (Needs Testing)

**Tenant Dashboard** (`/[orgSlug]`):
- ✅ Dashboard with analytics summary and recent transactions
- ✅ Transactions list with filters
- ✅ Settlements/payout history
- ✅ Gateways page for tenant selection

**Platform Dashboard** (`/[orgSlug]/platform`):
- ✅ Platform gateways page (activate Paystack, M-Pesa, COD)
- ✅ Credentials management UI
- ✅ Equity page (holders, royalty config, payout run)
- ✅ Superadmin-only access protection

**Shared Pay Page**:
- ✅ `/(public)/pay` route exists for invoice-first payment flow

### Subscriptions-API - DOCUMENTED

**Subscription Types**: Product, Feature, and One-time subscriptions documented in plan.md
**Default Pricing**: 80k–2M KES tiering documented
**Treasury Integration**: `source_service` on billing events documented

**Gap**: Verify actual implementation of `source_service` emission in billing event code

### Ordering-Frontend E2E Flow - MOSTLY COMPLETE

**Auth**:
- ✅ Token stored in Zustand with localStorage persistence
- ✅ 401 interceptor clears session
- ✅ SSO/OAuth PKCE flow implemented

**Menu**:
- ✅ Categories/items from `GET /{tenant}/menu/categories` and `/items`
- ✅ Item detail with variants
- ✅ Cart badge shows live count

**Checkout**:
- ✅ Order submission with `idempotencyKey`
- ✅ Delivery address selection
- ✅ Payment method selection (M-Pesa default)

**Payment**:
- ✅ "Check your phone" screen for M-Pesa
- ✅ Poll order status every 3 seconds
- ✅ Timeout handling (2 min)

**Tracking**:
- ✅ Status timeline display
- ✅ Auto-poll every 10 seconds
- ✅ ETA display when `out_for_delivery`
- ✅ Rider name/phone when assigned

**Gaps**:
- ⬜ Payment failed retry option
- ⬜ Map placeholder (static map for MVP)
- ⬜ COD flow verification
- ⬜ Rating step implementation

### Cafe-Website Admin Dashboard - COMPLETE

**Service Shortcuts** (permission-gated tiles):
- ✅ Inventory: `https://inventory.codevertexitsolutions.com` (inventory:read permission)
- ✅ Ordering: `https://ordersapp.codevertexitsolutions.com` (orders:read permission)
- ✅ Logistics: `https://logistics.codevertexitsolutions.com` (riders:read permission)
- ✅ Treasury: `https://books.codevertexitsolutions.com` (staff role)

**Implementation**: `@/app/(dashboard)/dashboard/page.tsx` with `SERVICE_LINKS` array and `visibleServiceLinks` filtering based on `hasPermission(me, permission)`.

---

- **Ordering customer flow**: ordering-frontend `docs/sprints/sprint-6-mvp-launch.md` — CP-1 E2E Customer Flow Wiring (auth, menu, cart, checkout, payment, tracking). Completed: token/store, menu/categories/items, order submit with idempotency, checkout redirect; M-Pesa "check your phone" + poll; tracking timeline, ETA, rider; COD flow; rating step. Confirm delivery: order status moves to delivered via backend when logistics confirms; customer sees delivered state and rating CTA.
- **Ordering backend**: `ordering-backend/docs/sprints/sprint-9-mvp-launch.md` — E2E customer flow; cart/order endpoints; treasury integration.
- **Shared**: `shared-docs/mvp-critical-path.md` — E2E customer order flow and E2E rider delivery flow (P0); Sprint B/C checklists.
- **Blocker**: DNS for auth.codevertexitsolutions.com and authapi.codevertexitsolutions.com must be fixed before functional E2E (see bengobox-mvp-production-test-report.md).

## E2E Test Suite (March 2026)

Python-based E2E tests created for testing production endpoints using raw requests library.
Tests authenticate via SSO, fetch existing production data, and create new entries.

### Test File Locations

| Service | Test File | Test Count |
|---------|-----------|------------|
| **ordering-backend** | `ordering-service/ordering-backend/tests/test_ordering_workflows.py` | 12 tests |
| **treasury-api** | `finance-service/treasury-api/tests/test_treasury_workflows.py` | 11 tests |
| **subscriptions-api** | `subscriptions-service/subscriptions-api/tests/test_subscription_workflows.py` | 9 tests |
| **logistics-api** | `logistics-service/logistics-api/tests/test_logistics_workflows.py` | 10 tests |

### Test Structure (All Services)

**Phase 1: Authentication & SSO Integration** (5 tests)
- SSO health check
- OIDC discovery endpoint
- JWKS endpoint validation
- Login with credentials
- /me endpoint with permissions

**Phase 2: Data Fetching** (3-4 tests)
- Fetch existing menu items/categories/outlets (ordering)
- Fetch payment methods/transactions (treasury)
- Fetch subscription plans (subscriptions)
- Fetch fleet/riders/tasks (logistics)

**Phase 3: Workflow Tests** (3-4 tests)
- Health checks
- Create new entries using real fetched data
- Verify created entries
- Additional endpoint tests

### Running Tests

```bash
# Ordering service
cd ordering-service/ordering-backend/tests
python test_ordering_workflows.py

# Treasury service
cd finance-service/treasury-api/tests
python test_treasury_workflows.py

# Subscription service
cd subscriptions-service/subscriptions-api/tests
python test_subscription_workflows.py

# Logistics service
cd logistics-service/logistics-api/tests
python test_logistics_workflows.py
```

### Test Configuration

Each service has a `test_config.py` with:
- Production API URLs (verified from devops-k8s values.yaml)
- Auth service endpoints
- Test credentials (from environment variables)
- Default tenant (urban-loft)

### Production Domains Verified

All test configurations use verified production domains:
- Auth: `sso.codevertexitsolutions.com`
- Ordering API: `orderingapi.codevertexitsolutions.com`
- Ordering UI: `ordersapp.codevertexitsolutions.com`
- Treasury API: `booksapi.codevertexitsolutions.com`
- Subscription API: `pricingapi.codevertexitsolutions.com`
- Logistics API: `logisticsapi.codevertexitsolutions.com`
- Rider App: `riderapp.codevertexitsolutions.com`

---

## E2E Test Results (March 9, 2026)

### Test Run: ordering-backend

**Results**: 5/12 tests passed
- **Infra**: Fix auth-api deployment so sso.codevertexitsolutions.com serves discovery and token endpoints (see P0 #1).

### Ordering-frontend: replace mock data with backend

- **Current**: Landing page, outlet list, menu discovery, promo banners, saved addresses use mock/dummy data; `NEXT_PUBLIC_API_URL` defaults to `http://localhost:4000/api/v1/`.
- **Required**: Set production `NEXT_PUBLIC_API_URL` (e.g. `https://orderingapi.codevertexitsolutions.com/api/v1/`); wire landing to `GET /{tenant}/outlets`, catalog to `GET /{tenant}/catalog/items` and categories; use backend-seeded data for default tenant (urban-loft). Remove or gate mock fallbacks for production.

### Cafe-website: real API for menu (DONE)

- **Completed**: All dummy menu data and `useDummyData` logic removed. Menu and landing featured section load only from ordering-backend catalog API (`fetchCategories` + `fetchMenuItems`). `lib/dummy-data/menu.ts` now exports only display types (no arrays). Set `NEXT_PUBLIC_ORDERING_SERVICE_URL` in production to ordering API URL.

### Microservices without UI/frontend (scaffolded, need API wiring)

- **logistics-ui**, **inventory-ui**, **subscriptions-ui**, **pos-ui**, **treasury-ui**: All have Next.js apps with SSO; need to wire to their respective backend APIs (fleet/tasks, catalog/balances, plans, order entry, transactions). See mvp-critical-path.md Sprint B.
