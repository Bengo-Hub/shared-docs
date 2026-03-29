# BengoBox SSO Integration Guide

**Last Updated**: March 29, 2026
**Status**: Production — all MVP frontends integrated. SSO revamp (JWT permissions, JIT, public menu, canonical codes, tenant-in-URL token minting, auth/me Redis cache) implemented. **JIT role assignment** now maps global JWT roles to service-level roles on first login across all backends (treasury, inventory, pos, logistics, notifications). **Subscription enforcement (March 29 fix):** ALL services now use mutations-only enforcement — GET requests pass through unconditionally; only POST/PUT/PATCH/DELETE require active subscription. Frontend 403 discrimination distinguishes subscription 403 (`code: subscription_inactive`, `upgrade: true`) from auth 403 to prevent login redirect loops. All frontends implement `SubscriptionBanner` + `SubscriptionGate` + `useSubscription()` hook for UI-level gating. **Production domains** align with devops-k8s/apps/*/values.yaml only (no alternate domains); see Progress and Production domains table below.

---

## Overview

BengoBox uses a single centralised SSO (Single Sign-On) service for all authentication. Every frontend delegates login/register entirely to the SSO — no service handles passwords or sessions independently.

| Component | Domain | Role |
|-----------|--------|------|
| **auth-api** (SSO server) | `sso.codevertexitsolutions.com` | Issues JWT tokens, manages sessions |
| **auth-ui** (login/register UI) | `accounts.codevertexitsolutions.com` | User-facing login/register forms |
| All other frontends | `*.codevertexitsolutions.com` | Consume SSO tokens |

**Progress (March 2026):** Auth-api issues JWT with `roles` and `permissions` (canonical codes: e.g. `catalog:view`, `catalog:manage`). Login/register/refresh responses return `roles` and `permissions` only at the top level (not duplicated under `user`). Authorize URL supports `tenant=<slug>`; token exchange prefers that tenant when the user is a member. GET `/api/v1/auth/me` is cached in Redis by user ID with TTL = token expiry (or 24h) to reduce DB load; frontends should use TanStack Query with a similar TTL (e.g. 5 min–24h). Ordering-backend (and other Go backends) use JIT tenant sync and JIT user provisioning. OAuth clients: `pos-ui` and tenant-aware redirect URIs for pos-ui, subscriptions-ui, treasury-ui, notifications-ui. Public menu endpoints (`/menu/*`) documented and used by cafe-website. **JIT role assignment:** All backends now map global JWT roles (superuser, admin, staff) to service-level roles during JIT provisioning (e.g. superuser → finance_admin in treasury, inventory_admin in inventory, pos_admin in POS). **Subscription enforcement:** ordering-backend (mutations), logistics-api (mutations), treasury-api, inventory-api, pos-api, projects-api enforce RequireActiveSubscription; core services (auth-api, subscriptions-api, notifications-api) do not. **Notifications rate limiting:** Email sending is rate-limited by plan via `max_emails_per_day` from JWT SubscriptionLimits (Redis sliding window, returns 429). **Treasury-ui platform fix:** AuthProvider now checks `superuser` role and `isPlatformOwner` flag (was incorrectly checking `super_admin`). Docs updated: JWT claims, JIT role assignment, subscription enforcement, rate limiting, debugging table.

---

## OIDC Authorization Code + PKCE Flow

Every frontend uses the same flow:

```
1. User clicks "Login" or "Sign Up" on any frontend
         ↓
2. Frontend generates PKCE: code_verifier + code_challenge (SHA-256)
         ↓
3. Frontend redirects to:
   https://sso.codevertexitsolutions.com/api/v1/authorize
     ?response_type=code
     &client_id=<service-client-id>
     &redirect_uri=<callback-url>
     &scope=openid profile email offline_access
     &state=<csrf-token>
     &code_challenge=<pkce-challenge>
     &code_challenge_method=S256
     &tenant=<slug>            ← optional, pre-selects tenant
         ↓
4. auth-api detects user is not authenticated, redirects to:
   https://accounts.codevertexitsolutions.com/login
     ?return_to=<full-authorize-url>
     &tenant=<slug>
   (auth-api does **not** pass client_id/redirect_uri as separate params; they are only inside return_to.)
         ↓
5. auth-ui handles login/register (email+password, Google, GitHub, Microsoft)
         ↓
6. auth-ui redirects back to return_to (the full authorize URL). This **must** be a **full page redirect** (window.location.href), not a client-side router.push, so the browser sends the session cookie to sso and the redirect loop is avoided. auth-ui validates return_to with isValidReturnUrl (allows same-origin relative paths and absolute URLs starting with NEXT_PUBLIC_API_URL / SSO issuer).
         ↓
7. auth-api now has authenticated user → generates auth code
   Redirects to: <redirect_uri>?code=<auth-code>&state=<csrf-token>
         ↓
8. Frontend callback page:
   a. Verify state matches stored value (CSRF check)
   b. POST /api/v1/token with code + code_verifier + client_id + redirect_uri
   c. Receive: access_token (JWT), id_token, refresh_token
         ↓
9. Bridge/sync screen:
   Poll service's own /me endpoint until user data is available
   (NATS events sync user from auth-service to each service's DB)
         ↓
10. Redirect to destination based on user role/scenario
```

---

## Critical: Correct OIDC Endpoint Paths

**CORRECT:**
```
POST https://sso.codevertexitsolutions.com/api/v1/token
GET  https://sso.codevertexitsolutions.com/api/v1/authorize
GET  https://sso.codevertexitsolutions.com/api/v1/auth/logout?post_logout_redirect_uri=<url>  (clears session cookie, redirects to allowlisted URL or accounts)
POST https://sso.codevertexitsolutions.com/api/v1/auth/logout  (requires Bearer token; revokes session, returns JSON)
GET  https://sso.codevertexitsolutions.com/.well-known/openid-configuration
```

**WRONG (will return 404):**
```
/api/v1/auth/oidc/authorize   ← used by old frontends — DO NOT USE
/api/v1/auth/login            ← not an OIDC path
/api/v1/auth/oidc/token       ← wrong path
```

> The correct paths are defined in `auth-api/internal/httpapi/router.go`.

---

## Uniform SSO integration standard (all services)

To keep the ecosystem maintainable, **every frontend and backend that integrates with SSO must follow the same pattern**. Divergent flows (e.g. ordering vs treasury) cause 401s, broken UX, and hard-to-debug issues.

### Frontend (all UIs: ordering-frontend, treasury-ui, pos-ui, subscriptions-ui, cafe-website, etc.)

| Step | Requirement |
|------|-------------|
| **1. Login entry** | Redirect to SSO authorize URL with PKCE (`code_challenge`, `code_verifier`, `state`). Pass `tenant` only when the user is already in a tenant context (e.g. path `/{orgSlug}/menu` → pass `orgSlug`). When the user lands on auth-ui directly (no `?tenant=`), auth-ui sends **no tenant**; auth-api resolves tenant from the user's primary org. |
| **2. Callback** | Exchange `code` + `code_verifier` at `POST /api/v1/token`. Store `access_token`, `refresh_token`, `expires_at`. Attach token getter to the API client so **every** request sends `Authorization: Bearer <token>`. |
| **3. Tenant context** | After first successful profile response, store `tenant_id` and `tenant_slug` (from SSO or service `/me`) in localStorage. Send `X-Tenant-ID` (must be the **tenant UUID** from auth-api, not a slug or custom string like `tenant-urban-loft`) and `X-Tenant-Slug` on **every** request to tenant-scoped backends. Backends expect `X-Tenant-ID` to be a valid UUID. |
| **4. Profile** | Prefer service's own `GET /api/v1/{tenant}/auth/me` (or equivalent) so roles/permissions match that service. If the service returns 404 (user not yet synced), fall back to SSO `GET /api/v1/auth/me` with the access token and map the response so the UI still shows authenticated state. |
| **5. 401 handling** | Register a global 401 handler (e.g. axios interceptor): on 401, (a) clear TanStack query cache (`queryClient.clear()`), (b) clear localStorage (`accessToken`, `refreshToken`, `tenantId`, `tenantSlug`, `expiresAt`), (c) reset auth store state, (d) redirect to SSO logout `GET /api/v1/auth/logout?post_logout_redirect_uri={origin}`. Reference implementation: ordering-frontend `src/lib/api/base.ts` + `src/providers/app-providers.tsx`. |
| **6. Tenant branding** | Fetch from auth-api `GET /api/v1/tenants/by-slug/{slug}` and cache with TanStack Query `staleTime: 6 * 60 * 60 * 1000` (6 hours, matching JWT TTL). Apply CSS variables (`--tenant-primary`, `--tenant-secondary`, `--tenant-logo-url`) from cached data. **Do NOT store branding locally or provide a branding editor** — redirect to auth-ui `/dashboard/settings?tab=branding`. |
| **7. Profile management** | Common profile fields (name, email, avatar) → redirect to auth-ui `/dashboard/profile`. Keep only role-specific fields in the service's own profile page (e.g. rider KYC in rider-app, customer preferences in ordering-frontend). |
| **8. Logout flow** | On user-initiated logout: (a) clear all caches and localStorage, (b) redirect to SSO logout `GET /api/v1/auth/logout?post_logout_redirect_uri={origin}` which clears the session cookie and redirects back. |

### Backend (all Go services: ordering-backend, treasury-api, etc.)

| Step | Requirement |
|------|-------------|
| **1. JWT validation** | Use the shared auth-client validator (e.g. `shared-auth-client`) with the same JWKS/issuer as auth-api. Validate `Authorization: Bearer <token>` on protected routes. |
| **2. Tenant in path or header** | For tenant-scoped routes, require tenant in path (e.g. `/api/v1/{tenant}/auth/me`) or accept `X-Tenant-ID` (UUID). Resolve tenant from path first, then header. |
| **3. JIT user** | If the JWT is valid but the user is not in the local DB, JIT-provision from token claims (and optional NATS sync). Use tenant from path/header for the provisioned membership. |
| **4. Response shape** | Return `session` (accessToken, refreshToken, expiresAt, sessionId), `user` (id, email, fullName, roles, permissions, …), and `tenant_id` / `tenant_slug` so the frontend can persist them. Use camelCase JSON keys to match frontend types. |

### auth-ui (login/register only)

- **Email/password form:** Only email and password fields. Do **not** ask for or default tenant. Send `tenant_slug: ''` when the URL has no `?tenant=`. auth-api resolves the user's org from `primary_tenant_id`.
- **OAuth buttons:** Same rule: send `tenant_slug` only when `?tenant=` is present in the URL (e.g. when redirected from an app with tenant in the link). Otherwise send empty.

### E2E tests

- Tests must mirror **real user experience**: no forged query params (e.g. no `?tenant=urban-loft` for tenant admin). User opens `/login`, enters email and password only, submits; backend resolves tenant from email.
- After login, assert that **authenticated requests succeed** (e.g. no 401 when calling `/auth/me` or a protected endpoint with the token in headers).

---

## OAuth Client Registration

Each frontend must be registered as an OAuth client in auth-api. The seed runs on every pod startup (`auth-api/cmd/seed/main.go`) and upserts these clients:

| client_id | Frontend | Redirect URI pattern (production domain from devops-k8s values.yaml) | Public |
|-----------|----------|----------------------------------------------------------------------|--------|
| `ordering-ui` | ordering-frontend | `https://ordersapp.codevertexitsolutions.com/{tenant}/auth/callback` | Yes |
| `rider-app` | rider-app | `https://riderapp.codevertexitsolutions.com/auth/callback` | Yes |
| `notifications-ui` | notifications-ui | `https://notifications.codevertexitsolutions.com/auth/callback` and `/{tenant}/auth/callback` | Yes |
| `pos-ui` | pos-ui | `https://pos.codevertexitsolutions.com/{tenant}/auth/callback` and `/auth/callback` | Yes |
| `inventory-ui` | inventory-ui | `https://inventory.codevertexitsolutions.com/{tenant}/auth/callback` and `/auth/callback` | Yes |
| `subscriptions-ui` | subscriptions-ui | `https://pricing.codevertexitsolutions.com/{tenant}/auth/callback` and `/auth/callback` | Yes |
| `treasury-ui` | treasury-ui | `https://books.codevertexitsolutions.com/{tenant}/auth/callback` and `/auth/callback` | Yes |
| `logistics-ui` | logistics-ui | `https://logistics.codevertexitsolutions.com/auth/callback` | Yes |
| `auth-ui` | auth-ui | `https://accounts.codevertexitsolutions.com/auth/callback`, `https://sso.codevertexitsolutions.com/auth/callback` | Yes |
| `cafe-website` | cafe-website | `https://theurbanloftcafe.com/auth/callback` | Yes (PKCE) |

**The seed uses upsert** — re-running it fixes misconfigured redirect URIs automatically. For tenant-aware apps, seed includes both `/{tenant}/auth/callback` and `/auth/callback` so either pattern works.

**CORS and X-Tenant-ID:** auth-api (and any backend that accepts `X-Tenant-ID`) must include `X-Tenant-ID` in `Access-Control-Allow-Headers` (app CORS and ingress annotations). Otherwise frontends that send the tenant UUID header (e.g. after loading profile from `/me`) will get a CORS preflight failure. See [devops-k8s-ingress-cors.md](./devops-k8s-ingress-cors.md).

**Production domains (from devops-k8s/apps/*/values.yaml ingress host):** Only these domains are configured; CORS and OAuth use this list only (no alternate domains).

