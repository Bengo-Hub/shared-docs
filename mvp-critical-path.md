# BengoBox MVP Critical Path

**MVP Deadline**: March 17, 2026
**Last Updated**: March 6, 2026
**Active Outlet**: Busia (ONLY -- Kiambu is post-MVP)

**Progress (March 2026)**: **Default tenants:** Auth-api and notifications-api seeds use: Codevertex (platform), Masterspace (mss, masterspace.co.ke), Urban Loft (urban-loft, theurbanloftcafe.com), KURA (kura, kura.go.ke), UltiChange (ultichange, ultichange.org). Tenant slug must be consistent across auth-service and all services integrating with notifications. **devops-k8s:** Ingress CORS values added under `devops-k8s/apps/<app>/values.yaml` in this repo (copy to Bengo-Hub/devops-k8s). **CORS / ordering-frontend SSO:** Ordering-frontend was calling `http://localhost:4000` from production (ordersapp.codevertexitsolutions.com) because Next.js bakes NEXT_PUBLIC_* at build time and the Dockerfile had no build args. Fixed: ordering-frontend Dockerfile and build.sh now pass production API/SSO URLs as build args. Auth-api CORS: added explicit origins (ordersapp, theurbanloftcafe, notifications, logistics). Ordering-backend CORS: default AllowedOrigins corrected to frontend origins only (removed API host), added localhost:3001 for dev. See §9. **Cafe-website SSO:** NextAuth removed; login/signup and header "Login"/"Join" buttons now use direct SSO (PKCE): redirect to auth-service `/api/v1/authorize`, callback at `/auth/callback`, Zustand store; auth-api seed updated with cafe-website redirect_uris `{origin}/auth/callback` (public client). Post-login redirect: role-based default (staff→dashboard, others→profile); profile page added (fix 404). MVP launch sprint docs updated across cafe-website (D1 auth token, D2 role-based dashboard, D3/D5 ticked), ordering-frontend (idempotency key, 401 handler, checkout error state, sprint-6 ticked), ordering-backend (CORS, sprint-9 ticked), auth-api and notifications-ui (sprint-mvp-launch ticked). Builds: cafe-website, ordering-backend, ordering-frontend, treasury-api, notifications-api, inventory-api, logistics-api pass. **RBAC & data fetching:** auth-api seeds Permission + RolePermission (add/read/read_own/change/change_own/delete/manage/manage_own per resource: orders, menu, users, tenants, riders, inventory, settings, gateways), GET /me returns roles + permissions. Cafe-website: useMe() TanStack Query (5 min TTL), permission-based sidebar (orders:read, menu:read, inventory:read, riders:read, users:read) with fallback for staff when permissions empty; 404/unauthorized pages; dashboard fetches via TanStack Query. Ordering-backend: seed includes catalog:read_own, catalog:change_own for full 8-action set; Redis cache and NATS events in use. Ordering-frontend: useMe with TanStack Query TTL. Plan and sprint docs updated per service. **Seed/RBAC audit (notifications-api, treasury-api, logistics-api):** notifications-api has no local Role/Permission schema—RBAC delegated to auth-api JWT; documented in notifications-api sprint-1. treasury-api seed enhanced with MVP 8-action permissions for payments, transactions, gateways; finance_admin role updated. logistics-api has no local RBAC/seed yet—documented in plan.md and sprint-0 that RBAC is auth-api JWT and future seed must add tasks/riders/fleet permissions with 8-action set.

---

## 1. MVP Service Status Matrix

