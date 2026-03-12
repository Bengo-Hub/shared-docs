# BengoBox Architecture Recommendations

**Document Version**: 1.0
**Last Updated**: January 2026
**Status**: Active Implementation

---

## Executive Summary

This document provides architecture recommendations for the BengoBox microservices ecosystem based on comprehensive analysis of all 11 Go services, their integration patterns, and cross-cutting concerns.

### Key Recommendations

1. **Dual Authentication**: All services MUST support both JWT and API Key authentication
2. **Keep subscription-service separate**: Current 3-service boundary is optimal
3. **Trinity Authorization Pattern**: 3-layer model (RBAC + Licensing + Resources)
4. **JWT Claims Enrichment**: Embed subscription data at login to eliminate per-request lookups
5. **Standardize on shared libraries**: Consistent patterns across all services

---

## 1. Authentication Architecture

### 1.1 Dual Authentication Mandate

Every microservice in BengoBox MUST support both authentication methods:

| Auth Method | Use Case | Header | Validation |
|-------------|----------|--------|------------|
| JWT Bearer | User sessions, frontend apps | `Authorization: Bearer <token>` | JWKS/RS256 |
| API Key | Service-to-service, webhooks, automation | `X-API-Key: <key>` | auth-service lookup |

#### Implementation Pattern

```go
import authclient "github.com/Bengo-Hub/shared-auth-client"

func main() {
    // 1. Create JWT validator
    jwtValidator, err := authclient.NewValidator(authclient.Config{
        JWKSUrl:  os.Getenv("AUTH_SERVICE_URL") + "/.well-known/jwks.json",
        Issuer:   os.Getenv("AUTH_SERVICE_URL"),
        Audience: "your-service",
    })

    // 2. Create API key validator
    apiKeyValidator := authclient.NewAPIKeyValidator(
        os.Getenv("AUTH_SERVICE_URL"),
        nil, // uses default HTTP client
    )

    // 3. Create dual-auth middleware
    authMiddleware := authclient.NewAuthMiddlewareWithAPIKey(
        jwtValidator,
        apiKeyValidator,
    )

    // 4. Apply to routes
    r.Use(authMiddleware.RequireAuth)
}
```

### 1.2 Service-to-Service Authentication

**Recommended**: Direct API Key usage (simpler, auth-service caching handles performance)

```go
// In service configuration
type Config struct {
    // API keys for calling other services
    InventoryServiceAPIKey string `envconfig:"INVENTORY_SERVICE_API_KEY"`
    TreasuryServiceAPIKey  string `envconfig:"TREASURY_SERVICE_API_KEY"`
    AuthServiceAPIKey      string `envconfig:"AUTH_SERVICE_API_KEY"`
}

// In service client
func (c *InventoryClient) GetStock(ctx context.Context, itemID string) (*Stock, error) {
    req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
    req.Header.Set("X-API-Key", c.apiKey)
    // ...
}
```

---

## 2. Authorization Architecture

### 2.1 Trinity Authorization Pattern

BengoBox uses a 3-layer authorization model ensuring complete access control:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TRINITY AUTHORIZATION MODEL                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐    │
│   │  LAYER 1: RBAC (auth-service)                               │    │
│   │  ──────────────────────────────────────────────────────────  │    │
│   │  Question: WHO can perform WHAT actions?                    │    │
│   │                                                             │    │
│   │  • Global roles: superuser, admin, manager, operator        │    │
│   │  • Scopes: read:orders, write:inventory, admin:users        │    │
│   │  • Stored in JWT claims                                     │    │
│   └─────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│                              ▼                                       │
│   ┌─────────────────────────────────────────────────────────────┐    │
│   │  LAYER 2: LICENSING (subscription-service)                  │    │
│   │  ──────────────────────────────────────────────────────────  │    │
│   │  Question: WHICH features are enabled for this tenant?      │    │
│   │                                                             │    │
│   │  • Plans: STARTER (KES 2,500), GROWTH (KES 6,000),         │    │
│   │           PROFESSIONAL (KES 12,500)                         │    │
│   │  • Features: multi_warehouse, api_access, advanced_reports  │    │
│   │  • Limits: max_orders_per_month, max_outlets, max_users     │    │
│   │  • Embedded in JWT at login for zero-latency checks         │    │
│   └─────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│                              ▼                                       │
│   ┌─────────────────────────────────────────────────────────────┐    │
│   │  LAYER 3: RESOURCE OWNERSHIP (domain services)              │    │
│   │  ──────────────────────────────────────────────────────────  │    │
│   │  Question: Does this user OWN/CAN ACCESS this resource?     │    │
│   │                                                             │    │
│   │  • Tenant isolation: All queries filtered by tenant_id      │    │
│   │  • Service-specific roles: POS cashier, kitchen manager     │    │
│   │  • Resource ownership: order.user_id == claims.subject      │    │
│   └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Authorization Check Flow

