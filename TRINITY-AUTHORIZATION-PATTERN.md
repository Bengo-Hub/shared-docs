# Trinity Authorization Pattern

**Last updated:** March 29, 2026 — Subscription enforcement changed to mutations-only across all services (pos-api, treasury-api, projects-api fixed). Frontend 403 discrimination added: subscription 403s show upgrade banners instead of redirecting to login. SubscriptionBanner + SubscriptionGate + useSubscription hook rolled out to all frontends. Platform owner bypass added to subscription middleware.

## Overview

The Trinity Authorization Pattern is a comprehensive authorization strategy that combines three layers of access control to provide robust, scalable, and flexible authorization across the entire BengoBox ecosystem.

```
Authorization = RBAC (Auth-Service) + Licensing (Subscription-Service) + Resources (Domain Services)
```

---

## The Three Layers

### Layer 1: RBAC (Role-Based Access Control) - Auth-Service

**Purpose**: User identity, authentication, and basic role assignments

**Owned By**: Auth-Service

**Components**:
- User identity (email, phone, password)
- Global roles (`superuser`, `admin`, `user`)
- Service-specific roles (can be defined by services)
- JWT token issuance with **roles** and **permissions** (canonical codes) from a single role–permission table
- Session management

**Canonical permission codes:** Auth-service defines one set of permission codes (e.g. `catalog:view`, `catalog:manage`, `orders:read`, `riders:read`) and issues them in the JWT access token and in GET /me. All microservices use these same codes for authorization; no service defines its own duplicate permission list for cross-cutting authz.

**Example Roles**:
- `superuser` - Full access across all services
- `admin` - Administrative access in specific service
- `user` - Standard user access
- `customer` - Ordering service customer
- `rider` - Logistics service rider
- `staff` - POS service staff member

---

### Layer 2: Licensing (Feature Entitlements) - Subscription-Service

**Purpose**: Feature availability and usage limits based on subscription plan

**Owned By**: Subscription-Service

**Components**:
- Subscription plans (Starter, Growth, Professional)
- Feature gates (which features are enabled)
- Usage limits (max riders, max orders per day, etc.)
- Usage tracking (current usage vs limits)
- Overage detection and billing

**Example Features**:
- `customer_portal` - Basic ordering
- `loyalty_program` - Loyalty points feature
- `multi_outlet` - Multiple outlet support
- `api_webhooks` - Webhook API access
- `route_optimization` - Advanced routing algorithms

**Example Limits**:
- `max_riders: 15` - Maximum active riders
- `max_orders_per_day: 1000` - Maximum orders per day
- `max_admins: 3` - Maximum admin users

---

### Layer 3: Resources (Domain-Specific Permissions) - Domain Services

**Purpose**: Fine-grained permissions and resource-level access control

**Owned By**: Individual Domain Services (Ordering, Logistics, POS, etc.)

**Components**:
- Service-specific permissions
- Resource-level access control (e.g., can only edit own orders)
- Business rule enforcement
- Data ownership and isolation

**Service-Level Permission System (Django-style RBAC):**

Each domain service implements its own fine-grained permission system stored in its database. Permission codes follow the format `{service}.{module}.{action}` with Django-style actions: `add`, `view`, `view_own`, `change`, `change_own`, `delete`, `delete_own`, `manage`, `manage_own`.

**Ent schemas per service** (following the treasury-api reference pattern):
- `{Service}Permission` — permission_code (unique), module, action, resource, description
- `{Service}Role` — tenant-scoped roles with role_code, is_system_role flag
- `RolePermission` — many-to-many junction table (role_id + permission_id)
- `UserRoleAssignment` — tenant_id, user_id, role_id, assigned_by, expires_at
- `{Service}User` — JIT-provisioned local user ref with auth_service_user_id, sync_status
- `RateLimitConfig` — DB-loaded rate limit settings per service
- `ServiceConfig` — key-value config with platform defaults and per-tenant overrides

**RBAC module per service** (`internal/modules/rbac/`): service.go, repository.go, repository_ent.go, models.go — provides EnsureUserFromToken (JIT), HasPermission, HasRole, AssignRole, RevokeRole.

**Middleware chain** (in order): Global rate limit → Auth (JWT/API key via shared-auth-client) → Subscription enforcement (RequireActiveSubscriptionForMutations — mutations only) → JIT user provisioning (with role assignment from JWT) → Route-level RequirePermission/RequireAnyPermission.