| # | Service | State | Production Domain | March 17 Readiness | Blocker? |
|:--|:--------|:------|:------------------|:--------------------|:---------|
| 1 | auth-api | DEPLOYED | `sso.codevertexitsolutions.com` | Root redirect to /v1/docs/, OIDC discovery at root; needs CI redeploy | No |
| 2 | auth-ui | DEPLOYED | `accounts.codevertexitsolutions.com` | Needs hardening (forgot-password flow, session edge-cases) | No |
| 3 | ordering-backend | DEPLOYED | `orderingapi.codevertexitsolutions.com` | Menu seed (39 items, 7 categories); GET /cafes (list outlets); public menu uses TenantID; media: ORDERING_MEDIA_ROOT, PVC /media, media/menu + placeholder; inventory client wired | No |
| 4 | ordering-frontend | DEPLOYED | `ordersapp.codevertexitsolutions.com` | **Live API**: All menu/outlets/categories/featured use tenant-scoped backend (no mock data). GET /cafes, GET /menu/items with TenantID; landing, menu, outlet, menu-discovery wired. E2E + mobile pass pending. | No |
| 5 | logistics-api | DEPLOYED | `logisticsapi.codevertexitsolutions.com` | Ready; base URL redirects to /v1/docs/ | No |
| 6 | rider-app | DEPLOYED | `riderapp.codevertexitsolutions.com` | Domain updated in values.yaml; Ready, 7 routes, PWA, proof-of-delivery | No |
| 7 | **logistics-ui** | SCAFFOLDED (code) | `logistics.codevertexitsolutions.com` | **Next.js app scaffolded** -- fleet, tasks, tracking, platform admin; needs API wiring | Partial |
| 8 | inventory-api | DEPLOYED | `inventoryapi.codevertexitsolutions.com` | Recipe/BOM schemas exist; SKU alignment with ordering complete; Busia warehouse seed | No |
| 9 | **inventory-ui** | SCAFFOLDED (code) | `inventory.codevertexitsolutions.com` | **Next.js app scaffolded** -- catalog, warehouses, adjustments, platform admin; needs API wiring | Partial |
| 10 | subscriptions-api | DEPLOYED | `pricingapi.codevertexitsolutions.com` | Root redirect to /v1/docs/; needs feature-gate caching (Redis TTL) | Partial |
| 11 | **subscriptions-ui** | SCAFFOLDED (code) | `pricing.codevertexitsolutions.com` | **Next.js app scaffolded** -- plans, usage, billing, platform plans/subs; needs API wiring | Partial |
| 12 | pos-api | DEPLOYED (foundation) | `posapi.codevertexitsolutions.com` | Base URL redirects to /v1/docs/ | Partial |
| 13 | **pos-ui** | SCAFFOLDED (code) | `pos.codevertexitsolutions.com` | **Next.js app scaffolded** -- order entry, tables, drawer, platform; needs API wiring | Partial |
| 14 | notifications-api | DEPLOYED | `notificationsapi.codevertexitsolutions.com` | Ready; fetchProfile fix (SSO /auth/me); swagger host typo fixed | No |
| 15 | notifications-ui | DEPLOYED | `notifications.codevertexitsolutions.com` | SSO integration fixed (profile from SSO); OAuth redirect URIs expanded for all tenants | No |
| 16 | treasury-api | DEPLOYED | `booksapi.codevertexitsolutions.com` | Base URL redirects to /v1/docs/; treasury-ui scaffolded | No |
| 17 | **treasury-ui** | SCAFFOLDED (code) | `books.codevertexitsolutions.com` | **Next.js app scaffolded** — transactions, settlements, gateways, platform; **shared pay page** `/pay` (gateway picker, modals with QR and “I paid at till”); see payment-workflow.md | Partial |
| 18 | cafe-website | DEPLOYED | `theurbanloftcafe.com` | **SSO fix**: refresh URL must use `/api/v1/token`. **Real API**: set `NEXT_PUBLIC_USE_DUMMY_DATA=false`, wire menu to ordering-backend (catalog.ts). Auth fails when auth-api returns 404 (P0) | Partial |

### Legend

- **DEPLOYED**: Running in K8s, APIs reachable
- **SCAFFOLDED**: Repo exists with boilerplate, routes defined, no business logic
- **NOT STARTED**: No repo or only a placeholder

### MVP UI Status (March 6 update)

All five admin UIs are now scaffolded with production-ready Next.js apps (SSO/PKCE, multi-tenant [orgSlug], platform admin sections, PWA). Each has Dockerfile, build.sh, .github/workflows/deploy.yml, README, and /healthz for K8s probes; ArgoCD app.yaml exist in devops-k8s. Each UI is its own git repo (init + initial commit done); push from the UI folder root (e.g. `inventory-service/inventory-ui`). Remaining: add GitHub remote per repo, set secrets (GH_PAT, REGISTRY_* , KUBE_CONFIG), then push to `main` to trigger deploy.

1. **logistics-ui** -- scaffolded; dispatch + fleet view for Busia ops team
2. **inventory-ui** -- scaffolded; stock levels + item management for Busia kitchen
3. **subscriptions-ui** -- scaffolded; plan/tenant management for platform admin
4. **pos-ui** -- scaffolded; in-store order terminal for Busia counter staff
5. **treasury-ui** -- scaffolded; transactions, settlements, gateways, platform admin

---

## 2. Cross-Cutting Concerns (Pending / Done)