```go
func authorizeOrderAccess(ctx context.Context, orderID string) error {
    claims, _ := authclient.ClaimsFromContext(ctx)

    // Layer 1: RBAC - Does user have required role/scope?
    if !claims.HasScope("read:orders") && !claims.IsAdmin() {
        return ErrForbidden
    }

    // Layer 2: Licensing - Is feature enabled for tenant?
    if !claims.HasFeature("ordering_module") {
        return ErrFeatureNotEnabled
    }

    // Layer 3: Resource ownership - Does user have access to this order?
    order, err := repo.GetOrder(ctx, orderID)
    if err != nil {
        return err
    }
    if order.TenantID != claims.TenantID {
        return ErrForbidden // Tenant isolation
    }
    if order.UserID != claims.Subject && !claims.HasRole("manager") {
        return ErrForbidden // Resource ownership
    }

    return nil // Access granted
}
```

---

## 3. Subscription Architecture

### 3.1 Architecture Decision: Keep subscription-service Separate

After thorough analysis, the recommendation is to **KEEP subscription-service as a standalone microservice**. Consolidation would violate domain boundaries.

**Rationale**:
- **Clear domain boundary**: Subscription management is a distinct business domain
- **Already fully implemented**: 4 Ent schemas, HTTP API, NATS integration
- **Single Responsibility**: Manages plans, features, limits, entitlements
- **Decoupled billing**: treasury-api handles payment processing

**Current 3-Service Architecture (Optimal)**:

