# Subscription Gating Guide

**Last Updated:** March 29, 2026

## Principles

1. **Subscription NEVER blocks login.** Users must always be able to authenticate regardless of subscription status.
2. **Read operations always pass through.** GET/HEAD/OPTIONS are never gated by subscription — users can view their data even with expired subscriptions.
3. **Mutations require active subscription.** POST/PUT/PATCH/DELETE are blocked with 403 when subscription is inactive.
4. **Superuser and platform owner always bypass.** Both `claims.IsSuperuser()` and `claims.IsPlatformOwner` skip all subscription checks.
5. **Frontend shows upgrade UI, not login redirects.** Subscription 403s trigger banners/toasts/modals — never redirect to SSO or login page.

---

## Backend Pattern (Go Services)

### Mutations-Only Middleware

All Go services use this inline middleware in their router (same pattern as ordering-backend):

```go
api.Use(func(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Read-only methods always pass through
        if r.Method == http.MethodGet || r.Method == http.MethodHead || r.Method == http.MethodOptions {
            next.ServeHTTP(w, r)
            return
        }
        claims, ok := authclient.ClaimsFromContext(r.Context())
        if !ok {
            next.ServeHTTP(w, r)
            return
        }
        if claims.IsSuperuser() || claims.IsPlatformOwner || claims.IsSubscriptionActive() {
            next.ServeHTTP(w, r)
            return
        }
        w.Header().Set("Content-Type", "application/json")
        w.WriteHeader(http.StatusForbidden)
        _, _ = w.Write([]byte(`{"error":"Your subscription is not active. Please renew to continue.","code":"subscription_inactive","upgrade":true}`))
    })
})
```

### Error Response Format

All subscription enforcement returns:
```json
{
  "error": "Your subscription is not active. Please renew to continue.",
  "code": "subscription_inactive",
  "upgrade": true
}
```

The `upgrade: true` field is the key discriminator frontends use to distinguish subscription 403s from auth/permission 403s.

### Shared Auth-Client Convenience Function

`shared/auth-client/middleware.go` provides `RequireActiveSubscriptionForMutations()` for services that update to the latest shared-auth-client release. Services using a published version (e.g. v0.5.0) should use the inline pattern above.

### Services Reference

| Service | Enforcement | Notes |
|---------|------------|-------|
| ordering-backend | Mutations only (inline) | Reference implementation |
| pos-api | Mutations only (inline) | Fixed March 29, 2026 |
| treasury-api | Mutations only (inline) | Fixed March 29, 2026 |
| projects-api | Mutations only (inline) | Fixed March 29, 2026 |
| inventory-api | Mutations only (per-route) | Already correct |
| logistics-api | Mutations only (inline) | Already correct |
| auth-api | No enforcement | Core service (token authority) |
| subscriptions-api | No enforcement | Core service (licensing authority) |
| notifications-api | No enforcement | Uses plan-based email rate limiting instead |

---

## Frontend Pattern (Next.js/React)

### Architecture

```
Login → SSO callback → Token exchange → /me sync → Dashboard
                                                      ↓
                                           useSubscription() hook
                                           (lazy load from subscriptions-api)
                                                      ↓
                                    SubscriptionBanner (top of layout)
                                    SubscriptionGate (wraps gated features)
```

### Files Per Frontend

Each frontend implements these files:

| File | Purpose |
|------|---------|
| `src/lib/auth/subscription.ts` | `fetchSubscriptionInfo()` — fetches from subscriptions-api, returns null on error (fail-open) |
| `src/hooks/use-subscription.ts` | `useSubscription()` — React hook with `isActive`, `hasFeature()`, `isPastDue`, `isExpired`, etc. |
| `src/components/subscription/subscription-gate.tsx` | `<SubscriptionGate feature="...">` — wraps content, shows upgrade prompt when gated |
| `src/components/subscription/subscription-banner.tsx` | `<SubscriptionBanner />` — persistent top banner for trial expiry, past due, expired |

### Auth Store Requirements

Each frontend's Zustand auth store must include:
```typescript
subscriptionInfo: Record<string, unknown> | null | undefined;
setSubscriptionInfo: (info: Record<string, unknown> | null) => void;
```

Do NOT persist `subscriptionInfo` in Zustand's `partialize` — fetch fresh each session.

### API Client: 403 Discrimination

Each frontend's API client must add a subscription-403 interceptor alongside the existing 401 handler:

```typescript
// Axios-based:
private onSubscription403Callback: ((data: any) => void) | null = null;

public setOnSubscription403(callback: ((data: any) => void) | null) {
    this.onSubscription403Callback = callback;
}

private handleError = (error: any) => {
    if (error.response?.status === 401 && this.on401Callback) {
        this.on401Callback();
    }
    if (error.response?.status === 403 && this.onSubscription403Callback) {
        const data = error.response?.data;
        if (data?.code === 'subscription_inactive' || data?.upgrade === true) {
            this.onSubscription403Callback(data);
        }
    }
    return Promise.reject(error);
};
```

### Auth Provider: Skip Redirect for Subscription 403

Auth providers that handle 403 from `/me` must check the error body before redirecting:

```typescript
// WRONG: redirects to unauthorized on ANY 403
if (isError && statusCode === 403) {
  router.replace('/unauthorized');
}

// CORRECT: skip redirect for subscription 403
if (isError && statusCode === 403) {
  const data = (error as any)?.response?.data;
  if (data?.code === 'subscription_inactive' || data?.upgrade === true) return;
  router.replace('/unauthorized');
}
```

### useSubscription() Hook

The hook:
1. Waits for `status === "authenticated"` before fetching
2. Skips fetch for platform owners (auto-grants enterprise)
3. Fetches from `NEXT_PUBLIC_SUBSCRIPTIONS_API_URL/api/v1/subscription` with Bearer token + tenant headers
4. Returns `null` on error (fail-open — never blocks UI)
5. Exposes: `isActive`, `isPastDue`, `isExpired`, `needsSubscription`, `hasFeature(code)`, `getLimit(key)`

### SubscriptionBanner

- Placed at top of org-scoped layout, before main content
- Shows nothing for active/trial subscriptions (unless trial ends in < 3 days)
- Shows warning for trial ending soon, past due payment
- Shows error for expired subscriptions
- Shows info for free tier (no subscription)
- Dismissible per session
- Links to subscriptions-ui for upgrade/billing actions

### SubscriptionGate

- Wraps content that requires a specific feature or plan
- Shows children optimistically during loading
- Shows upgrade prompt (lock icon + upgrade button) when feature is unavailable
- Links to subscriptions-ui subscribe page

---

## Adding Subscription Gating to a New Service

### Backend

1. Add the mutations-only middleware to your router (see pattern above)
2. Ensure `claims.IsSuperuser()` and `claims.IsPlatformOwner` bypass
3. Response must include `"code":"subscription_inactive"` and `"upgrade":true`

### Frontend

1. Add `subscriptionInfo` + `setSubscriptionInfo` to your Zustand auth store
2. Copy `subscription.ts`, `use-subscription.ts`, `subscription-gate.tsx`, `subscription-banner.tsx` from ordering-frontend
3. Adapt auth store import path
4. Add `<SubscriptionBanner />` to your org-scoped layout
5. Add `setOnSubscription403` to your API client
6. Fix auth-provider 403 handling to skip redirect for subscription 403
7. Wrap gated actions with `<SubscriptionGate feature="...">` or check `useSubscription().isActive`