| Concern | Scope | Priority | Notes |
|:--------|:------|:---------|:------|
| Atlas versioned migrations | All Go services | DEFERRED | Skipped for MVP; entrypoint.sh auto-migrate remains in use |
| Platform admin vs tenant admin | auth-api, auth-ui | P0 | Superuser routes must be separated from tenant-scoped admin routes; UIs have platform sections gated by role |
| Menu-inventory SKU linkage | ordering-backend + inventory-api | DONE | 39 menu items seeded with matching SKUs; inventory client wired; Recipe/BOM schemas exist |
| Busia-only outlet enforcement | auth-api seed, all frontends | DONE | Busia-only enforced in ordering-frontend, cafe-website, inventory seed (Busia Kitchen) |
| API base URL / SSO 404 fixes | All Go backends, auth-api | DONE | Root `/` redirects to `/v1/docs/`; OIDC discovery at `/.well-known/openid-configuration`; notifications-ui fetchProfile fixed |
| OAuth client redirect URIs | auth-api seed | DONE | All tenant slugs get redirect URIs for notifications-ui, ordering-ui; new UIs need OAuth client registration |
| DevOps 503 / config | values.yaml, rider-app | DONE | inventory-api secret name fixed; treasury-api duplicate keys fixed; 4 new UI values.yaml (logistics-ui, inventory-ui, subscription-ui, treasury-ui); rider-app domain set to riderapp.codevertexitsolutions.com |
| PWA install prompts | All frontends | P1 | Re-prompt every 30 min if not installed (ordering-frontend, rider-app, pos-ui, notifications-ui) |
| Mobile responsiveness audit | All frontends | P1 | Ordering-frontend and rider-app done; new UIs scaffolded responsive |
| Feature-gate caching | subscriptions-api + all consumers | P1 | Redis-backed TTL cache for `CheckFeature()` calls; avoid round-trip on every request |
| Payment workflow (invoice-first, shared pay page) | treasury-api, treasury-ui, ordering, subscription, cafe | P1 | Services create intent with `payment_method: "pending"`, redirect to treasury-ui `/pay`; user selects gateway; modals support QR and “I paid at till”. See [payment-workflow.md](payment-workflow.md). |
| E2E customer order flow | ordering-frontend -> ordering-backend -> treasury -> logistics -> rider-app | P0 | Full browser walkthrough not yet verified; blocked by DNS (auth subdomains) per bengobox-mvp-production-test-report.md; see e2e-gap-analysis.md for current E2E doc refs |
| E2E rider delivery flow | rider-app -> logistics-api -> ordering-backend (status callback) | P0 | Task accept -> navigate -> deliver -> POD not verified end-to-end |
| Cafe website real API wiring | cafe-website -> ordering-backend, auth-api | P1 | Set NEXT_PUBLIC_USE_DUMMY_DATA=false; menu/categories from catalog.ts (ordering-backend). Fix SSO: refresh token URL `/api/v1/token` in auth config |
| RBAC: roles + permissions seed and API | auth-api, all backends | P0 | See §8. All services seed roles/permissions (add, read, read_own, change, change_own, delete, manage, manage_own). Auth-api: Permission + RolePermission schema, seed, GET /me returns roles + permissions. Frontends: fetch from API, TanStack Query TTL cache, nav/route/404/unauthorized by permission. **Seed/RBAC audit (March 2026):** inventory-api: no local Role/Permission schema; RBAC via auth-api JWT; core data (tenants, warehouses) from ordering-backend sync; see inventory-api docs/rbac-and-seed.md. pos-api: no local schema; RBAC via auth-api JWT; docs/rbac-and-seed.md defines 8-action POS resources (orders, products, drawer, etc.). subscriptions-api: no local Role/Permission schema; cmd/seed seeds products, plans, bundles, demo subscription; RBAC via auth-api JWT; plan.md and sprint-3 updated. |
| CORS and production API URLs | auth-api, ordering-backend, all frontends, devops-k8s ingress | DONE | See §9. Backend CORS + **devops-k8s ingress CORS** (see [devops-k8s-ingress-cors.md](./devops-k8s-ingress-cors.md)); frontend builds must receive production API/SSO URLs at build time (Next.js NEXT_PUBLIC_*). |

---

## 3. Priority Ordering

### P0 -- Must ship by March 17 (launch blockers)