| App | Production host |
|-----|-----------------|
| auth-api (SSO) | `sso.codevertexitsolutions.com` |
| auth-ui | `accounts.codevertexitsolutions.com` |
| ordering-frontend | `ordersapp.codevertexitsolutions.com` |
| cafe-website | `theurbanloftcafe.com` |
| notifications-ui | `notifications.codevertexitsolutions.com` |
| rider-app | `riderapp.codevertexitsolutions.com` |
| subscriptions-ui | `pricing.codevertexitsolutions.com` |
| treasury-ui | `books.codevertexitsolutions.com` |
| pos-ui | `pos.codevertexitsolutions.com` |
| logistics-ui | `logistics.codevertexitsolutions.com` |
| inventory-ui | `inventory.codevertexitsolutions.com` |
| ticketing-ui | `ticketing.codevertexitsolutions.com` |
| projects-ui | `projects.codevertexitsolutions.com` |

**Do not use:** `treasury.codevertexitsolutions.com` or `subscriptions.codevertexitsolutions.com` for the UIs — use `books.codevertexitsolutions.com` (treasury-ui) and `pricing.codevertexitsolutions.com` (subscriptions-ui). Rider app host is `riderapp.codevertexitsolutions.com` (not `rider.`).

---

## Tenant Context

All SSO requests should include tenant context so auth-api can mint the token for the correct organisation and downstream services can JIT-sync the tenant:

```typescript
// In buildAuthorizeUrl():
url.searchParams.set("tenant", orgSlug ?? "urban-loft");  // default tenant: urban-loft
```

- **Authorize URL:** `tenant=<slug>` is optional; when present, auth-api stores it on the authorization code and prefers that tenant when minting the access token (if the user is a member).
- **Default tenant:** `urban-loft` is the default app tenant; frontends should pass it (or the current org slug from the path) so the token carries the correct tenant.
- **Platform vs tenant orgs:** **Platform organisation** = `codevertex` (operates the platform; users may have cross-tenant access and do not consume tenant subscriptions). **Tenant organisations** = customer orgs (e.g. `urban-loft`, `mss`) that have subscriptions and use the product. Organisation slug `codevertex` is the platform owner; users with that primary tenant have elevated access.

### Login without tenant_slug: tenant resolved from user's primary tenant

**Direct login from auth-ui (e.g. `/login` with no `?tenant=` in the URL):** auth-ui sends `tenant_slug` as empty when the URL has no tenant. auth-api **does not** require a tenant slug for login. When `tenant_slug` is missing or empty:

1. auth-api looks up the user by email.
2. It then resolves the tenant from the user's **primary_tenant_id** in the database (each user has a linked primary organisation).
3. It verifies the user is a member of that tenant and continues the login flow.

