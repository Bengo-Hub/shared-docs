# Cross-Service Data Ownership & User Management

**Last updated:** March 2026 — JWT + JIT and service-specific onboarding reflected in Authentication & SSO section.

## Overview

This document defines the architecture pattern for data ownership and user management across microservices in the BengoBox platform. Each service owns and manages all data related to its domain, while other services reference data via IDs and tenant mapping.

---

## Core Principles

1. **Single Source of Truth**: Each service owns and manages all data related to its domain
2. **Reference Only**: Other services store only reference IDs, never duplicate data
3. **Tenant Service Availability**: Check tenant subscription plan before creating/referencing data in another service
4. **SSO Authentication**: All users authenticate via auth-service (SSO), service-specific data stored locally
5. **Service Independence**: Services can operate standalone or in combination based on tenant subscription

---

## Data Ownership by Service

### Auth-Service
**Owns**:
- User identity (email, password, phone, status)
- **Tenant definitions and UUIDs** — auth-api is the single source of truth for tenant identity; all services MUST use the same tenant UUID for a given tenant (DB-generated in auth-api seed, never generated per-service)
- Tenant membership and roles
- Sessions and MFA
- OAuth accounts

**Other Services Reference**:
- `auth_service_user_id` (UUID) - Reference to auth-service user
- Tenant ID (UUID) from JWT or from auth-api events — use this UUID when storing tenant_id locally; do not create new UUIDs for the same tenant
- Identity data synced via events: `auth.user.created`, `auth.user.updated`, `auth.user.deactivated`

### Logistics-Service
**Owns**:
- Rider profiles (KYC, documents, vehicle info)
- Fleet members (riders, drivers)
- Delivery tasks
- Shifts and availability
- Telemetry and location data
- Proof of delivery
- Rider earnings and payouts

**Other Services Reference**:
- `rider_id` (UUID) - Reference to logistics-service fleet member
- `logistics_task_id` (UUID) - Reference to delivery task
- All rider queries go to logistics-service APIs: `GET /v1/{tenant}/fleet-members`

### Inventory-Service
**Owns**:
- Inventory items (SKUs, stock levels, locations)
- Warehouses (code, name, address, is_default)
- Inventory balances (on_hand, available, reserved per item per warehouse)
- Reservations (order-linked stock holds with status: pending/confirmed/released/consumed)
- Consumptions (stock deductions with order reference and idempotency)
- Recipes and BOMs
- Stock adjustments and movements
- Low-stock alerts

**Other Services Reference**:
- `inventory_sku` (String) - Reference to inventory item
- `inventory_item_id` (UUID) - Reference to inventory item
- `reservation_id` (UUID) - Reference to stock reservation
- All inventory queries go to inventory-service APIs (8 endpoints implemented Feb 2026)

### POS-Service
**Owns**:
- POS connections and credentials
- POS outlets and locations
- POS orders and tickets
- Settlement data

**Other Services Reference**:
- `pos_connection_id` (UUID) - Reference to POS connection
- `pos_outlet_id` (UUID) - Reference to POS outlet
- `pos_order_id` (String) - Reference to POS order

### Treasury-Service
**Owns**:
- Payment intents and transactions
- Payment methods
- Refunds
- Payouts and settlements
- Invoices

**Other Services Reference**:
- `payment_intent_id` (UUID) - Reference to payment intent
- `payment_id` (UUID) - Reference to payment
- `payout_id` (UUID) - Reference to payout

### Notifications-Service
**Owns**:
- Notification templates
- Message delivery status
- Channel preferences (per user, per tenant)

**Other Services Reference**:
- `notification_template_id` (UUID) - Reference to template
- `notification_message_id` (UUID) - Reference to sent message

### Ordering-Service
**Owns**:
- Cafe-specific user data (preferences, cafe roles, loyalty points)
- Menu items and categories (references inventory SKUs)
- Orders and carts
- Promo codes and redemptions
- Loyalty accounts and transactions

**Other Services Reference**:
- `order_id` (UUID) - Reference to cafe order
- `cafe_id` (UUID) - Reference to cafe outlet

---

## Cross-Service Event Subscription Matrix

| Publisher | Event Subject | Subscriber | Action |
|:---|:---|:---|:---|
| Auth Service | `auth.user.created` | Ordering Service | Create local user reference |
| Auth Service | `auth.user.updated` | Ordering Service | Sync profile changes |
| Auth Service | `auth.user.deactivated` | Ordering Service | Deactivate local user |
| Auth Service | `auth.tenant.created` | Ordering Service | Initialize tenant data |
| Auth Service | `auth.tenant.updated` | Ordering Service | Sync tenant changes |
| Ordering Service | `ordering.order.ready` | Logistics Service | Auto-create delivery task |
| Treasury Service | Payment webhooks (HTTP) | Ordering Service | Update order payment status |
| Logistics Service | Delivery webhooks (HTTP) | Ordering Service | Update order delivery status |