| Task | Service(s) | Est. Days | Owner | Status |
|:-----|:-----------|:----------|:------|:-------|
| Wire logistics-ui to logistics-api (fleet list, task board, dispatch) | logistics-ui | 2-3 | -- | Scaffold done |
| Wire inventory-ui to inventory-api (item list, stock dashboard, adjustments) | inventory-ui | 2-3 | -- | Scaffold done |
| Wire subscriptions-ui to subscriptions-api (plan list, tenant subscription view) | subscriptions-ui | 2-3 | -- | Scaffold done |
| Wire pos-ui to pos-api (order entry, receipt, cash drawer) | pos-ui | 2-3 | -- | Scaffold done |
| Wire treasury-ui to treasury-api | treasury-ui | 1-2 | -- | Scaffold done |
| Menu-inventory SKU linkage | ordering-backend, inventory-api | -- | -- | DONE |
| E2E customer order flow verification (browser) | ordering-frontend, ordering-backend, treasury-api, logistics-api | 1-2 | -- | Blocked by 503s; re-trigger CI deploy |
| E2E rider delivery flow verification (browser) | rider-app, logistics-api | 1 | -- | Pending |
| Platform admin vs tenant admin route separation | auth-api, auth-ui | 2 | -- | In progress |
| Atlas versioned migrations | all Go services | -- | -- | SKIPPED for MVP |

### P1 -- Should ship by March 17 (degrades experience if missing)

| Task | Service(s) | Est. Days | Owner |
|:-----|:-----------|:----------|:------|
| Busia-only outlet enforcement (seed + UI) | auth-api, all frontends | 1 | -- |
| PWA install prompts on all new frontends | logistics-ui, inventory-ui, pos-ui, subscriptions-ui | 1 | -- |
| Feature-gate caching (Redis TTL in subscriptions-api) | subscriptions-api | 1 | -- |
| Cafe website real API integration | cafe-website | 2 | -- |
| Mobile responsiveness pass on new UIs | logistics-ui, inventory-ui, pos-ui | 1-2 | -- |
| Security hardening review (CORS, CSP, rate-limit) | all services | 1-2 | -- |
| Inventory BOM/recipe module (composite items) | inventory-api | 2 | -- |

### P2 -- Nice to have (can launch without)

| Task | Service(s) | Est. Days | Owner |
|:-----|:-----------|:----------|:------|
| Promo code validation in ordering flow | ordering-backend | 1 | -- |
| Loyalty points accrual | ordering-backend | 1 | -- |
| Kitchen display system (KDS) screen | pos-ui | 2 | -- |
| Rider earnings dashboard polish | rider-app | 1 | -- |
| WebSocket real-time order tracking | logistics-api, ordering-frontend | 3 | -- |
| Distributed tracing (OpenTelemetry) | all services | 2 | -- |

---

## 4. Integration Dependency Graph

```
                       ┌──────────────┐
                       │   auth-api   │
                       │   auth-ui    │
                       └──────┬───────┘
                              │ JWT + tenant context
            ┌─────────────────┼─────────────────────────────────┐
            │                 │                                 │
            v                 v                                 v
   ┌─────────────────┐ ┌──────────────┐              ┌─────────────────┐
   │ subscriptions-  │ │notifications-│              │  All other      │
   │ api             │ │api           │              │  services       │
   │ subscriptions-  │ └──────┬───────┘              │  (via JWT)      │
   │ ui              │        │ email/sms             └────────┬────────┘
   └────────┬────────┘        │ on events                      │
            │ feature gates   │                                │
            │ (JWT claims)    │                                │
            v                 v                                v
   ┌──────────────────────────────────────────────────────────────────┐
   │                      treasury-api                                │
   │              (payment intents, M-Pesa, webhooks)                 │
   └──────────────────────────────┬───────────────────────────────────┘
                                  │ payment confirmation
                                  v
   ┌──────────────────────────────────────────────────────────────────┐
   │                    ordering-backend                               │
   │         (menu, cart, orders, promo, loyalty)                      │
   │                    ordering-frontend                              │
   └────────┬─────────────────────────────────┬───────────────────────┘
            │ stock check / reserve            │ order.ready event
            v                                  v
   ┌─────────────────┐               ┌─────────────────┐
   │ inventory-api   │               │  logistics-api   │
   │ inventory-ui    │               │  logistics-ui    │
   │ (SKU, stock,    │               │  rider-app       │
   │  BOM, warehouse)│               │ (fleet, tasks,   │
   └─────────────────┘               │  POD, tracking)  │
                                     └─────────────────┘

   ┌─────────────────┐               ┌─────────────────┐
   │   pos-api       │───────────────│  cafe-website    │
   │   pos-ui        │  POS orders   │  (public menu,   │
   │ (counter sales, │  feed into    │   ordering,      │
   │  cash drawer)   │  ordering +   │   SSO login)     │
   └─────────────────┘  inventory    └─────────────────┘
```