So **tenant users can log in directly from auth-ui** at `https://accounts.codevertexitsolutions.com/login` without any `?tenant=...` in the URL. The correct tenant is determined by the user's primary organisation in auth-api. Frontends (auth-ui) must send an empty or omitted `tenant_slug` when the user did not arrive via a tenant-specific link; do not default to a fixed slug (e.g. `codevertex`) or tenant users who belong only to another org would get "invalid credentials".

After login, the JWT claims include `tenant_id` and `tenant_slug`. All service APIs read these via:
- `X-Tenant-ID` header (UUID)
- `X-Tenant-Slug` header (string)

### Tenant UUID: single source of truth

**Tenant UUID is issued by auth-api only.** All microservices that store or reference tenants MUST use this same UUID for a given tenant (no per-service UUIDs). Auth-api seeds tenants with DB-generated UUIDs (no fixed IDs). When a user logs in:

1. JWT contains `tenant_id` (UUID) and `tenant_slug` from auth-api.
2. **Profile source:** Frontends must load user/roles/permissions from **auth-api (SSO)** `GET /api/v1/auth/me` (Bearer token). Do not call the service’s own API for profile unless that service exposes a dedicated /auth/me (e.g. ordering-backend `GET /api/v1/{tenant}/auth/me` for its synced user). Treasury-ui, notifications-ui, subscriptions-ui, etc. call **SSO** for `/api/v1/auth/me`; treasury-api also exposes `GET /api/v1/auth/me` (JWT claims) as an optional fallback.
3. Frontends should store `tenant_id` (e.g. in localStorage) after the first successful profile load and send it as `X-Tenant-ID` on subsequent requests; use `tenant_slug` in the URL path (e.g. `/api/v1/urban-loft/...`).
4. When syncing users or tenants from events (e.g. NATS `auth.user.created`), downstream services must use the tenant UUID from the event (auth-api-issued), not generate a new one.

---

## Frontend Implementation Pattern

### 1. PKCE helpers (`src/lib/auth/pkce.ts`)

```typescript
export function generateCodeVerifier(): string          // 32 random bytes → base64url
export async function generateCodeChallenge(v): string  // SHA-256 → base64url
export function generateState(): string                 // 16 random bytes → hex
export function storeVerifier(v: string): void          // sessionStorage
export function consumeVerifier(): string | null        // get + delete
export function storeState(s: string): void
export function consumeState(): string | null
```

### 2. Auth store (`src/store/auth-store.ts` or equivalent)

See **[login-flow-contract.md](login-flow-contract.md)** for the full contract, service table, and platform vs tenant scope.

```typescript
// Start login flow (tenant optional; pass when in tenant context e.g. from path)
redirectToSSO(returnTo?: string, tenant?: string): Promise<void>

// Handle /auth/callback
handleSSOCallback(code: string, callbackUrl: string, tenantSlug?: string): Promise<void>
// ↑ Exchanges code → tokens → polls /me until user synced

// Logout
logout(): void  // Clears state + redirects to SSO logout
```