**Note**: Inventory and notifications services use synchronous REST calls from the ordering service, not NATS events.

---

## User Management Patterns

### Pattern 1: Service-Specific User Data

**Example: Rider User Management**

1. **User Identity** (auth-service):
   - User created in auth-service with email, password, tenant membership
   - Role: `rider` assigned in auth-service
   - User authenticates via auth-service (SSO)

2. **Rider Profile** (logistics-service):
   - Rider-specific data stored in logistics-service:
     - KYC documents (national ID, license)
     - Vehicle information
     - Shift availability
     - Earnings and payouts
   - Linked to auth-service user via `auth_service_user_id`

3. **Rider Creation Flow**:

   **From Cafe Service**:
   ```
   1. User initiates rider onboarding in cafe UI
   2. Check tenant has logistics service enabled:
      GET /api/v1/tenants/{tenant_id}/services
      → Verify "logistics" in enabled_services
   3. If not enabled: Show error "Logistics service not available. Upgrade plan."
   4. If enabled, choose one:
      Option A - API Push:
        - POST /api/v1/cafe/riders/onboard (cafe-backend)
        - Cafe-backend pushes to logistics-service:
          POST /v1/{tenant}/fleet-members
        - Logistics-service creates rider in auth-service (if needed)
        - Returns rider_id
        - Cafe stores rider_id reference
      
      Option B - UI Redirect:
        - Redirect to: https://logistics.codevertexitsolutions.com/{tenant_slug}/riders/onboard?return_url={cafe_url}
        - User authenticates with auth-service (SSO)
        - User completes onboarding in logistics-service UI
        - Logistics-service redirects back with rider_id
   ```

   **Standalone Logistics Service**:
   ```
   1. User goes directly to logistics-service UI
   2. User authenticates via auth-service (SSO)
   3. User completes rider onboarding
   4. All rider data stored in logistics-service
   5. No cafe-service involvement
   ```

### Pattern 2: Tenant Service Availability Check

**Before creating/referencing data in another service:**

```go
// Pseudo-code example
func createRider(ctx context.Context, tenantID uuid.UUID, riderData RiderData) error {
    // 1. Check tenant has logistics service enabled
    tenant, err := subscriptionService.GetTenantServices(ctx, tenantID)
    if err != nil {
        return err
    }
    
    if !contains(tenant.EnabledServices, "logistics") {
        return ErrServiceNotAvailable("Logistics service not enabled for this tenant")
    }
    
    // 2. Verify tenant exists in logistics-service
    exists, err := logisticsService.TenantExists(ctx, tenantID)
    if err != nil {
        return err
    }
    if !exists {
        return ErrTenantNotFound("Tenant not found in logistics-service")
    }
    
    // 3. Create rider in logistics-service
    riderID, err := logisticsService.CreateFleetMember(ctx, tenantID, riderData)
    if err != nil {
        return err
    }
    
    // 4. Store only reference ID locally
    return cafeRepo.StoreRiderReference(ctx, tenantID, riderID)
}
```

### Pattern 3: Service-to-Service Data Queries

**Never duplicate data, always query the owning service:**

```go
// ❌ WRONG: Storing rider data locally
type OrderAssignment struct {
    RiderID      uuid.UUID
    RiderName    string  // ❌ Don't store
    RiderPhone   string  // ❌ Don't store
    VehicleType  string  // ❌ Don't store
}

// ✅ CORRECT: Store only reference, query when needed
type OrderAssignment struct {
    RiderID      uuid.UUID  // ✅ Only reference
}

// Query rider data from logistics-service when needed
func getRiderDetails(ctx context.Context, riderID uuid.UUID) (*Rider, error) {
    return logisticsService.GetFleetMember(ctx, tenantID, riderID)
}
```

---

## Subscription Plan Integration

### Service Availability Check

**Subscription Plans** define which services are available:
- Starter Plan: cafe-service only
- Growth Plan: cafe-service + logistics-service
- Professional Plan: All services (cafe, logistics, inventory, POS, treasury, notifications)

**Before creating/referencing data in another service:**
1. Check tenant subscription plan: `GET /api/v1/tenants/{tenant_id}/subscription`
2. Verify service in plan features: `plan.features.includes("logistics")`
3. If not available: Show error or redirect to upgrade

---

## Authentication & SSO

### Single Sign-On (SSO)

