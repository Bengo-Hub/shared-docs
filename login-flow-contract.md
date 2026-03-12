# Login Flow Contract (SSO)

**Last updated:** March 2026

This document defines the canonical login flow contract for all frontends that integrate with BengoBox SSO (auth-api/auth-ui). It aligns with [sso-integration-guide.md](sso-integration-guide.md) and [TRINITY-AUTHORIZATION-PATTERN.md](TRINITY-AUTHORIZATION-PATTERN.md).

---

## 1. Canonical Signatures

All frontends should follow the same logical contract. Two patterns exist for historical reasons; **preferred** is (returnTo first, tenant optional).

### Preferred (ordering-frontend, rider-app, cafe-website)

```typescript
// Start login: returnTo = URL to resume after login; tenant = slug when in tenant context (e.g. from path).
redirectToSSO(returnTo?: string, tenant?: string): Promise<void>

// Handle OAuth callback: callbackUrl must match the redirect_uri used in the authorize request.
handleSSOCallback(code: string, callbackUrl: string, tenantSlug?: string): Promise<void>
```

- **Tenant-scoped UIs** (ordering, logistics, treasury, pos, inventory): When the user is on a route that includes `orgSlug` (e.g. `/[orgSlug]/dashboard`), pass that slug as `tenant` / `tenantSlug` so the authorize URL includes `?tenant=<slug>` and the token is minted for that org. Callback URL must match seed (e.g. `https://ordersapp.../urban-loft/auth/callback`).
- **Platform / mixed UIs** (notifications, subscriptions): Support both platform-level and tenant-level access. When in tenant context (e.g. route or selection), pass `tenant`; when at platform level, omit it. Backend and filters behave per section 3 below.

### Variant (treasury-ui, pos-ui, inventory-ui)

Some tenant-scoped UIs use **orgSlug first** (required) because every route is under `[orgSlug]`:

```typescript
redirectToSSO(orgSlug: string, returnTo?: string): Promise<void>
handleSSOCallback(orgSlug: string, code: string, callbackUrl: string): Promise<void>
```

Behavior is the same: callback URL is `origin/${orgSlug}/auth/callback`, and the authorize URL must include `tenant=<orgSlug>` so the token is minted for that tenant. These UIs should still pass `tenant` into `buildAuthorizeUrl` (either as param or via orgSlug).

---

## 2. Service Summary Table

| Service | Client ID | Callback path | redirectToSSO | handleSSOCallback | Notes |
|---------|-----------|----------------|--------------|-------------------|-------|
| **ordering-frontend** | ordering-ui | `/{tenant}/auth/callback` | `(returnTo?, tenant?)` | `(code, callbackUrl, tenantSlug?)` | Canonical; tenant from path. |
| **treasury-ui** | treasury-ui | `/{orgSlug}/auth/callback` | `(orgSlug, returnTo?)` | `(orgSlug, code, callbackUrl)` | Tenant required in route. |
| **pos-ui** | pos-ui | `/{orgSlug}/auth/callback` | `(orgSlug, returnTo?)` | `(orgSlug, code, callbackUrl)` | Same as treasury. |
| **inventory-ui** | inventory-ui | `/{orgSlug}/auth/callback` | `(orgSlug, returnTo?)` | `(orgSlug, code, callbackUrl)` | Same as treasury. |
| **logistics-ui** | logistics-ui | `/{orgSlug}/auth/callback` | `(returnTo?, tenant?)` | `(code, callbackUrl, tenantSlug?)` | Aligned to preferred; tenant from path when available. |
| **notifications-ui** | notifications-ui | `/auth/callback` or `/{tenant}/auth/callback` | `(returnTo?, tenant?)` | `(code, callbackUrl)` | Platform + tenant; optional tenant. |
| **subscriptions-ui** | subscriptions-ui | `/auth/callback` or `/{tenant}/auth/callback` | `(returnTo?, tenant?)` | `(code, callbackUrl)` | Platform + tenant; optional tenant. |
| **rider-app** | rider-app | `/auth/callback` | `(returnTo?, tenant?)` | `(code, callbackUrl)` | Tenant optional for join flow. |
| **cafe-website** | cafe-website | `/auth/callback` | `(returnTo?)` | `(code, callbackUrl)` | No tenant in path. |
| **auth-ui** | auth-ui | N/A (login UI) | N/A | N/A | Users log in here; no redirectToSSO. |