### 3. Callback page (`src/app/auth/callback/page.tsx`)

```typescript
// 1. Get code + state from URL params
// 2. Call handleSSOCallback(code, callbackUrl)
// 3. On authenticated: check user.status
//    - "pending" or "pending_review" → /auth/pending
//    - otherwise → sessionStorage.getItem("sso_return_to") or "/"
```

### 4. Pending page (`src/app/auth/pending/page.tsx`)

```typescript
// Poll fetchMe() every 15s
// When status is no longer "pending": redirect to /{orgSlug}/profile
```

---

## Service-Specific Notes

### auth-ui (login/register only): direct vs service-originated entry

| Entry | URL | After login |
|-------|-----|-------------|
| **Direct** | User opens `/login` (no `return_to`). | Redirect to `/dashboard` or valid relative `return_to` via `router.push`. |
| **Service-originated** | auth-api redirects to `/login?return_to=<full_sso_authorize_url>&tenant=...`. auth-api does **not** pass `client_id`/`redirect_uri` as separate params. | auth-ui must do a **full page redirect** (`window.location.href = return_to`) so the browser sends the session cookie to sso. Then auth-api sees the cookie, issues the auth code, and redirects to the service callback. |

auth-ui validates `return_to` with `isValidReturnUrl` (allows relative paths and absolute URLs starting with `NEXT_PUBLIC_API_URL` or fallback `https://sso.codevertexitsolutions.com`). Set `NEXT_PUBLIC_API_URL` to the SSO base so the sso authorize URL is accepted. See auth-ui README Environment section.

### ordering-frontend
- Client ID: `ordering-ui`
- Callback: `/{orgSlug}/auth/callback` (tenant-aware)
- Authorize URL: pass `tenant` from path (`orgSlug`) or default `urban-loft` so token is minted for the correct org
- After sync: redirect to returnTo URL (e.g. `/{orgSlug}/menu`)
- Source: `src/lib/auth/api.ts`, `src/store/auth.ts`

### rider-app
- Client ID: `rider-app`
- Callback: `/auth/callback` (NOT tenant-aware — uses fixed path)
- Profile: Call **SSO** `GET /api/v1/auth/me` (Bearer token) — not logistics-api. Implemented in `lib/auth-api.ts` (`fetchMe(accessToken)`); response is normalized to User (id, email, roles, tenants). Fixes "Syncing your account..." stuck screen when logistics-api `/riders/me` returns 404.
- After sync: check status → pending page or dashboard
- After admin approval: redirect to `/{orgSlug}/profile` for profile completion
- Invitation flow: `/join?invite_code=ABC&org=urban-loft` → SSO → pending → profile
- Source: `src/lib/auth-api.ts`, `src/store/auth-store.ts`, `src/hooks/useAuth.ts`

### notifications-ui
- Client ID: `notifications-ui`
- Callback: `/{orgSlug}/auth/callback`
- Profile: Call **SSO** `GET /api/v1/auth/me` (Bearer token).
- Source: `src/lib/auth/api.ts`

### treasury-ui
- Client ID: `treasury-ui`
- Callback: `/[orgSlug]/auth/callback`
- Profile: Call **SSO** `GET /api/v1/auth/me` (Bearer token) — not treasury-api. Implemented in `lib/auth/api.ts` (`fetchProfile(accessToken)`) and `hooks/useMe.ts`. Treasury-api also exposes `GET /api/v1/auth/me` (JWT claims) as an optional fallback.
- Source: `src/lib/auth/api.ts`, `src/store/auth.ts`, `src/hooks/useMe.ts`

### inventory-ui
- Client ID: `inventory-ui`
- Callback: `/{orgSlug}/auth/callback`
- Profile: Call **SSO** `GET /api/v1/auth/me` (Bearer token).
- Source: `src/lib/auth/api.ts`, `src/store/auth.ts`, `src/app/[orgSlug]/auth/callback/page.tsx`

### cafe-website
- Direct SSO (PKCE); no NextAuth
- Callback: `/auth/callback` (see seed redirect_uris)
- Public menu: uses `lib/api/public-menu.ts` (GET `/menu/categories`, `/menu/items` — no Authorization). Dashboard catalog uses `lib/api/catalog.ts` (auth required).
- Source: `src/lib/store/auth-store.ts`, `src/app/auth/callback/page.tsx`

---

## JWT Access Token Claims (Single Source of Truth for Authorization)

Auth-api must issue access tokens that contain everything microservices need to authorize requests, so that 401s are not caused by missing or inconsistent role/permission data.

**Required claims in the access token:**

- `sub` — User ID (UUID).
- `tenant_id`, `tenant_slug` — Tenant context.
- `roles` — Array of tenant-scoped roles (e.g. `superuser`, `admin`, `staff`, `member`, `rider`).
- `permissions` — Array of **canonical permission codes** derived from the SSO role–permission table (e.g. `catalog:view`, `catalog:manage`, `orders:read`, `orders:change`, `riders:read`).