**Subscription enforcement by service (March 2026, updated March 29):**
- **Enforced (mutations only):** treasury-api, inventory-api, pos-api, ordering-backend, logistics-api, projects-api — all use mutations-only enforcement: GET/HEAD/OPTIONS pass through, POST/PUT/PATCH/DELETE require active subscription.
- **NOT enforced (core services, free in all plans):** auth-api (token authority), subscriptions-api (subscription authority), notifications-api (core messaging). Notifications uses **plan-based email rate limiting** (`max_emails_per_day` from JWT `SubscriptionLimits`) instead of subscription gating.
- Superuser and platform owner always bypass subscription enforcement.

**Subscription enforcement rules:**
- Subscription NEVER blocks authentication or login. Users must always be able to log in regardless of subscription status.
- Read operations (GET) are always allowed so users can view their data even with an expired subscription.
- Mutation operations (POST/PUT/PATCH/DELETE) are blocked with HTTP 403 and response body `{"error":"...","code":"subscription_inactive","upgrade":true}`.
- The `upgrade: true` field in the JSON response distinguishes subscription 403s from auth/permission 403s.
- Frontends must discriminate subscription 403s from auth 403s: subscription 403 → show upgrade banner/toast, NOT redirect to login. Auth 403 → redirect to unauthorized page.

**Frontend subscription gating pattern:**
Each frontend implements lazy subscription loading via `useSubscription()` hook + `SubscriptionBanner` (persistent top banner) + `SubscriptionGate` (wraps gated features). Subscription info is fetched AFTER login from subscriptions-api; loading never blocks UI. Platform owners get automatic `active/enterprise` status.

**Example service-level permissions:**
- `treasury.payments.add`, `treasury.payments.view`, `treasury.payments.manage`
- `ordering.orders.add`, `ordering.catalog.change`, `ordering.config.manage`
- `logistics.tasks.add`, `logistics.fleet.manage`, `logistics.zones.view`
- `notifications.templates.change`, `notifications.providers.manage`

**Relationship to Layer 1 (auth-service) permissions:**
Layer 1 canonical codes (e.g. `catalog:view`) are global cross-cutting codes issued in JWT by auth-service. Layer 3 service-level codes (e.g. `ordering.catalog.view`) are fine-grained codes managed locally by each service. Both can coexist: the shared-auth-client `RequirePermission` middleware checks `claims.Permissions` (from JWT), while the service RBAC module checks local DB permissions via `rbacService.HasPermission()`.

**Superuser bypass:** All permission checks (both JWT-level and service-level) are bypassed for users with the `superuser` role. Platform owner (`is_platform_owner`) bypasses tenant isolation and platform route restrictions.

**Just-in-Time (JIT) provisioning:** When a microservice receives a valid JWT but has no local user record for `sub`, it should create a minimal user from token claims and then proceed (not return 401). This avoids "user not found" 401s when NATS sync is delayed. Resource-level (Layer 3) checks still apply after the user exists. **JIT must also assign a default service-level role** based on global JWT roles (e.g. superuser/admin → service admin, staff → manager/operator, others → viewer). This ensures local RBAC queries return correct role data for role-based UI gating and RBAC management endpoints. All services now implement this: treasury-api (finance_admin), inventory-api (inventory_admin), pos-api (pos_admin), logistics-api (admin), notifications-api (super_admin).

**JIT tenant sync:** All Go backends must sync the tenant from auth-api when the request carries a tenant slug (e.g. from JWT or path). If the slug is present and the tenant is missing locally, the service should fetch and upsert the tenant from auth-api before processing the request. This avoids "tenant not found" after SSO login when the token was minted for a tenant (via `?tenant=` on the authorize URL).

**Tenant ID format:** Frontends must send `X-Tenant-ID` as the **tenant UUID** from auth-api (e.g. from GET `/api/v1/auth/me` response `tenant_id`). Do not send a slug or custom string (e.g. `tenant-urban-loft`). Auth-api and all SSO-integrated backends must include `X-Tenant-ID` in CORS `Access-Control-Allow-Headers` (app and ingress) so browser preflights succeed.