```
┌─────────────────────────────────────────────────────────────────┐
│                   SUBSCRIPTION ECOSYSTEM                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  subscription-service          auth-service          treasury-api │
│  ──────────────────           ────────────           ──────────── │
│  • Plan definitions           • User identity        • Billing     │
│  • Feature entitlements       • Tenant registry      • Invoices    │
│  • Usage limits               • JWT issuance         • Payments    │
│  • Plan history               • Session mgmt         • Refunds     │
│                                                                  │
│      ─────────── Subscription Events ───────────►                │
│      ◄─────────── Billing Events ────────────────               │
│                                                                  │
│  Data Flow:                                                      │
│  1. subscription-service → NATS → auth-service (feature sync)    │
│  2. subscription-service → NATS → treasury-api (billing events)  │
│  3. treasury-api → NATS → subscription-service (payment status)  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 JWT Claims Enrichment

To eliminate per-request subscription-service lookups, embed subscription data in JWT at login:

**auth-service Login Flow**:

```go
func (h *LoginHandler) Handle(ctx context.Context, req LoginRequest) (*AuthResponse, error) {
    // 1. Authenticate user
    user, err := h.userRepo.Authenticate(ctx, req.Email, req.Password)
    if err != nil {
        return nil, err
    }

    // 2. Fetch subscription data (cached from subscription-service events)
    subscription, err := h.subscriptionCache.GetByTenantID(ctx, user.TenantID)
    if err != nil {
        // Fallback: free tier if subscription lookup fails
        subscription = &Subscription{Plan: "FREE", Status: "ACTIVE"}
    }

    // 3. Build JWT claims with embedded subscription
    claims := &Claims{
        Subject:              user.ID,
        TenantID:             user.TenantID,
        Email:                user.Email,
        Roles:                user.Roles,
        SubscriptionPlan:     subscription.PlanCode,
        SubscriptionFeatures: subscription.FeatureCodes,
        SubscriptionLimits:   subscription.Limits,
        SubscriptionStatus:   subscription.Status,
        SubscriptionExpires:  subscription.CurrentPeriodEnd,
    }

    // 4. Issue JWT
    token, err := h.tokenService.Issue(claims)
    return &AuthResponse{AccessToken: token}, nil
}
```

### 3.3 Feature Gate Checking

```go
// In any service handler
func (h *WarehouseHandler) CreateWarehouse(w http.ResponseWriter, r *http.Request) {
    claims, _ := authclient.ClaimsFromContext(r.Context())

    // Check subscription feature
    if !claims.HasFeature("multi_warehouse") {
        http.Error(w, "Multi-warehouse feature not included in your plan", http.StatusForbidden)
        return
    }

    // Check usage limit
    currentCount, _ := h.warehouseRepo.CountByTenant(r.Context(), claims.TenantID)
    maxWarehouses := claims.GetLimit("max_warehouses")
    if maxWarehouses > 0 && currentCount >= maxWarehouses {
        http.Error(w, "Warehouse limit reached for your plan", http.StatusForbidden)
        return
    }

    // Proceed with creation
    // ...
}
```

---

## 4. Entity Ownership Matrix

Each microservice owns specific entities and references others. No data duplication.

| Service | Owns | References |
|---------|------|------------|
| **auth-service** | Users, Tenants, Sessions, MFA, OAuth Clients, API Keys | - |
| **subscription-service** | Plans, Features, Entitlements, Usage Metrics | auth-service (tenant_id) |
| **treasury-api** | Invoices, Payments, Refunds, Wallets, GL Entries | auth (user_id), subscription (plan) |
| **inventory-service** | Items, Variants, Warehouses, Balances, POs, BOMs | auth (tenant_id, user_id) |
| **pos-service** | POS Orders, Devices, Cash Drawers, Sessions, Tables | auth, inventory (items) |
| **ordering-service** | Carts, Orders, Addresses, Loyalty | auth, inventory (items), treasury |
| **logistics-service** | Tasks, Zones, Drivers, Fleet, Routes | auth, ordering (orders), inventory |
| **notifications-service** | Templates, Channels, Delivery Logs, Preferences | auth (user_id, tenant_id) |
| **projects-service** | Projects, Tasks, Milestones, Time Entries | auth (user_id) |
| **ticketing-service** | Tickets, Events, Venues, Attendees | auth, treasury |
| **iot-service** | Devices, Sensors, Telemetry, Alerts, Geofences | auth (tenant_id), logistics |

---

## 5. Shared Libraries

### 5.1 Current Libraries

| Library | Version | Purpose | GitHub |
|---------|---------|---------|--------|
| `httpware` | v0.1.1 | HTTP middleware (RequestID, Logging, Recover, CORS) | Bengo-Hub/httpware |
| `shared-auth-client` | v0.1.2 | JWT/API Key validation, Claims, Middleware | Bengo-Hub/auth-client |
| `shared-service-client` | v0.1.0 | Circuit breaker, retry, tracing | Bengo-Hub/service-client |
| `shared-events` | v0.1.0 | Transactional outbox pattern | Bengo-Hub/events |
| `shared-password-hasher` | v0.1.0 | Argon2id password hashing | Bengo-Hub/password-hasher |

### 5.2 Planned Libraries

| Library | Purpose | Target |
|---------|---------|--------|
| `shared-config` | Standardized configuration loading | Q2 2026 |
| `shared-observability` | Logger, metrics, tracing initialization | Q2 2026 |
| `shared-errors` | Standardized error response format | Q2 2026 |

### 5.3 Library Usage Pattern

```go
// go.mod
require (
    github.com/Bengo-Hub/httpware v0.1.1
    github.com/Bengo-Hub/shared-auth-client v0.1.2
    github.com/Bengo-Hub/shared-service-client v0.1.0
    github.com/Bengo-Hub/shared-events v0.1.0
)

// In router setup
import (
    httpware "github.com/Bengo-Hub/httpware"
    authclient "github.com/Bengo-Hub/shared-auth-client"
)

func NewRouter(log *zap.Logger, authMiddleware *authclient.AuthMiddleware) http.Handler {
    r := chi.NewRouter()

    // Apply shared middleware
    r.Use(httpware.RequestID)
    r.Use(httpware.Logging(log))
    r.Use(httpware.Recover(log))

    // Apply auth middleware
    r.Use(authMiddleware.RequireAuth)

    return r
}
```

---

## 6. Migration Checklist

### 6.1 Per-Service Migration

For each Go microservice, complete the following:

```markdown
### [Service Name] Migration Checklist

#### Shared Libraries
- [ ] Add `github.com/Bengo-Hub/httpware` v0.1.1
- [ ] Replace local middleware with httpware
- [ ] Add `github.com/Bengo-Hub/shared-auth-client` (or verify existing)
- [ ] Implement dual auth (JWT + API Key)
- [ ] Add `github.com/Bengo-Hub/shared-service-client`
- [ ] Replace direct HTTP calls with resilient client
- [ ] Add `github.com/Bengo-Hub/shared-events`
- [ ] Implement outbox pattern for domain events