**Canonical permission codes** are defined once in auth-api (seed) and used by all services. No service should define its own permission strings for cross-cutting authz; use the same codes (e.g. ordering-backend checks `catalog:view` / `catalog:manage`, and auth-api issues those same strings in the token and in GET /me).

Services validate the JWT (signature, issuer, audience, expiry) and read `roles` and `permissions` from the token to authorize. GET /me should return the same roles and permissions for UI and for services that prefer to call /me.

**Service-level permissions (Layer 3):** In addition to global JWT permissions, each domain service maintains its own fine-grained permission system in its database (see TRINITY-AUTHORIZATION-PATTERN.md). Service-level permission codes use the format `{service}.{module}.{action}` (e.g. `treasury.payments.add`, `ordering.orders.view`). The shared-auth-client library provides `RequirePermission()` middleware that checks `claims.Permissions` from the JWT, while each service's RBAC module provides local DB-backed permission checks via `rbacService.HasPermission()`. Both layers are enforced; superuser role bypasses all checks.

---

## Just-in-Time (JIT) Provisioning

When a microservice receives a **valid** JWT (valid signature, issuer, audience, expiry) but has **no local user record** for `sub`, it must not return 401. Instead it should **provision the user just-in-time**:

1. Create a minimal local user from token claims: `sub`, email, name, `tenant_id`, `tenant_slug`, and optionally roles/permissions from the token (or one call to auth-api GET /me).
2. Persist the user and then **retry the requested operation** (or continue the request).
3. Return 200 (or the appropriate success response), not 401.

This eliminates "user not found" 401s when NATS events are delayed or missing. NATS (`auth.user.created`, `auth.user.login`) remains the primary sync mechanism; JIT is the fallback so the first API call after login succeeds.

---

## Service-Specific Registration

- **Central auth:** Login and basic registration (email, password, profile) happen only at SSO (auth-ui). No service stores passwords or implements its own login.
- **Service-specific data:** When a service needs extra data (e.g. rider: KYC docs, vehicle; cafe: preferences), the flow is:
  1. User is already authenticated (has valid SSO token).
  2. User lands on the service; service detects "no local profile" or "incomplete profile".
  3. Service redirects to **service-specific onboarding** (auth-ui or service-owned page) with identity **prefilled** from the token (e.g. `?email=...&name=...` from token or GET /me).
  4. User completes service-specific fields (e.g. rider KYC, uploads); form submits to the service backend.
  5. Service creates or updates local profile linked to `sub`, then redirects back to the service or auth-ui landing.

No duplicate "registration" for credentials—only for service-specific attributes.

---

## Public vs Protected Endpoints

| Path pattern | Auth required | Use case |
|--------------|---------------|----------|
| `/api/v1/{tenant}/menu/*` | No | Public menu, categories, item detail |
| `/api/v1/{tenant}/cafes/*` | No | Public cafe/outlet list |
| `/api/v1/{tenant}/config` | No | Tenant brand/config |
| `/api/v1/{tenant}/catalog/*` | Yes | Staff catalog CRUD |
| `/api/v1/{tenant}/orders/*` (mutations) | Yes | Create/update orders, etc. |

Frontends must use **public** paths for unauthenticated or public reads (e.g. site menu). Do **not** send `Authorization` for public menu/catalog reads. Use `/menu/items` and `/menu/categories`, not `/catalog/items` and `/catalog/categories`, for public menu display.

---

## Auth/me and Caching

- **Backend (auth-api):** GET `/api/v1/auth/me` is cached in Redis by user ID. TTL = token expiry (from JWT `exp`) or 24h. Reduces DB load for high traffic; cache is per user and expires with the token.
- **Frontend:** Use TanStack Query (or equivalent) to call `GET /auth/me` (or the service’s `/me`) with a `staleTime`/TTL aligned to token lifetime (e.g. 5 min–24h). Check cache before refetching so the first read after login is fast; refetch on window focus or after TTL as needed.

## NATS User Sync

After SSO login, each service needs to know about the user. This happens via NATS events:

```
auth-api publishes: auth.user.created  (on new user)
auth-api publishes: auth.user.login    (on each login)

ordering-backend subscribes → creates/updates customer profile
logistics-api subscribes    → links FleetMember to UserID (for riders)
notifications-api subscribes → creates notification preferences
```

**Bridge screen polling** (all frontends):
- Call **SSO** `GET /api/v1/auth/me` (Bearer token) — not the service API (e.g. do not call booksapi for treasury-ui profile). Poll up to 10 times with 1.5s intervals if needed.
- Stop when user data is returned (200 OK)
- Show "Syncing your account..." spinner during wait
- If sync times out (15s): show error with retry

---

## Subscription Gating (Post-Login, Never Blocks Auth)