**Auth/me caching:** Auth-api caches GET `/api/v1/auth/me` in Redis by user ID with TTL = token expiry. Frontends should use TanStack Query (or similar) with a TTL aligned to token lifetime so the first read is fast and DB load is reduced.

**Claims best practices:** Keep claims in the token stable (e.g. user ID, tenant, roles, permissions). Avoid putting volatile or rarely used data in the token; services can resolve fine-grained rules from role/claims locally.

---

## Integration Flow

### 1. User Authentication (Auth-Service)

```typescript
// User logs in
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password",
  "tenant_slug": "urban-cafe"
}

// Auth-service validates credentials and issues JWT
Response:
{
  "access_token": "jwt-token",
  "refresh_token": "refresh-token",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "tenant_id": "tenant-uuid",
    "roles": ["admin", "user"]
  }
}
```

### 2. JWT Claims Extension (Subscription-Service)

```typescript
// Auth-service enriches JWT with subscription data
// Before issuing token, auth-service calls subscription-service:

GET /api/v1/{tenant_id}/subscription/claims

Response:
{
  "subscription_features": [
    "customer_portal",
    "loyalty_program",
    "multi_outlet"
  ],
  "subscription_limits": {
    "max_riders": 15,
    "max_orders_per_day": 1000,
    "max_admins": 3
  },
  "subscription_status": "active",
  "subscription_plan": "growth"
}

// Auth-service includes this in JWT claims
```

### 3. Enhanced JWT Token

```json
{
  "sub": "user-uuid",
  "tenant_id": "tenant-uuid",
  "email": "user@example.com",
  "roles": ["admin", "user"],
  "subscription_features": [
    "customer_portal",
    "loyalty_program",
    "multi_outlet"
  ],
  "subscription_limits": {
    "max_riders": 15,
    "max_orders_per_day": 1000,
    "max_admins": 3
  },
  "subscription_status": "active",
  "subscription_plan": "growth",
  "exp": 1234567890,
  "iat": 1234567890
}
```

### 4. Request Authorization (Domain Service)

```typescript
// User makes request to domain service
POST /api/v1/{tenant}/orders
Authorization: Bearer {jwt-token}

// Domain service validates authorization:

// Step 1: Validate JWT (RBAC check)
const claims = validateJWT(token);
if (!claims) {
  return 401 Unauthorized;
}

// Step 2: Check service-specific RBAC permissions
if (!hasPermission(claims.roles, "orders:create")) {
  return 403 Forbidden("Insufficient permissions");
}

// Step 3: Check subscription features (Licensing)
if (!claims.subscription_features.includes("customer_portal")) {
  return 403 Forbidden("Feature not available on current plan");
}

// Step 4: Check resource limits (Licensing)
const todayOrders = await getTodayOrderCount(tenantId);
if (todayOrders >= claims.subscription_limits.max_orders_per_day) {
  // Allow with overage tracking
  await subscriptionService.ReportOverage(tenantId, "order_count", 1);
  // Or reject if hard limit
  // return 403 Forbidden("Daily order limit exceeded");
}

// Step 5: Check domain-specific business rules (Resources)
if (isOrderValid(requestData)) {
  // Create order
  return createOrder(requestData);
}
```

---

## Implementation Patterns

### Pattern 1: Feature Gate Check

```typescript
// Before allowing feature access
const checkFeature = async (tenantId: string, featureCode: string): Promise<boolean> => {
  // Check cache first (Redis)
  const cacheKey = `subscription:feature:${tenantId}:${featureCode}`;
  const cached = await redis.get(cacheKey);
  
  if (cached !== null) {
    return cached === "true";
  }
  
  // Check subscription service
  const hasFeature = await subscriptionService.HasFeature(tenantId, featureCode);
  
  // Cache result (60s TTL)
  await redis.set(cacheKey, hasFeature ? "true" : "false", "EX", 60);
  
  return hasFeature;
};

// Usage
if (!await checkFeature(tenantId, "loyalty_program")) {
  return ErrFeatureNotAvailable;
}
```

### Pattern 2: Limit Enforcement

