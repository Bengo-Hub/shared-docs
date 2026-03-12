# SSO: Authenticated requests and 401 prevention

**Last updated:** March 2026  
**Related:** [sso-integration-guide.md](./sso-integration-guide.md), [TRINITY-AUTHORIZATION-PATTERN.md](./TRINITY-AUTHORIZATION-PATTERN.md)

---

## Problem

After a user logs in via SSO, calls to authenticated endpoints (e.g. `GET /api/v1/{tenant}/auth/me`, cart, orders) sometimes return **401 Unauthorized** even when the token is present. This affects ordering-frontend/backend, cafe-website, treasury, pos, subscriptions, inventory, logistics. The cause is usually one of:

1. **Token not sent** – API client not attaching `Authorization: Bearer <token>` (e.g. token getter not set, or called before store is updated).
2. **Tenant missing** – Backend expects `X-Tenant-ID` or tenant in path; frontend does not send it or sends it only after a separate profile call.
3. **JWT validation failure** – Backend validator (JWKS URL, issuer, audience) does not match auth-api; or token expired.
4. **User not in service DB** – Backend requires the user to exist locally (e.g. ordering-backend); JIT provisioning fails (e.g. wrong tenant slug in path).

---

## Contract: what frontends must do

| Requirement | Detail |
|-------------|--------|
| **Attach token to every request** | Before any call to a protected endpoint, the API client must read the access token from the auth store and set `Authorization: Bearer <token>`. Use a getter (e.g. `attachAuthTokenGetter(() => store.session?.accessToken ?? null)`) so the latest token is always used. |
| **Send tenant context** | For tenant-scoped backends, send `X-Tenant-ID` (UUID) and optionally `X-Tenant-Slug` on every request. Persist `tenant_id` and `tenant_slug` from the first successful profile response (SSO or service `/me`) to localStorage and add them in the request interceptor. |
| **Use correct base URL and path** | Ordering-backend uses `/api/v1/{tenant}/...`. The frontend must call e.g. `GET /api/v1/urban-loft/auth/me` with the tenant slug from the URL path or localStorage. |

---

## Contract: what backends must do

| Requirement | Detail |
|-------------|--------|
| **Validate JWT** | Use the same issuer/JWKS as auth-api. Reject invalid or expired tokens with 401. |
| **Resolve tenant** | From path (`/{tenant}/...`) or `X-Tenant-ID` header. Do not require both if one is sufficient. |
| **JIT user** | If the token is valid but the user is not in the local DB, create the user (and tenant membership) from token claims and optional NATS events. Return 401 only if JIT fails (e.g. invalid tenant). |
| **Response shape** | Return JSON with camelCase keys matching frontend types: `session` (accessToken, refreshToken, expiresAt, sessionId), `user` (id, email, fullName, roles, permissions, …), `tenant_id`, `tenant_slug`. |

---

## Backend DTO ↔ frontend types alignment

Frontends must map backend response keys exactly. Mismatches (e.g. snake_case vs camelCase, or different field names) cause missing data and can look like “not authenticated”.

### ordering-backend ↔ ordering-frontend

| Backend (Go) | JSON key | Frontend type (TypeScript) |
|--------------|----------|----------------------------|
| AuthResponsePayload | session, user, tenant_id, tenant_slug | AuthResponse.session, .user, .tenant_id?, .tenant_slug? |
| SessionResponsePayload | accessToken, refreshToken, expiresAt, sessionId | SessionTokens |
| UserResponsePayload | id, email, fullName, phone, avatarUrl, roles, permissions, loyaltyPoints, availableCoupons, preferences, lastLoginAt, createdAt, updatedAt | UserProfile |

Ordering-backend uses camelCase in JSON; ordering-frontend types use the same. No mapping layer needed if backend keeps this shape.

### auth-api (SSO) GET /api/v1/auth/me

Returns a flat user object (id, email, profile, roles, permissions, tenant_id, tenant_slug, tenant). Frontends that call SSO /me (e.g. for fallback) must map `profile.name` / `profile.full_name` to `fullName`, and `roles` / `permissions` to the service’s role/permission types.

### Other services (treasury, pos, subscriptions, inventory, logistics)

Each should expose a consistent auth/profile response (session, user, tenant_id, tenant_slug) with camelCase keys. Frontends should define types that match the backend DTOs and use them in API client and store.

---

## E2E: assert no 401 after login

1. **Auth-ui:** After login, the page calls GET /api/v1/auth/me (SSO; with cookie). Assert that the request returns 200 and that the response body includes roles and permissions (user synced at SSO). Assert that the navbar shows authenticated state (e.g. Dashboard link), not Log In.
2. **Ordering-frontend:** The 401 test covers SSO /me (when observed, or via auth-ui E2E), at least two service endpoints, and role/permission mapping: ordering-backend GET /api/v1/{tenant}/auth/me – assert 200 and response includes user.roles and user.permissions; second endpoint GET /api/v1/{tenant}/customers/orders/summary – assert 200; SSO GET /api/v1/auth/me when observed – assert 200 (otherwise covered by auth-ui E2E).
3. **Other UIs:** Same idea: after login, assert at least one authenticated request returns 200 and the UI shows authenticated content.

---

## Checklist per service

- [ ] **ordering-frontend:** Token getter attached; X-Tenant-ID and X-Tenant-Slug set from store/localStorage; base URL includes tenant path for tenant-scoped calls; types match ordering-backend DTOs.
- [ ] **ordering-backend:** JWT validated with shared validator; tenant from path; JIT user on 404; response shape matches frontend AuthResponse.
- [ ] **treasury-ui / treasury-api:** Same pattern (token, tenant headers, DTO alignment).
- [ ] **pos-ui / pos backend:** Same pattern.
- [ ] **subscriptions-ui:** Same pattern.
- [ ] **cafe-website:** Same pattern; callback stores token and tenant; authenticated requests use Bearer + X-Tenant-ID.
- [ ] **inventory-ui, logistics-ui:** Same pattern.