### Key Integration Flows for MVP

1. **Customer Order Flow**:
   `cafe-website/ordering-frontend` -> `ordering-backend` -> `inventory-api` (reserve stock) -> `treasury-api` (payment) -> `logistics-api` (delivery task) -> `rider-app` (accept + deliver) -> `notifications-api` (email/SMS confirmation)

2. **POS Order Flow**:
   `pos-ui` -> `pos-api` -> `ordering-backend` (shared order model) -> `inventory-api` (deduct stock) -> `treasury-api` (payment)

3. **Rider Delivery Flow**:
   `ordering-backend` publishes `ordering.order.ready` -> `logistics-api` creates task -> `rider-app` shows task -> rider accepts -> rider delivers -> POD photo -> `logistics-api` marks complete -> `ordering-backend` receives callback

4. **Subscription Flow**:
   `subscriptions-ui` -> `subscriptions-api` -> plan/feature management -> JWT claims enrichment via `auth-api` -> all services enforce feature gates

---

## 5. Risk Register (March 17)

| # | Risk | Likelihood | Impact | Mitigation | Status |
|:--|:-----|:-----------|:-------|:-----------|:-------|
| 1 | Four UI scaffolds not wired to APIs | MEDIUM | HIGH | All 5 UIs scaffolded; wire to backends and deploy | OPEN |
| 2 | M-Pesa till number not provisioned for Busia | MEDIUM | HIGH | Fall back to COD (cash on delivery) for MVP | MONITORING |
| 3 | Menu-inventory SKU linkage incomplete | LOW | HIGH | DONE: 39 items seeded, inventory client wired | RESOLVED |
| 4 | Single developer bandwidth | HIGH | HIGH | Ruthless scope cut; P2 items deferred entirely; AI-assisted scaffolding | ACCEPTED |
| 5 | Atlas migration not adopted (auto-migrate entrypoint.sh) | MEDIUM | MEDIUM | entrypoint.sh works but is fragile; acceptable for single-outlet MVP | ACCEPTED |
| 6 | E2E flow never tested end-to-end in staging | HIGH | HIGH | Allocate Mar 10-12 exclusively for E2E verification | OPEN |
| 7 | Feature-gate caching missing (every request hits subscriptions-api) | LOW | MEDIUM | Single-outlet load is low; cache can be added post-launch | ACCEPTED |
| 8 | Busia outlet data not seeded | LOW | HIGH | Busia-only enforced in frontends and inventory seed | RESOLVED |
| 9 | PWA install prompts missing on new UIs | LOW | LOW | Users can still use browser; prompts are UX enhancement | ACCEPTED |
| 10 | No staging environment distinct from production | MEDIUM | MEDIUM | Test on production with feature flags; accept risk for MVP | ACCEPTED |

---

## 6. Recommended Sprint Plan (Mar 6 - Mar 17)

### Sprint A: Mar 6-9 (Build)

- [x] Scaffold subscriptions-ui (Next.js + Zustand + SSO/PKCE)
- [x] Scaffold logistics-ui (fleet list, task board, tracking, platform)
- [x] Scaffold inventory-ui (item list, stock levels, adjustments, platform)
- [x] Scaffold pos-ui (order entry, receipt, drawer, platform)
- [x] Scaffold treasury-ui (transactions, settlements, gateways, platform)
- [x] Menu-inventory SKU linkage (ordering-backend seed 39 items; inventory client wired)
- [x] API base URL redirect to /v1/docs/ (all Go backends)
- [x] SSO OIDC root discovery + notifications-ui fetchProfile fix
- [x] DevOps: new UI values.yaml, rider-app domain, config fixes
- [ ] Platform admin vs tenant admin separation in auth-api (RBAC hardening)

### Sprint B: Mar 10-12 (Integrate + Test)