**Principle:** Subscription NEVER blocks login. Users must always be able to authenticate. Subscription is enforced AFTER login on mutations, UI elements, and action buttons.

### Backend Enforcement Pattern

All Go services use mutations-only enforcement via inline middleware (same pattern as ordering-backend):

```go
api.Use(func(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // GET/HEAD/OPTIONS always pass through
        if r.Method == http.MethodGet || r.Method == http.MethodHead || r.Method == http.MethodOptions {
            next.ServeHTTP(w, r)
            return
        }
        claims, ok := authclient.ClaimsFromContext(r.Context())
        if !ok { next.ServeHTTP(w, r); return }
        if claims.IsSuperuser() || claims.IsPlatformOwner || claims.IsSubscriptionActive() {
            next.ServeHTTP(w, r); return
        }
        // Returns {"error":"...","code":"subscription_inactive","upgrade":true}
        w.Header().Set("Content-Type", "application/json")
        w.WriteHeader(http.StatusForbidden)
        _, _ = w.Write([]byte(`{"error":"Your subscription is not active.","code":"subscription_inactive","upgrade":true}`))
    })
})
```

### Frontend 403 Discrimination

Frontends MUST distinguish subscription 403s from auth 403s using the `code` and `upgrade` fields:

```typescript
// In API client error interceptor:
if (error.response?.status === 403) {
  const data = error.response?.data;
  if (data?.code === 'subscription_inactive' || data?.upgrade === true) {
    // Subscription issue — show upgrade toast/banner, do NOT redirect to login
    onSubscription403Callback(data);
  }
}

// In auth-provider 403 handling:
if (isError && statusCode === 403) {
  const data = (error as any)?.response?.data;
  if (data?.code === 'subscription_inactive' || data?.upgrade === true) return; // Skip redirect
  router.replace(`/${orgSlug}/unauthorized`); // Only redirect for permission 403
}
```

### Frontend UI Components

Each frontend implements these subscription components:
- **`useSubscription()`** hook — lazy-loads subscription info after auth, returns `isActive`, `hasFeature()`, `isPastDue`, `isExpired`, etc.
- **`<SubscriptionBanner />`** — persistent top banner for trial expiry, past due, expired states. Never blocks access.
- **`<SubscriptionGate feature="..." />`** — wraps content requiring specific features; shows upgrade prompt when gated.

---

## Debugging Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| 404 on authorize redirect | Wrong path `/api/v1/auth/oidc/authorize` | Change to `/api/v1/authorize` |
| Invalid redirect_uri error | URI not registered in auth-api | Re-run auth-api seed (upsert fixes it) |
| User synced but 403 on APIs | Missing `X-Tenant-ID` header | Ensure headers injected in API client |
| 401 on /me even with token | Token may be expired or user not found | Check token expiry; re-login |
| Infinite loading on landing page buttons | useAuth stuck in isLoading=true on 401 | Fixed in useAuth.ts: 401 resolves immediately as unauthenticated |
| Infinite polling on callback | NATS event not delivered | Check NATS connection in service logs |
| Blank/error after SSO login | PKCE verifier missing from sessionStorage | Check `consumeVerifier()` returns non-null |
| Pod not running after deploy | K8s probe returning non-200 | Use `/healthz` route (not `/` which redirects) |
| 401 "user not found" with valid token | User not yet in service DB | Enable JIT provisioning in service; or check NATS delivery |
| 403 on catalog/menu with valid token | Permission codes in token don't match backend | Use canonical permission codes in auth-api (e.g. `catalog:view`) and in backend checks |
| Duplicate `roles`/`permissions` in login response | Legacy response shape | Fixed: auth-api returns them only at top level, not under `user` |
| "client not found" or "invalid_redirect" for pos-ui/subs/treasury/notifications | Wrong client_id or redirect_uri not in seed | Ensure auth-api seed includes `pos-ui` and tenant-aware redirect URIs; re-run seed |
| 404 on `/auth/me` or stuck on "Syncing your profile" | Frontend calling service API (e.g. booksapi) for profile | Call **SSO** `GET /api/v1/auth/me` with Bearer token; see treasury-ui `lib/auth/api.ts` and `useMe.ts` |
| "Access denied" on treasury-ui /platform page | AuthProvider checking wrong role name (`super_admin` instead of `superuser`) | Fixed: AuthProvider now checks `isPlatformOwner` and `superuser` role from SSO /me response |
| User has no local service roles after first login | JIT provisioning created user but didn't assign roles | Fixed: All backends now map JWT roles to service-level roles during JIT (e.g. superuser → finance_admin) |
| 429 on notifications /messages endpoint | Email rate limit exceeded for subscription plan | Check `max_emails_per_day` in JWT SubscriptionLimits; upgrade plan or wait for daily reset |
| Redirect to login after SSO login (subscription) | Backend returns 403 `subscription_inactive` on GET; frontend treats as auth error | Fix: backend must use mutations-only enforcement; frontend must check `data.code === 'subscription_inactive'` before redirecting |
| 403 on GET with expired subscription | Service uses `RequireActiveSubscription()` on all routes | Fix: use inline mutations-only middleware (skip GET/HEAD/OPTIONS) |
| Toast "subscription inactive" on every page load | Subscription 403 interceptor fires on read requests | Fix: backend should only enforce on mutations; if already fixed, clear browser cache |