```typescript
// Before creating resource
const checkLimit = async (
  tenantId: string,
  metricType: string,
  limitName: string
): Promise<{ allowed: boolean; current: number; limit: number }> => {
  // Get limits from JWT claims or subscription service
  const limits = await subscriptionService.GetLimits(tenantId);
  const currentUsage = await subscriptionService.GetUsage(tenantId, metricType, "current");
  
  const limit = limits[limitName];
  
  return {
    allowed: currentUsage < limit,
    current: currentUsage,
    limit: limit,
  };
};

// Usage
const limitCheck = await checkLimit(tenantId, "rider_count", "max_riders");
if (!limitCheck.allowed) {
  // Option 1: Reject
  return ErrLimitExceeded(`Maximum ${limitCheck.limit} riders allowed`);
  
  // Option 2: Allow with overage
  await subscriptionService.ReportOverage(tenantId, "rider_count", 1);
}
```

### Pattern 3: Usage Reporting

```typescript
// After creating resource
const reportUsage = async (
  tenantId: string,
  metricType: string,
  value: number,
  metadata?: any
) => {
  await subscriptionService.ReportUsage(tenantId, metricType, value, metadata);
};

// Usage
await createOrder(orderData);
await reportUsage(tenantId, "order_count", 1, {
  order_id: order.id,
  date: new Date().toISOString().split('T')[0],
});
```

### Pattern 4: Trinity Authorization Middleware

```typescript
// Express/Next.js middleware
const trinityAuth = (
  requiredPermissions: string[],
  requiredFeatures: string[] = [],
  resourceCheck?: (req: Request) => Promise<boolean>
) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    // Step 1: Extract and validate JWT
    const token = extractToken(req);
    const claims = await validateJWT(token);
    
    if (!claims) {
      return res.status(401).json({ error: "Unauthorized" });
    }
    
    // Step 2: Check RBAC permissions
    const hasPermissions = requiredPermissions.every(perm =>
      hasPermission(claims.roles, perm)
    );
    
    if (!hasPermissions) {
      return res.status(403).json({ error: "Insufficient permissions" });
    }
    
    // Step 3: Check subscription features
    const hasFeatures = requiredFeatures.every(feature =>
      claims.subscription_features?.includes(feature)
    );
    
    if (!hasFeatures) {
      return res.status(403).json({ 
        error: "Feature not available on current plan",
        required_features: requiredFeatures,
        available_features: claims.subscription_features,
      });
    }
    
    // Step 4: Check resource-level permissions (if provided)
    if (resourceCheck) {
      const hasResourceAccess = await resourceCheck(req);
      if (!hasResourceAccess) {
        return res.status(403).json({ error: "Resource access denied" });
      }
    }
    
    // Attach claims to request for use in handlers
    req.user = claims;
    next();
  };
};

// Usage
app.post(
  '/api/v1/orders',
  trinityAuth(
    ['orders:create'], // Required permissions
    ['customer_portal'], // Required features
    async (req) => {
      // Resource-level check: can only create orders for own tenant
      return req.user.tenant_id === req.body.tenant_id;
    }
  ),
  createOrderHandler
);
```

---

## Plan Transitions & Grace Periods

### Upgrade Flow

```typescript
// User upgrades plan
1. Subscription service creates plan transition record
2. Calculates proration
3. Emits billing event to treasury
4. After payment confirmation:
   - Updates subscription status
   - Activates new features
   - Updates JWT claims (on next token refresh)
   - Emits subscription.entitlements_changed event
5. All services refresh feature gates
```

### Downgrade Flow

```typescript
// User downgrades plan
1. Subscription service schedules downgrade (period-end or immediate)
2. Before downgrade:
   - Checks if current usage exceeds new plan limits
   - Shows warning if limits will be exceeded
   - Allows user to cancel downgrade
3. On downgrade:
   - Deactivates premium features
   - Updates limits
   - Emits subscription.entitlements_changed event
4. Services gracefully disable premium features
```

### Grace Period

```typescript
// Subscription expires
1. Subscription service marks subscription as expired
2. Grace period starts (e.g., 7 days)
3. During grace period:
   - Features remain active
   - Usage tracking continues
   - Warnings shown to users
4. After grace period:
   - Features disabled
   - Access restricted (read-only mode)
   - Billing retry attempts continue
```

---

## Best Practices

### 1. Cache Feature Gates

**Rationale**: Feature checks happen frequently; caching reduces latency

**Implementation**:
- Cache in Redis with 60s TTL
- Invalidate cache on subscription changes
- Use stale-while-revalidate pattern