- [ ] E2E customer order flow (browser walkthrough)
- [ ] E2E rider delivery flow (browser walkthrough)
- [ ] E2E POS order flow (browser walkthrough)
- [ ] Busia outlet seed data verification
- [x] Cafe website: fix SSO (refresh URL `/api/v1/token` in auth config; AUTH_CLIENT_ID=cafe-website)
- [x] Cafe website real API: dummy menu and useDummyData removed; menu and landing use only ordering-backend catalog
- [x] Ordering-backend seed: image_url added for all 39 menu items (paths like /images/menu/…)
- [ ] Ordering-frontend: production API URL env; align order creation with backend (cart+checkout or POST /orders)
- [ ] Mobile responsiveness pass on all new UIs
- [ ] PWA install prompts on all frontends

### Sprint C: Mar 13-15 (Harden + Fix)

- [ ] Fix bugs found in E2E testing
- [ ] Security hardening (CORS, CSP, rate limits)
- [ ] Feature-gate caching if time permits
- [ ] Atlas migrations if time permits
- [ ] Performance spot-check (key API response times < 500ms)

### Sprint D: Mar 16-17 (UAT + Launch)

- [ ] Client UAT walkthrough
- [ ] Fix critical UAT bugs
- [ ] Go/No-Go decision
- [ ] Tag all repos v1.0.0-mvp
- [ ] DNS + TLS verification for all production domains
- [ ] Smoke test all services post-deploy

---

## 7. Tenant and brand configuration (MVP)

**Goal**: All frontends load tenant-specific branding (logo, org name, brand colors, outlets) from the backend with fallback to `NEXT_PUBLIC_TENANT_SLUG` (or equivalent). Tenant-related endpoints are public where needed for landing and org discovery.

### Backend

- **auth-api**: `GET /api/v1/tenants/by-slug/{slug}` is **public**; returns tenant `id`, `name`, `slug`, `status`, `metadata`. Use `metadata` for brand (logo_url, primary_color, secondary_color) if present; else frontends fall back to service-specific branding endpoints or env.
- **Per-service branding**: Services that own tenant-facing UI (e.g. notifications-api `GET /api/v1/{tenant}/branding`, ordering-backend optional `GET /api/v1/{tenant}/config`) may expose public tenant/brand config. Frontends should prefer auth-api tenant by slug for name/slug, then service branding for logo/colors.
- **Seed data**: Tenant seed must include `urban-loft` with correct slug; brand fields in metadata or in each service’s tenant/config seed as applicable.

### Frontend

- **Tenant slug**: From URL (`[orgSlug]` or `[tenantSlug]`) on public pages; pass in API requests (path and/or header `X-Tenant-Slug`). Persist in localStorage only when set by user/route.
- **Brand loading**: On app or org layout load, fetch tenant/brand (auth-api `/tenants/by-slug/{slug}` and/or service branding API). Apply logo, org name, primary/secondary colors to layout and theme (CSS variables or theme provider). Fallback: `NEXT_PUBLIC_TENANT_SLUG` (default slug), default logo and colors.
- **Theme**: Set CSS variables (e.g. `--primary`, `--secondary`) or theme provider from tenant brand colors; ensure contrast and accessibility.
- **System config page**: Each frontend’s system/settings page MUST include brand-related config (logo URL, brand colors, tenant/org name, outlets/branches link) — either inline or link to dedicated branding page.

### Status

- [x] auth-api: Tenant by slug public; metadata for brand; PublicTenantResponse DTO
- [x] ordering-backend: Public GET /api/v1/{tenant}/config (TenantSetting.BrandPalette + metadata)
- [x] ordering-frontend: useBrandConfig + BrandThemeSync; staff settings AppBrandSummary
- [x] cafe-website: TenantBrandProvider + auth-api by-slug; Settings Branding section
- [x] notifications-api/ui: GET /branding; BrandingProvider; HP-2 branding ticked Already has `/branding`; ensure public or auth as doc’d; UI applies theme
- [x] treasury-ui, logistics-ui, inventory-ui, pos-ui, subscriptions-ui, auth-ui: BrandingProvider/TenantProvider; Settings brand section

---

## 8. RBAC, permissions, caching, and data fetching (MVP)

### 8.1 Permission model (all services)

All MVP services MUST seed **roles** and **permissions** for models in their schema. Use a consistent action set per resource:

| Action       | Meaning                          | Example code    |
|-------------|-----------------------------------|-----------------|
| `add`       | Create new                        | `orders:add`    |
| `read`      | Read any                          | `orders:read`   |
| `read_own`  | Read only own                     | `orders:read_own` |
| `change`    | Update any                        | `orders:change` |
| `change_own`| Update only own                   | `orders:change_own` |
| `delete`    | Delete any                        | `orders:delete` |
| `manage`    | Full admin on resource            | `orders:manage` |
| `manage_own`| Full admin on own only            | `orders:manage_own` |