---

## Security Checklist

- [x] PKCE used on all public clients (no client secret in browser)
- [x] `state` parameter stored and verified (CSRF protection)
- [x] PKCE verifier consumed after single use
- [x] Refresh tokens stored only in memory (not localStorage for security-sensitive apps)
- [x] CORS restricted to known domains (no wildcards in production)
- [x] All redirect URIs whitelisted explicitly in auth-api
- [x] JWT verified against JWKS endpoint (shared-auth-client library)

---

## Platform Owner Access Pattern

**Codevertex is the platform owner, not a business tenant.** Users linked to the `codevertex` organisation bypass tenant isolation.

### Detection
`GET /api/v1/auth/me` returns `is_platform_owner: true` when `primary_tenant.slug == "codevertex"` and the user has the `superuser` role.

### Service Enforcement
```typescript
// In any service's auth middleware:
if (user.is_platform_owner || user.roles.includes('superuser')) {
  // Skip tenant isolation — allow access to ALL tenant data
  return next();
}
// Otherwise enforce tenant_id === request.tenant_id
```

### Backend: Platform Owner Tenant Override (`?tenantId=`)

All Go backend services support a `?tenantId=<uuid>` query parameter on tenant-scoped endpoints for platform owners. This allows cross-tenant drill-down without requiring tenant headers.

**Pattern (implemented in all services — March 2026):**
```go
// In each handler's tenant resolution function:
ctx := r.Context()
if httpware.IsPlatformOwner(ctx) {
    if q := r.URL.Query().Get("tenantId"); q != "" {
        return uuid.Parse(q) // override to target tenant
    }
}
// Fallback: httpware context → JWT claims
tenantIDStr := httpware.GetTenantID(ctx)
```

**Frontend behaviour:**
- Platform owner UIs (orgSlug `codevertex`) skip `X-Tenant-ID`/`X-Tenant-Slug` headers (apiClient `setPlatformOwner(true)`)
- A `TenantFilter` dropdown in the header lets platform owners select a specific tenant
- Selected tenant is passed as `?tenantId=<uuid>` on API calls
- When no tenant is selected ("All Tenants"), the backend returns data across all tenants (for list endpoints) or requires explicit selection (for mutations/config)

**Services implementing this pattern:**
- treasury-api, inventory-api, logistics-api, pos-api, subscriptions-api, ordering-backend, notifications-api

---

## Multi-Step Account Registration

All account creation is centralised in **auth-ui** (`accounts.codevertexitsolutions.com/signup`). All other services redirect unauthenticated users here.

### Registration Steps
1. **Account** — Full name, email, password
2. **Organisation** — Search & join existing org (by slug) OR create new org (name, slug, size, use case)
3. **Plan** — Subscription tier recommendation with 14-day trial; fetched from subscription-api

### Org Roles
| Action | Role Assigned |
|--------|--------------|
| Join existing org | `member` (admin can promote later) |
| Create new org | `admin` (founding user becomes org admin) |

### Subscription Enforcement Post-Login
After login, non-platform users without an active subscription are redirected to the subscription selection page:
```
login success
  → check user.is_platform_owner → skip if true
  → GET /api/v1/tenants/{tenant_id}/subscription
  → status in [ACTIVE, TRIAL] → allow app access
  → status EXPIRED or 404 → redirect to /subscribe
```

---

## New Service OAuth Client Registration

When a new frontend integrates with SSO:

### Option A — Seed (MVP Services)
Add to `auth-api/cmd/seed/main.go` OAuth clients list and redeploy. Use for all services that are part of MVP.

### Option B — Admin API (Runtime)
For new services added post-MVP without redeployment:
```bash
# Requires valid superuser JWT
curl -X POST https://sso.codevertexitsolutions.com/api/v1/admin/clients \
  -H "Authorization: Bearer <superuser-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "my-new-service",
    "name": "My New Service",
    "redirect_uris": ["https://mynewservice.codevertexitsolutions.com/callback"],
    "scopes": ["openid", "profile", "email"],
    "public": true
  }'
```

**Rule:** seed = source of truth for MVP clients. Admin API = runtime additions. Both are valid.

---

## Public Tenant Endpoint

Services that need to resolve tenant UUIDs (e.g. subscription-api seed) use the public endpoint — **no authentication required:**

```
GET /api/v1/tenants/by-slug/{slug}
Response: { "id": "<uuid>", "name": "...", "slug": "...", "status": "active" }
```

This ensures cross-service UUID consistency without hardcoding values.