### 2. Fail Closed for Feature Checks

**Rationale**: If subscription service is unavailable, deny access rather than allow

**Implementation**:
- If feature check fails → assume feature unavailable
- Log error for monitoring
- Alert operations team

### 3. Real-time Usage Reporting

**Rationale**: Accurate usage tracking enables proper limit enforcement

**Implementation**:
- Report usage immediately after action
- Batch multiple reports for efficiency
- Retry on failure with exponential backoff

### 4. Soft Limits with Overage

**Rationale**: Better user experience - allow usage but charge for overages

**Implementation**:
- Allow action even if limit exceeded
- Track overage quantity
- Calculate overage charges daily
- Emit billing events for overages

### 5. JWT Claims Caching

**Rationale**: Reduce calls to subscription service for every request

**Implementation**:
- Include subscription data in JWT claims
- Cache claims for token lifetime
- Refresh claims on token refresh
- Invalidate cache on subscription changes

---

## Product-Level Entitlements (Added February 2026)

### Layer Between RBAC and Feature Licensing

Products represent the bridge between RBAC (who can access) and Feature Licensing (what's available):

**Product activation flow:**
1. Tenant subscribes to a bundle (e.g., Professional)
2. Bundle activates products: ordering, logistics, treasury, notifications, auth
3. Active product IDs are embedded in JWT claims
4. Frontend checks `jwt.products` array before rendering service-specific UI
5. Backend middleware validates product access before processing API calls

**Product → Service mapping:**

| Product | Service | Frontend App |
|:---|:---|:---|
| ordering | ordering-service | ordering-frontend |
| logistics | logistics-service | rider-app, logistics-ui |
| treasury | treasury-service | (embedded in ordering) |
| pos | pos-service | pos-frontend |
| analytics | analytics-service | (embedded dashboard) |
| notifications | notifications-service | (backend only) |
| auth | auth-service | auth-ui |
| inventory | inventory-service | inventory-frontend |

### Bundle-Based Activation

| Bundle | Products Included | Price Tier |
|:---|:---|:---|
| Starter | ordering, auth | Entry-level |
| Professional | ordering, logistics, treasury, notifications, auth | Mid-tier |
| Enterprise | All 8 products | Full platform |

---

## Monitoring & Alerts

### Metrics to Track

- Feature check latency (p50, p95, p99)
- Feature check success/failure rates
- Usage reporting latency
- Limit enforcement accuracy
- Overage detection accuracy
- Plan transition success rates

### Alerts

- High feature check failure rate (>5%)
- Subscription service unavailable
- Usage reporting failures
- Overage calculation errors
- Plan transition failures

---

## References

- [Subscription Service Integration](../../subscription-service/docs/integrations.md)
- [Auth Service Integration](../../auth-service/auth-api/docs/integrations.md)
- [Cross-Service Data Ownership](./CROSS-SERVICE-DATA-OWNERSHIP.md)

---

## Platform Owner Pattern (Codevertex)

**Codevertex is NOT a business tenant** — it is the platform owner. Any user whose `primary_tenant = "codevertex"` and who has the `superuser` role has **cross-tenant access** to all tenants' data.

### Subscription and tenant sync
- **Subscription-service must NOT create tenant subscriptions for the platform owner.** Only business (customer) organisations have subscriptions. The subscription-api seed excludes the platform owner slug so no `TenantSubscription` is created for Codevertex.
- **All services that sync tenants** (in seed or at startup) **must sync the codevertex platform org** in addition to other default tenants, so the platform tenant row exists in each service DB (e.g. ordering-backend, inventory-api, subscriptions-api app, notifications-api seed).
- **Platform org admin user:** Each service that maintains local user/role/permission data must sync or JIT-provision the platform admin user (auth-api super admin, e.g. `admin@codevertexitsolutions.com`) and assign **all permissions** in that service as the global admin user (e.g. superuser + admin roles in ordering-backend, finance_admin in treasury-api, admin role in logistics-api JIT).

### Token Claims
`GET /api/v1/auth/me` returns `is_platform_owner: true` when the user's primary tenant slug is `codevertex`. Services should grant full read/write when this flag is set:

```
if claims.roles.includes("superuser") || user.is_platform_owner:
    → bypass tenant isolation checks
    → allow reading/writing any tenant's data
```

### Backend Tenant Override for Platform Owners

All tenant-scoped handlers support `?tenantId=<uuid>` query parameter for platform owners (March 2026). The standard pattern:

```go
func getTenantID(r *http.Request) (uuid.UUID, error) {
    ctx := r.Context()
    // Platform owner can target any tenant via query param
    if httpware.IsPlatformOwner(ctx) {
        if q := r.URL.Query().Get("tenantId"); q != "" {
            return uuid.Parse(q)
        }
    }
    // Standard resolution: httpware context → headers → JWT claims
    tenantIDStr := httpware.GetTenantID(ctx)
    return uuid.Parse(tenantIDStr)
}
```

**Frontend pattern:** Platform owner UIs do NOT send `X-Tenant-ID`/`X-Tenant-Slug` headers. Instead, a centralized `TenantFilter` component lets the platform owner select a tenant, and the selected ID is passed as `?tenantId=` on API calls. When "All Tenants" is selected, no `tenantId` param is sent and the backend returns cross-tenant data for list endpoints.

### Auth-API Seed Logic
The auth-api seed creates the `codevertex` tenant first, then creates Codevertex-owned users (e.g. `admin@codevertex.dev`) with `superuser` membership. All other tenants are then seeded as business clients.

---

## Account Creation & Subscription Enforcement Flow

### Registration Flow (auth-ui multi-step)

```
Step 1: Account Info (name, email, password)
        ↓
Step 2: Organisation
        ├── Join Existing: search by slug → GET /api/v1/tenants/by-slug/{slug} (public)
        │     → user joins with `member` role
        └── Create New: provide name, slug, org_size, use_case
              → POST /api/v1/auth/register with org_action=create_new
              → auth-api creates tenant, assigns user `admin` role (tenant founder)
              → publishes tenant.created event (downstream services sync)
        ↓
Step 3: Subscription Recommendation
        → Fetch plans from GET /api/v1/plans (subscription-api)
        → Display plans with features, limits, 14-day free trial
        → User selects preferred plan (stored as profile.selected_plan)
        ↓
Submit → POST /api/v1/auth/register → redirect to /login
        ↓ After login ↓
If not platform user (primary_tenant ≠ codevertex):
    → Check subscription-api: GET /api/v1/tenants/{id}/subscription
    → If ACTIVE or TRIAL: allow full access
    → If no subscription / EXPIRED: redirect to /subscribe page
        → Show subscription plans, free trial CTA
        → User selects plan → subscription-api provisions trial
```

### Subscription Member Limits
When a tenant's subscription tier has `max_admins = 2`:
- The 3rd user trying to register as `admin` for that org is blocked at registration
- Error returned: `subscription_limit_exceeded` with tier details
- Implementation: `Register()` checks `GET /api/v1/tenants/{id}/subscription` before creating membership *(planned — not yet enforced in code; tracked for next sprint)*

### Login Post-Auth Subscription Check
After successful login, **every frontend** (except auth-ui itself) must:

```
1. Receive access_token from auth-api
2. Check user.is_platform_owner
   → true: skip subscription check, grant full access
3. Call GET /api/v1/tenants/{tenant_id}/subscription (subscription-api)
   → status=ACTIVE or TRIAL: allow access
   → status=EXPIRED or no record: redirect to subscription page
```

---

## Subscription Seed UUID Resolution

> **Critical:** The subscription-api seed must NEVER hardcode tenant UUIDs.
> Auth-api generates UUIDs at runtime (DB-generated). Hardcoded UUIDs will never match.

### Resolution Order
1. **Env var override**: `TENANT_ID_{SLUG_UPPER}` (e.g. `TENANT_ID_URBAN_LOFT=<uuid>`)
2. **Auth-api public endpoint**: `GET /api/v1/tenants/by-slug/{slug}` (no auth required)
3. **Skip with warning**: if auth-api unreachable and no env var, log and continue

### Env Var Override (for CI/offline seeding)
```bash
TENANT_ID_URBAN_LOFT=<uuid-from-auth-api-db>
TENANT_ID_CODEVERTEX=<uuid-from-auth-api-db>
AUTH_API_URL=https://sso.codevertexitsolutions.com  # default
```

### Run Order
Auth-api seed **must run before** subscription-api seed so tenants exist in auth-api DB.