- **Auth-api**: Source of truth for platform/tenant **roles** and **permissions**. Seed roles (e.g. `superuser`, `admin`, `staff`, `member`, `rider`) and map each role to the above permission codes for relevant resources (users, tenants, orders, menu, riders, etc.). Expose permissions via `GET /api/v1/me` or `GET /api/v1/me/permissions` (and optionally in JWT).
- **Other backends**: Seed service-specific roles/permissions if they enforce local RBAC; otherwise rely on auth-api JWT + permission claims and enforce in middleware.

### 8.2 Frontend RBAC (all MVP frontends)

- **Granular RBAC**: Use both **role** and **permissions** (from backend API) to control:
  - **Nav/sidebar**: Show or hide items based on `hasPermission(resource, 'read')` (or role fallback).
  - **Route protection**: Guard dashboard/admin routes; redirect to login or **403 Unauthorized** page when missing permission.
  - **404**: Dedicated not-found page for unknown routes.
  - **Unauthorized**: Dedicated page when user is authenticated but lacks permission for the resource/action.
- **Data source**: Roles and permissions MUST be **pulled from backend/API** (e.g. auth-api `GET /me` or `GET /me/permissions`). No hardcoded permission lists in frontend.
- **Caching**: Cache roles/permissions in **TanStack Query** with a TTL (e.g. `staleTime: 5 * 60 * 1000` ms). Invalidate on logout or on 401.

### 8.3 Frontend data fetching

- **TanStack Query**: All MVP frontend services MUST use **TanStack Query** (`useQuery`, `useMutation`) for all API fetch queries (menu, orders, user, permissions, etc.). No raw `fetch` or `axios` in components without a Query hook wrapper.

### 8.4 Backend caching and performance

- **Roles/permissions**: Backend (auth-api and others that resolve permissions) SHOULD cache permission lookups in **Redis** with a short TTL (e.g. 60s) to reduce DB load.
- **Events, background jobs, real-time**: All MVP backend services SHOULD use **events** (e.g. NATS), **Redis cache** (sessions, permission cache, feature flags), and **background jobs** where applicable for production performance, scalability, and security. Use **real-time** (WebSocket/SSE) where UX requires live updates (e.g. order status, rider location).

### 8.5 mvp-critical-path task alignment

- For each service in **§1 MVP Service Status Matrix**, ensure:
  - Seed includes core data, roles, and permissions (per §8.1).
  - Frontend uses TanStack Query for fetches, RBAC from API with TTL cache, nav/route/404/unauthorized per §8.2–8.3.
  - Backend uses Redis (and events/background jobs) per §8.4 where applicable.
- **Platform admin vs tenant admin** (§2): Implement with roles + permissions (e.g. `superuser` vs `admin` + resource permissions).

---

## 9. Production domains

Use this table as the single reference for config and docs; replace or align any legacy domain references (e.g. treasury → booksapi, ordersapp → ordering).

| Service | API | UI |
|---------|-----|-----|
| Treasury | booksapi.codevertexitsolutions.com | books.codevertexitsolutions.com |
| Cafe website | — | theurbanloftcafe.com |
| Ordering | orderingapi.codevertexitsolutions.com | ordersapp.codevertexitsolutions.com |
| Subscription | pricingapi.codevertexitsolutions.com | pricing.codevertexitsolutions.com |
| Inventory | inventoryapi.codevertexitsolutions.com | inventory.codevertexitsolutions.com |
| Logistics | logisticsapi.codevertexitsolutions.com | logistics.codevertexitsolutions.com |

Auth: sso.codevertexitsolutions.com (API), accounts.codevertexitsolutions.com (UI). Rider app: riderapp.codevertexitsolutions.com. Subscriptions UI: pricing.codevertexitsolutions.com. Treasury UI: books.codevertexitsolutions.com. **Ordering UI**: ordersapp.codevertexitsolutions.com. See e2e-gap-analysis.md for full table and status.

## 10. CORS and production domains (SSO integration)

To avoid **production CORS errors** and **"Network Error"** when frontends (e.g. ordersapp.codevertexitsolutions.com) call backends:

### 10.1 Backend CORS (allowed origins)