Production hosts and redirect URI patterns are in [sso-integration-guide.md](sso-integration-guide.md) and `auth-api/cmd/seed/main.go`.

---

## 3. Platform vs Tenant Scope (All Services)

Backends are built to support **both platform scope and tenant scope**. Frontends must behave consistently.

### Platform users (e.g. platform owner, superuser)

- **Headers:** Do **not** send `X-Tenant-ID` or `X-Tenant-Slug` (or send only when user explicitly selects a tenant for the request).
- **UI:** Show **tenant dropdown / tenant filter** on list pages and data tables so the user can scope data to a tenant. Use a **shared, centralized tenant-select component** where applicable so logic is controlled from one place.
- **Login:** May land on platform-level routes (e.g. `/dashboard`) or tenant routes; pass `tenant` only when the user is in a tenant context (e.g. path contains orgSlug).

### Tenant users (single-tenant org members)

- **Headers:** Send `X-Tenant-ID` and optionally `X-Tenant-Slug` on **every** request to tenant-scoped backends (from profile/me or first successful login).
- **UI:** Do **not** show tenant dropdown / tenant filter; all data is already scoped to that tenant. Backend filters by tenant from headers.
- **Login:** When on a tenant route (e.g. `/{orgSlug}/...`), pass `tenant` / `orgSlug` so the token is minted for that org.

### Notifications-ui and Subscriptions-ui (core, both scopes)

- These are **core services** that other services integrate with (like auth-ui/auth-api). They are not only tenant-scoped in the frontend: they support **both platform and tenant** access.
- **Routes:** May be platform-level (e.g. `/dashboard`) or tenant-level (e.g. `/{orgSlug}/...`) if such routes exist. Seed allows both `/auth/callback` and `/{tenant}/auth/callback`.
- **Login flow:** Same as others: when in tenant context, pass `tenant` to `redirectToSSO` and use tenant in callback path if applicable; when at platform level, omit tenant. Authorize URL and token minting follow the same rules.
- **Headers:** Platform users do not send tenant by default (tenant filters shown); tenant users send tenant in headers (no tenant filter).
- **Backend:** Already supports both scopes; frontend only needs to pass or omit tenant and show/hide tenant filters as above.

---

## 4. Build Authorize URL

- **Authorize URL:** `GET https://sso.codevertexitsolutions.com/api/v1/authorize` with PKCE (`code_challenge`, `code_challenge_method=S256`), `client_id`, `redirect_uri`, `state`, and optional **`tenant`**.
- When the frontend has a tenant context (e.g. from path or selection), pass `tenant` so auth-api mints the token for that org. When at platform level or no tenant context, omit `tenant`; auth-api may resolve from user’s primary org for direct login from auth-ui.
- `redirect_uri` must match exactly one of the client’s redirect URIs in the seed (production domains in sso-integration-guide).

---

## 5. Callback and After Login

- Callback page: read `code` (and `state`) from query, call `handleSSOCallback(code, callbackUrl)`. `callbackUrl` must be the same as `redirect_uri` used in the authorize step.
- After tokens are stored: fetch profile (SSO `GET /api/v1/auth/me` or service’s `/auth/me` with fallback to SSO), then redirect to `returnTo` (e.g. from `sessionStorage`) or default destination.
- Persist `tenant_id` and `tenant_slug` from profile when present so headers and UI can follow platform vs tenant rules above.

---

## 6. Tenant Select Filter (Recommendation)

- Use a **shared, centralized tenant-select filter component** in each frontend that supports platform scope. Use it on list pages and data tables where tenant filtering applies.
- **Platform users:** Component visible; selection drives `X-Tenant-ID` / `X-Tenant-Slug` for the request (or scope in URL).
- **Tenant users:** Component hidden or not rendered; tenant is fixed from auth context and headers.

This keeps “show tenant filter vs not” and “send tenant headers vs not” consistent and maintainable across services.