#### Authentication
- [ ] Verify JWT validation with JWKS
- [ ] Implement API Key validation fallback
- [ ] Add subscription claims checking
- [ ] Implement feature gating where applicable

#### Testing
- [ ] Unit tests for auth middleware
- [ ] Integration tests for protected endpoints
- [ ] Contract tests with auth-service
```

### 6.2 Priority Order

1. **High Priority (Q1 2026)**:
   - inventory-service
   - pos-service
   - ordering-service

2. **Medium Priority (Q2 2026)**:
   - auth-service (outbox pattern)
   - ticketing-service
   - iot-service

3. **Low Priority (Q3 2026)**:
   - Complete remaining gaps

---

## 7. Security Best Practices

### 7.1 JWT Security

- RS256 signing algorithm (asymmetric)
- 15-minute access token expiry
- 7-day refresh token expiry
- JWKS rotation every 90 days
- Audience validation per service

### 7.2 API Key Security

- SHA-256 hashed storage
- Scoped permissions per key
- Service account identification
- Automatic rotation support
- Audit logging for all validations

### 7.3 Multi-Tenant Isolation

```go
// ALWAYS filter by tenant_id in queries
func (r *OrderRepo) GetOrders(ctx context.Context, tenantID string) ([]*Order, error) {
    return r.client.Order.Query().
        Where(order.TenantID(tenantID)). // MANDATORY
        All(ctx)
}
```

---

## 8. Observability Standards

### 8.1 Logging

All services MUST use structured logging with:
- Request ID propagation (`X-Request-ID`)
- Tenant ID context
- User ID (if authenticated)
- Service name
- Operation name

```go
logger.Info("order created",
    zap.String("request_id", requestID),
    zap.String("tenant_id", tenantID),
    zap.String("user_id", userID),
    zap.String("order_id", orderID),
)
```

### 8.2 Metrics

Standard Prometheus metrics per service:
- `http_requests_total{method, path, status}`
- `http_request_duration_seconds{method, path}`
- `service_errors_total{type}`

### 8.3 Tracing

OpenTelemetry context propagation via `shared-service-client`.

---

## 9. Critical Gaps & Action Items (January 2026 Audit)

### 9.1 CORS Security Misconfiguration (HIGH PRIORITY)

**Issue**: All services set `AllowCredentials: true` with wildcard `["*"]` origins, which browsers reject.

**Affected Services**: logistics, subscriptions, notifications, finance, ordering, pos, inventory

**Fix Required**:
```go
// INCORRECT - Will be rejected by browsers
cors.Options{
    AllowedOrigins:   []string{"*"},
    AllowCredentials: true, // This combination is invalid
}