- **auth-api** (`internal/httpapi/router.go`): AllowOriginFunc must include every **frontend** origin that calls auth-api (authorize, token, /me): `https://ordersapp.codevertexitsolutions.com`, `https://theurbanloftcafe.com`, `https://notifications.codevertexitsolutions.com`, `https://accounts.codevertexitsolutions.com`, `https://logistics.codevertexitsolutions.com`, `https://pos.codevertexitsolutions.com`, plus localhost for dev. Auth-api already allows `*.codevertexitsolutions.com` (https).
- **ordering-backend** (`internal/config/config.go`): `HTTP_ALLOWED_ORIGINS` (env) must list **browser origins** that call the API (frontends), not the API host: e.g. `https://ordersapp.codevertexitsolutions.com`, `https://theurbanloftcafe.com`, `https://pos.codevertexitsolutions.com`, `https://accounts.codevertexitsolutions.com`, `http://localhost:3001`. Default in code and in **values.yaml** (or deployment env) must match production.
- Other backends (treasury-api, notifications-api, logistics-api, inventory-api, etc.): Ensure CORS allows their respective frontend origins.

### 10.2 Frontend build-time env (Next.js)

- **Next.js bakes `NEXT_PUBLIC_*` at build time.** If the Docker/build does not pass production URLs, the app will use code defaults (e.g. `http://localhost:4000`) and production will call localhost → CORS/network error.
- **ordering-frontend**: Dockerfile must declare ARG/ENV for `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SSO_URL`, etc. **build.sh** (and CI) must pass `--build-arg NEXT_PUBLIC_API_URL=https://orderingapi.codevertexitsolutions.com/api/v1` (and other NEXT_PUBLIC_*) when running `docker build`.
- **values.yaml** (devops-k8s): For frontend apps, ensure build args or runtime env (where applicable) set production API/SSO URLs. For Next.js, build args are required; runtime env does not change already-baked NEXT_PUBLIC_*.

### 10.3 Ingress CORS (devops-k8s)

**All services that integrate with SSO** must have ingress CORS configured in **devops-k8s** so browser requests from frontend origins are allowed. Use the canonical list of allowed origins and NGINX Ingress annotations per backend.

- **Reference:** [devops-k8s-ingress-cors.md](./devops-k8s-ingress-cors.md) — canonical allowed origins, NGINX Ingress CORS annotations for **auth-api**, **ordering-backend**, **notifications-api**, **logistics-api**, **treasury-api**, **inventory-api**, **pos-api**, **subscriptions-api**, and **values.yaml** env for `HTTP_ALLOWED_ORIGINS` where applicable.
- Apply the annotations in `apps/<app-name>/` Ingress resources (or Helm values that render the Ingress) in the **Bengo-Hub/devops-k8s** repo.
- Frontend apps do not need ingress CORS for their own host; the **backend** ingress must allow the frontend origins.

### 10.4 Checklist (per service)

| Service | CORS / allowed origins | Frontend build args (if Next.js) |
|---------|------------------------|-----------------------------------|
| auth-api | All SSO frontend origins + *.codevertexitsolutions.com | N/A |
| ordering-backend | ordersapp, theurbanloftcafe, pos, accounts, notifications, localhost:3001 | N/A |
| ordering-frontend | N/A (calls backends) | NEXT_PUBLIC_API_URL, NEXT_PUBLIC_SSO_URL, NEXT_PUBLIC_CAFE_WEBSITE_URL, NEXT_PUBLIC_LOGISTICS_UI_URL, etc. |
| cafe-website | N/A | NEXT_PUBLIC_AUTH_SERVICE_URL, NEXT_PUBLIC_SITE_URL |
| notifications-ui | N/A | NEXT_PUBLIC_SSO_URL, NEXT_PUBLIC_API_URL (notifications-api) |
| auth-ui | N/A | NEXT_PUBLIC_API_URL (auth-api), NEXT_PUBLIC_APP_URL |

---

## Project conventions (uniformity)

- **Frontend package manager**: Use **pnpm** (not npm or yarn) for all frontend apps. Install: `pnpm install`. Run: `pnpm run dev`, `pnpm run build`, etc. Each frontend app should have `packageManager` and `engines.pnpm` in `package.json`. See `.cursor/rules/frontend-pnpm.mdc` for the full rule.

---

## References

- [MVP Countdown Tracker](./mvp-countdown-tracker.md)
- [Cross-Service Data Ownership](./CROSS-SERVICE-DATA-OWNERSHIP.md)
- [Microservice Architecture](./microservice-architecture.md)
- [Trinity Authorization Pattern](./TRINITY-AUTHORIZATION-PATTERN.md)
- [Roadmap](./roadmap.md)