- All users authenticate via **auth-service** (`https://sso.codevertexitsolutions.com/`)
- JWT access tokens contain: `sub` (user_id), `tenant_id`, `tenant_slug`, `roles`, and `permissions` (canonical codes from auth-service role–permission table). All services use these same permission codes for authorization.
- All services validate tokens via JWKS from auth-service and read roles/permissions from the token (or from GET /me). If the token is valid but the service has no local user yet, the service **JIT-provisions** the user from token claims and continues (no 401 for "user not found").
- Service-specific profile data (e.g. rider KYC, vehicle) is **not** in the token. It is collected via **service-specific onboarding** after SSO login, with identity (email, name) prefilled from the token.

### Service-Specific Roles

- **Auth-Service**: Global roles (`superuser`, `admin`, `user`)
- **Cafe-Service**: Cafe-specific roles (`customer`, `staff`, `admin`)
- **Logistics-Service**: Logistics-specific roles (`rider`, `fleet_manager`)
- **Combined**: User can have multiple roles across services

---

## Examples

### Example 1: Creating a Rider from Ordering Service

**Scenario**: Tenant has cafe-service and logistics-service enabled

1. User clicks "Become a Rider" in cafe UI
2. Cafe-frontend checks tenant services: `GET /api/v1/tenants/{tenant_id}/services`
3. If logistics enabled:
   - Option A: Submit form to cafe-backend → pushes to logistics-service API
   - Option B: Redirect to logistics-service UI for self-onboarding
4. Logistics-service creates rider user in auth-service (if not exists)
5. Logistics-service stores rider profile locally
6. Returns `rider_id` to cafe service
7. Cafe service stores `rider_id` reference

### Example 2: Standalone Logistics Service

**Scenario**: Tenant only has logistics-service (no cafe-service)

1. User goes to logistics-service UI
2. User authenticates via auth-service (SSO)
3. User completes rider onboarding
4. All rider data stored in logistics-service
5. No cafe-service involvement needed

### Example 3: Order Assignment with Rider

**Scenario**: Assign rider to order

1. Cafe service queries available riders: `GET /v1/{tenant}/fleet-members?status=available`
2. Logistics-service returns rider list (all data from logistics-service)
3. Cafe service selects rider and stores `rider_id` in `order_assignments` table
4. Cafe service creates delivery task: `POST /v1/{tenant}/tasks` with `order_id` and `rider_id`
5. Logistics-service manages task lifecycle (assignment, acceptance, completion)
6. Cafe service consumes events: `logistics.task.assigned`, `logistics.task.completed`

---

## Event Subscription Matrix (Added February 2026)

Shows which services publish events and which services consume them:

| Publisher | Event | Subscribers |
|:---|:---|:---|
| auth-service | `user.created` | subscription-service (trial provision), notifications-service (welcome email) |
| auth-service | `tenant.created` | subscription-service (trial provisioning), notifications-service (onboarding email) |
| auth-service | `user.password_changed` | notifications-service (security alert) |
| subscription-service | `subscription.activated` | auth-service (JWT refresh with product claims) |
| subscription-service | `subscription.upgraded` | auth-service (JWT refresh), notifications-service (upgrade confirmation) |
| subscription-service | `subscription.cancelled` | auth-service (JWT refresh), notifications-service (cancellation notice) |
| ordering-service | `order.created` | logistics-service (task creation), notifications-service (order confirmation), treasury-service (payment intent) |
| ordering-service | `order.confirmed` | notifications-service (customer notification) |
| logistics-service | `task.completed` | ordering-service (order status update), notifications-service (delivery confirmation) |
| logistics-service | `task.assigned` | notifications-service (rider assignment notification) |
| treasury-service | `payment.completed` | ordering-service (order confirmation), notifications-service (receipt) |

---

## Best Practices

1. **Always Check Service Availability**: Before creating/referencing data, verify tenant has service enabled
2. **Store Only References**: Never duplicate data, always store reference IDs
3. **Query When Needed**: Query owning service for data when needed, don't cache long-term
4. **Use Events for Sync**: Subscribe to events from owning service for real-time updates
5. **Handle Service Unavailability**: Gracefully handle cases where service is not available
6. **Support Standalone Mode**: Services should work independently if tenant only has that service

---

## Migration Notes

- Legacy `riderprofile` and `riderdocument` schemas in cafe-backend are **deprecated** and **unused**
- All rider data migration should go to logistics-service
- Cafe-backend should only store `rider_id` references going forward

---

## References

- [Auth-Service Integration](integrations.md#auth-service)
- [Logistics-Service Integration](integrations.md#logistics-service)
- [Entity Relationship Diagram](erd.md)