// CORRECT - Use specific origins with credentials
cors.Options{
    AllowedOrigins: []string{
        "https://accounts.codevertexitsolutions.com",
        "https://orderapp.codevertexitsolutions.com",
        "https://pos.codevertexitsolutions.com",
        // Add all frontend origins
    },
    AllowCredentials: true,
}
```

**Action Item**: Update CORS configuration in each service's `router.go` to use explicit allowed origins.

### 9.2 Outbox Pattern Background Publisher (CRITICAL)

**Issue**: Transactional outbox schema exists but background publisher worker NOT IMPLEMENTED in ordering-service.

**Risk**: Events may be lost if service crashes between DB commit and NATS publish.

**Files to Update**:
- `ordering-service/ordering-backend/internal/modules/outbox/worker.go` (create)
- `ordering-service/ordering-backend/internal/app/app.go` (wire worker)

**Implementation**:
```go
// internal/modules/outbox/worker.go
func (w *OutboxWorker) Run(ctx context.Context) {
    ticker := time.NewTicker(w.pollInterval)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            return
        case <-ticker.C:
            events, _ := w.repo.GetPendingEvents(ctx, w.batchSize)
            for _, event := range events {
                if err := w.nats.Publish(event.Subject(), event.Payload); err != nil {
                    w.repo.MarkAsFailed(ctx, event.ID, err.Error())
                    continue
                }
                w.repo.MarkAsPublished(ctx, event.ID)
            }
        }
    }
}
```

### 9.3 Event Publishing Migration (MEDIUM)

**Issue**: Only ordering-service uses shared events library. Other services have ad-hoc implementations.

**Services Requiring Migration**:
- logistics-service
- subscriptions-service
- notifications-api
- treasury-api
- pos-service
- inventory-service

**Action Item**: Add `github.com/Bengo-Hub/shared-events` dependency and migrate to outbox pattern.

### 9.4 Tenant Extraction Inconsistency (MEDIUM)

**Issue**: ordering-backend uses custom `security.TenantValidation()` while others use `httpware.Tenant`.

**Recommendation**: Standardize on `httpware.Tenant` or add tenant validation to httpware library.

### 9.5 API Key Revocation Delay (MEDIUM)

**Issue**: 5-minute cache on API keys means compromised keys take time to revoke.

**Recommendation**:
- Add cache invalidation endpoint to auth-service
- Reduce cache TTL to 2 minutes for critical services
- Implement webhook notification on key revocation

### 9.6 Subscription Data Staleness (LOW-MEDIUM)

**Issue**: Subscription features embedded in JWT not refreshed mid-session.

**Impact**: User subscription downgrade may not be reflected until token refresh.

**Recommendation**:
- Shorter access token TTL (5 minutes) for subscription-dependent features
- Or implement real-time subscription status check for critical operations

### 9.7 Missing Scope/Role Registry

**Issue**: No central documentation of valid scopes and roles across services.

**Action Item**: Create `docs/RBAC-REGISTRY.md` documenting:
- Global roles and their permissions
- Service-specific roles
- All valid scope strings
- Permission inheritance rules

---

## 10. Shared Library Improvements Checklist

### httpware (v0.1.2 - Planned)
- [ ] Add optional OpenTelemetry tracing support
- [ ] Add configurable rate limiting middleware
- [ ] Standardize CORS configuration with env-based allowed origins
- [ ] Add UserID context helper widely adopted pattern

### shared-auth-client (v0.2.1 - Planned)
- [ ] Add `GetUserID()` helper to Claims (currently requires parsing Subject)
- [ ] Add API key cache invalidation endpoint support
- [ ] Standardize error response format across middleware
- [ ] Document scope/role naming conventions

### shared-events (v0.1.1 - Planned)
- [ ] Add dead-letter queue handling
- [ ] Add event schema versioning migration strategy
- [ ] Add subscriber/handler pattern (currently only publisher)
- [ ] Add typed event classes per aggregate type

---

## Event Publishing Standards (Added February 2026)

### Outbox Pattern Requirements

All Go services MUST use the transactional outbox pattern for event publishing:
- Write domain entity + outbox event in the same DB transaction
- Use `shared-events` library for publisher implementation
- Subject naming: `{service}.events` (e.g., `auth.events`, `subscriptions.events`)

### NATS Subject Naming Convention

| Publisher | Subject | Events |
|:---|:---|:---|
| auth-service | `auth.events` | `user.created`, `user.updated`, `user.deleted`, `tenant.created`, `tenant.updated`, `tenant.deleted`, `user.password_changed`, `user.2fa_enabled`, `user.session_created` |
| subscription-service | `subscriptions.events` | `subscription.created`, `subscription.activated`, `subscription.cancelled`, `subscription.expired`, `subscription.upgraded`, `subscription.downgraded` |
| ordering-service | `ordering.events` | `order.created`, `order.confirmed`, `order.completed`, `order.cancelled` |
| logistics-service | `logistics.events` | `task.created`, `task.assigned`, `task.completed`, `task.cancelled` |
| notifications-service | `notifications.events` | (consumer only — email/sms/push delivery) |

### Multi-Service Subscription Model

The subscription-service manages:
- **8 Products**: ordering, logistics, treasury, pos, analytics, notifications, auth, inventory
- **3 Bundles**: Starter (ordering+auth), Professional (+logistics+treasury+notifications), Enterprise (all)
- **6 Plans**: Monthly/Yearly per bundle tier
- **Feature gating**: Products embedded in JWT claims for zero-latency feature checks at the frontend

---

## 11. Conclusion

This document establishes the architectural patterns for BengoBox microservices. Key takeaways:

1. **Dual auth is mandatory** - All services must support JWT + API Key
2. **Subscription-service stays separate** - Domain boundaries are correct
3. **Trinity authorization** - 3-layer model for complete access control
4. **Shared libraries** - Use existing libraries, contribute improvements
5. **Zero-latency feature checks** - Embed subscription in JWT claims

### Critical Actions (January 2026)
1. **Fix CORS configuration** in all services
2. **Implement outbox background publisher** in ordering-service
3. **Migrate event publishing** to shared library across all services
4. **Create RBAC registry** documentation

For questions or updates, contact the platform team.
