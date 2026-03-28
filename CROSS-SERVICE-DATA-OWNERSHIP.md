# Cross-Service Data Ownership & User Management

**Last updated:** March 2026 — Multi-industry revamp (March 25): inventory-api gains hierarchical categories with icon field, compliance fields, custom fields, lot tracking, bundles, suppliers, purchase orders, stock transfers, warranties. pos-api gains KDS, appointments, staff/commission, serial tracking; POS catalog sync handler enriched with full compliance/physical/service fields from inventory events (inventory_item_id FK, item_type, requires_age_verification, barcode, duration_minutes). Use case is per-outlet (not per-tenant) — a single tenant can have outlets with different use cases. logistics-api gains dynamic pricing rules, rider shifts. treasury-api gains split payments, settlements, reconciliation, installments. Tenant schema reduced across all 7 downstream services (March 24). Services store only minimal tenant reference (id, slug, name, status, use_case, sync_status, last_sync_at). Branding, contact info, and subscription data fetched from auth-api Redis cache (cache v0.2.0) with JWT TTL. No data duplication; each service stores only its own data; references via REST, events, or gRPC.

## Overview

This document is the **canonical** definition of data ownership across BengoBox microservices. It ensures **no data duplication**: each service stores only the data it owns; any need for another service’s data is satisfied by **reference IDs** and access via **REST**, **events (NATS)**, or **gRPC** — never by copying entities into another service’s database.

---

## Expected Architecture: No Data Duplication

- **Single store per entity:** Each entity (e.g. Product Master, orders, riders, payments) has exactly one owning service. That service is the only place that creates, updates, and stores that data.
- **Reference only elsewhere:** Other services store only **references** (e.g. `inventory_item_id`, `rider_id`, `payment_id`) and optionally minimal **snapshots** for audit (e.g. amount at time of payment). They do **not** store a full copy of the entity.
- **Access via integration:** To read or act on another service’s data, a service calls that service’s **REST** or **gRPC** APIs, or reacts to **NATS events** it publishes. Catalog/projection caches (e.g. POS Sales Catalog, ordering catalog cache) are **synced from the owner** (inventory-api), not authored locally. Core inventory master data (Items, Categories, Warehouses) is accessible via **public GET endpoints** to facilitate auto-discovery and synchronization.
- **Auth is always available:** Tenant and user identity come from auth-api; all services use the same tenant UUID from auth. Other services may require a subscription check before use (subscriptions-api).

---

## Core Principles

1. **Single Source of Truth**: Each service owns and manages all data related to its domain; no other service duplicates that data.
2. **Reference Only**: Other services store only reference IDs (and optional audit snapshots), never full copies of entities they do not own.
3. **Access via REST / events / gRPC**: To use another service’s data, call its API or consume its events; do not replicate tables.
4. **Tenant Service Availability**: Check tenant subscription (subscriptions-api) before creating or referencing data in a dependent service (except auth-api, which is always available).
5. **SSO Authentication**: All users authenticate via auth-service (SSO); service-specific data (e.g. rider profile, loyalty) is stored only in the owning service.
6. **Service Independence**: Services can operate standalone or in combination based on tenant subscription.
1.  **Single Source of Truth**: Each service owns and manages all data related to its domain; no other service duplicates that data.
2.  **Reference Only**: Other services store only reference IDs (and optional audit snapshots), never full copies of entities they do not own.
3.  **Access via REST / events / gRPC**: To use another service’s data, call its API or consume its events; do not replicate tables.
4.  **Tenant Service Availability**: Check tenant subscription (subscriptions-api) before creating or referencing data in a dependent service (except auth-api, which is always available).
5.  **SSO Authentication**: All users authenticate via auth-service (SSO); service-specific data (e.g. rider profile, loyalty) is stored only in the owning service.
6.  **Service Independence**: Services can operate standalone or in combination based on tenant subscription.

---

## Canonical Data Ownership Matrix

| Domain | Owner Service | Data/Entities | Integration Pattern |
|-------|---------------|---------------|---------------------|
| **Identity** | `auth-api` | Users, Tenants, **Outlets**, Roles | SSO (JWT), `user_id`/`outlet_id` refs. Auto-provisions downstream (Inventory Warehouses, Ordering Outlets) via NATS events. |
| **Product Master** | `inventory-api` | Items (SKUs), BOM, Recipes, **Units**, **Categories** (hierarchical), **Variants**, **CustomFieldDefinition/Value**, **InventoryLot**, **VariantAttribute**, **Bundle/BundleComponent**, **Supplier**, **PurchaseOrder/Line**, **StockTransfer/Line**, **Warranty** | REST (GET), `sku`/`product_id` refs |
| **Sales Catalog** | `pos-api` | Catalogs, Modifier Groups, Local Prices, **KDSStation/KDSTicket**, **Appointment**, **StaffMember**, **SerialNumberLog**, **CommissionRecord** | Sync from Inventory, NATS `CatalogUpdated` |
| **Orders (Online)** | `ordering-backend` | Carts, Online Orders, Loyalty, **Catalog Projection**, Booking/Appointment refs | Projection of Global Catalog, NATS Events |
| **Logistics** | `logistics-api` | Riders, Tasks, Proof of Delivery, **PricingRule**, **RiderShift** | REST, Webhooks, `rider_id` refs |
| **Payments** | `treasury-api` | Intents, Transactions, Refunds, Taxes, **PaymentSplit**, **Settlement/SettlementLine**, **ReconciliationRun**, **InstallmentPlan/Installment** | REST, Webhooks, `payment_intent_id` refs |
| **Subscription plans, tenant entitlements** | subscriptions-api | All services: check plan before using inventory, POS, logistics, treasury, etc. |
| **Notification templates, delivery status, channel preferences** | notifications-api | Other services: trigger via events or API; store only `notification_message_id` etc. if needed |
| **IoT devices, telemetry, alerts** | iot-service-api | inventory-api (e.g. temperature/compliance), notifications; optional POS/inventory hardware integration |

---

## Item Lifecycle & "Use Case" Flexibility

To support a wide range of business models (Hospitality, Retail, Warehouse), the system employs a tiered data model:

### 1. Master Product (`inventory-api`)
- **Authority**: Owns the physical definition (Name, SKU, Base UoM, Recipe/BOM).
- **Flexibility**: Stores the `use_case` (Retail vs Hospitality) at the Outlet level.

### 2. Sales Catalog (`pos-api`)
- **Authority**: Owns the **Menu/Catalog**. Defines how Master Products are sold at a specific **Outlet**.
- **Data**: Modifiers, POS-specific Categories, Button positions, Outlet Prices.
- **Integration**: Publishes `pos.menu.updated` when the sales interface changes.

### 3. Fulfillment Projection (`ordering-backend`)
- **Authority**: Owns the **Online Storefront** presentation.
- **Data**: Read-only projection of the POS Menu, augmented with online-only flags (e.g., `featured_on_web`).
- **Integration**: Zero-authority for master data; hydrates local cache via NATS events.

## Generalization: `cafe_id` vs `outlet_id`
All services must use the generic `outlet_id` to refer to physical/logical locations. A "Cafe" is simply an outlet with a `Hospitality` use case. This allows the same services to manage "Warehouses" (Stock use case) or "Electronics Stores" (Retail use case).

## Data Ownership by Service

### Auth-Service (auth-api)
**Owns** (only store here; no duplication elsewhere):
- User identity (email, password, phone, status, full_name, avatar)
- **Tenant definitions, UUIDs, and branding** — single source of truth for tenant identity, logo, brand colors, contact info, use case, subscription cache
- Tenant membership and roles
- Sessions and MFA
- OAuth client registry and consent

**Other services reference** (no copy of user/tenant data):
- `tenant_id` (UUID) from JWT or auth-api events
- `auth_service_user_id` / `user_id` (UUID)
- Identity updates via events: `auth.user.created`, `auth.user.updated`, `auth.user.deactivated`, `auth.tenant.*`

**Tenant data access pattern (March 2026):**
- Downstream services store only: `id`, `slug`, `name`, `status`, `use_case`, `sync_status`, `last_sync_at`
- All branding (logo, colors, contact info) is fetched from auth-api `GET /api/v1/tenants/by-slug/{slug}` and cached in Redis with key `tenant:{slug}` and JWT-aligned TTL (6 hours default) via `cache.GetTenantDetails()`
- Frontend services use TanStack Query with staleTime = JWT TTL to cache tenant branding
- **No service stores branding locally** — no `brand_colors`, `logo_url`, `contact_email`, `contact_phone`, `website`, `country`, `timezone`, `org_size`, `subscription_plan/status/expires_at/id`, `tier_limits`, `metadata` in downstream tenant tables
- Subscription enforcement reads from JWT claims (`SubscriptionPlan`, `SubscriptionStatus`, `SubscriptionLimits`), not from tenant DB
- **Branding editing**: Only auth-ui (`accounts.codevertexitsolutions.com/dashboard/settings?tab=branding`). All other frontends redirect to auth-ui for branding management
- **Profile editing**: Common fields (name, email, avatar) managed at auth-ui. Role-specific fields (rider KYC, customer preferences) managed by owning service

---

### Inventory-Service (inventory-api)
**Owns** (single source of truth for product master and stock):
- **Units of measure (UoM)** — core shared, no tenant_id; one global unit list
- **Items (SKU master)** — tenant-scoped; now includes barcode, barcode_type, compliance flags (age_verification, controlled_substance, perishable, serial_numbers, lots), weight_kg, dimensions_cm, duration_minutes
- **ItemVariants** — attributes map, barcode, image_url, cost_price, weight_kg
- **Product categories** (ItemCategory) — tenant-scoped; now hierarchical with parent_id, depth, path, slug, icon, sort_order
- **Recipes and BOM** (recipe_ingredients) — tenant-scoped; Recipe now includes total_cost, cost_per_portion, target_margin_percent, suggested_price
- Warehouses, inventory_balances (now with reorder_quantity, preferred_supplier_id, auto_reorder_enabled), reservations, consumptions
- Stock adjustments, low-stock state
- **CustomFieldDefinition / CustomFieldValue** — structured metadata per item/category (NEW)
- **InventoryLot** — batch/lot tracking with expiry dates (NEW)
- **VariantAttribute** — structured variant matrix definitions (NEW)
- **Bundle / BundleComponent** — pre-packaged kits (NEW)
- **Supplier** — vendor management (NEW)
- **PurchaseOrder / PurchaseOrderLine** — procurement workflow (NEW)
- **StockTransfer / StockTransferLine** — inter-warehouse transfers (NEW)
- **Warranty** — serial number warranty tracking (NEW)

**Other services do not store** items, units, recipes, lots, suppliers, or purchase orders; they reference by `inventory_item_id`, `sku`, `recipe_id`, `lot_id`, `supplier_id` and get data via REST (e.g. GET /items, GET /units, GET /recipes, GET /lots, GET /suppliers) or events. Ordering and POS may keep a **read-only projection/cache** of catalog synced from inventory.

**Other services reference**: `inventory_item_id`, `inventory_sku`, `recipe_id`, `reservation_id`, `lot_id`, `supplier_id`, `purchase_order_id`, `transfer_id`, `warranty_id`; catalog and units via inventory-api APIs or sync.

---

### Ordering-Service (ordering-backend)
**Owns** (order lifecycle and cafe context only):
- Online orders (now with appointment_id, staff_preference_id, preferred_carrier), order_items (now with item_type, service_start_time, duration_minutes), carts, cart_items
- Cafe/outlet context (cafes, outlets) as used by ordering
- Promo codes, redemptions, loyalty accounts and transactions
- Cafe-specific user preferences/roles for ordering UX
- **CatalogOverride** — now with requires_age_verification, item_type, variant_options

**Catalog (catalog_items, catalog_categories):** Not owned as master. Either (A) **no local tables** — catalog read from inventory-api (proxy or frontend calls inventory), or (B) **read-only cache/projection** synced from inventory-api (all catalog writes go to inventory-api). `ordering-backend` pulls public core master data from `inventory-api`. Ordering stores only `item_id`/`sku`/`recipe_id` references.

**Does not store (reference only):** Payment intents, payments, payment methods, refunds (treasury-api); notification events/templates/subscriptions (notifications-api); proof of delivery, logistics events (logistics-api). Ordering keeps only `payment_intent_id` on Order and uses treasury client for intent create/get; notifications and payments modules use stub/treasury-only repositories.

**Other services reference**: `order_id`, `cafe_id`; logistics and treasury use order refs for tasks and payments.

---

### POS-Service (pos-api)
**Owns** (sales and shift context only):
- POS orders, pos_order_lines, cash_drawers, tenders, price_books, price_book_items
- **catalog_items** as **projection/cache** from inventory-api (not product master; sync or pull from inventory-api); CatalogItem now includes inventory_item_id, item_type, compliance flags, duration_minutes, cost_price, tags
- **OutletSetting** — display_mode (list/card/image_grid), show_barcode_scanner, enable_kds, enable_appointments
- **ModifierGroup** / **Modifier** — now with inventory_modifier_group_id / inventory_modifier_option_id for sync from inventory
- POS connections, outlets, sessions
- **KDSStation / KDSTicket** — Kitchen Display System routing and ticket lifecycle (NEW)
- **Appointment** — salon/service scheduling (NEW)
- **StaffMember** — staff with commission rates, service assignments (NEW)
- **SerialNumberLog** — serial number tracking at POS (NEW)
- **CommissionRecord** — commission tracking per staff member (NEW)

**Does not own**: Units, items, or recipes — obtained from inventory-api via REST or sync. Stock consumption reported to inventory-api via REST (POST /consumption) or event (`pos.sale.finalized`).

**Other services reference**: `pos_order_id`, `pos_outlet_id`, `pos_connection_id`, `appointment_id`, `staff_member_id`.

---

### Treasury-Service (treasury-api)
**Owns** (single source of truth for money and tax):
- Payment intents (now with allow_split), transactions, payment methods
- Refunds, payouts, invoices
- Taxes, payment gateway config, chart of accounts, ledger
- **PaymentSplit** — split payments across multiple methods (NEW)
- **Settlement / SettlementLine** — merchant settlement processing (NEW)
- **ReconciliationRun** — gateway reconciliation (NEW)
- **InstallmentPlan / Installment** — buy-now-pay-later support (NEW)

**Other services** store only payment references and minimal snapshots (e.g. amount at payment time); they do not duplicate treasury entities.

**Other services reference**: `payment_intent_id`, `payment_id`, `payout_id`, `settlement_id`, `installment_plan_id`; payment status via webhooks or events.

---

### Logistics-Service (logistics-api)
**Owns**:
- Rider/fleet member profiles (KYC, documents, vehicle); FleetMember now includes specialization_tags, has_cold_storage, max_weight_capacity_kg
- Delivery tasks (expanded task_type: food_delivery, retail_delivery, outlet_transfer, commercial_courier, drop_shipping; now with package_weight_kg, package_dimensions_cm, temperature_control, fragile/heavy flags, carrier_id), availability
- Telemetry and location, proof of delivery
- Rider earnings and payouts (logistics-side)
- **PricingRule** — dynamic pricing: distance/weight/time/surge/flat rate rules (NEW)
- **RiderShift** — shift management with zone assignment (NEW)

**Other services reference**: `rider_id`, `logistics_task_id`, `pricing_rule_id`, `shift_id`; rider/task data via logistics APIs (e.g. GET /fleet-members, POST /tasks).

---

### Subscriptions-Service (subscriptions-api)
**Owns**:
- Subscription plans, plan features, tier limits
- Tenant subscriptions, usage, billing state

**Other services** do not store plan or entitlement data; they check subscription/entitlement via subscriptions-api before using inventory, POS, logistics, treasury, etc.

---

### Notifications-Service (notifications-api)
**Owns**:
- Notification templates, delivery status
- Channel preferences (per user, per tenant)

**Other services reference**: trigger sends via API or events; store only message/template IDs if needed for audit.

---

### IoT-Service (iot-service-api)
**Owns**:
- Devices, telemetry, rules, alerts

**Consumers**: inventory-api (e.g. temperature/compliance), notifications; optional POS/inventory hardware (terminals, scanners, scales, KDS) documented in architecture/integrations.

---

## Entities That Must Not Exist in Non-Owner Services (No Duplication, No Legacy)

The following entities belong to a single owner. **No other service may store them.** Remove any such tables and logic from non-owner services; use references (IDs) and API/event calls only.

| Entity / Table(s) | Owner | Must NOT exist in |
|-------------------|-------|--------------------|
| Proof of delivery (signature, photo, OTP, recipient, rating) | **logistics-api** | ordering-backend, pos-api |
| Delivery task lifecycle events (task created, assigned, completed) | **logistics-api** | ordering-backend (no `logistics_events` table) |
| Notification templates, notification events, notification subscriptions | **notifications-api** | ordering-backend, pos-api, inventory-api |
| Payment intents, payments, payment methods, refunds, treasury webhook events | **treasury-api** | ordering-backend, pos-api (only refs on order: e.g. `payment_intent_id` UUID, `payment_status`) |
| PaymentSplit, Settlement, ReconciliationRun, InstallmentPlan/Installment | **treasury-api** | ordering-backend, pos-api, logistics-api |
| Product master (items, units, recipes, BOM, product categories) | **inventory-api** | ordering-backend, pos-api (only projection/cache synced from inventory; no authoring) |
| CustomFieldDefinition/Value, InventoryLot, VariantAttribute, Bundle/Component, Supplier, PurchaseOrder, StockTransfer, Warranty | **inventory-api** | ordering-backend, pos-api, logistics-api, treasury-api |
| KDSStation/Ticket, Appointment, StaffMember, SerialNumberLog, CommissionRecord | **pos-api** | ordering-backend, inventory-api, logistics-api (only refs e.g. `appointment_id`, `staff_member_id`) |
| PricingRule, RiderShift | **logistics-api** | ordering-backend, pos-api, treasury-api |
| Rider/fleet member profiles, KYC, vehicles, shifts | **logistics-api** | ordering-backend (only `rider_id`, `logistics_task_id` refs in order_assignments) |
| Tenant and user identity (full profile, sessions, MFA, OAuth) | **auth-api** | ordering-backend, pos-api (only `tenant_id`, `user_id` refs; minimal JIT cache allowed for FK only) |

**Ordering-backend cleanup (target state):**
- **Remove** (schemas + all associated logic): `proof_of_delivery`, `logistics_events`, `notification_templates`, `notification_events`, `notification_subscriptions`, `payment_intents`, `payments`, `payment_methods`, `refunds`, `treasury_events`.
- **Keep** (refs only): `order_assignments` with `logistics_task_id`, `rider_id` (no PoD edge); `orders` with `payment_intent_id` (UUID), `payment_status`, and optional amount snapshot for display; trigger notifications via notifications-api API or events; get payment details from treasury-api when needed.
- **Catalog:** `catalog_items` / `catalog_categories` only as read-only cache synced from inventory-api, or remove and proxy inventory-api for catalog (see plan).

**Logistics-api (owner):** Already has `proof_of_delivery` (task_id, fleet_member_id, signature_url, photo_url, etc.). ERD documents it. No ordering-backend copy.

**Notifications-api (owner):** Owns templates and delivery logs. Ordering and others send via API/events; no local template tables.

**Treasury-api (owner):** Owns payment intents, payments, refunds. Ordering and POS store only `payment_intent_id` and status on order; no local payment/refund tables.

---

## How Data Is Accessed (No Duplication)

- **REST:** Primary for reads and commands: catalog (GET items/units/recipes from inventory-api), reserve/consume (ordering → inventory-api), payments (ordering/pos → treasury-api), rider/task (ordering → logistics-api), JWT validation (all → auth-api).
- **NATS events:** For async sync and lifecycle: order lifecycle (`ordering.order.*`), stock/reservation (`inventory.stock.updated`, `inventory.reservation.confirmed`), sale finalised (`pos.sale.finalized` → inventory backflush), auth sync (`auth.user.*`, `auth.tenant.*`). Consumers must be idempotent.
- **gRPC (optional):** For low-latency calls where needed (e.g. stock check before add-to-cart); document in each service’s architecture.md if introduced.

---

## Cross-Service Event Subscription Matrix

| Publisher | Event Subject | Subscriber | Action |
|:---|:---|:---|:---|
| Auth Service | `auth.user.created` | Ordering, Subscriptions, Notifications | Create local user ref / trial / welcome |
| Auth Service | `auth.user.updated` | Ordering | Sync profile |
| Auth Service | `auth.user.deactivated` | Ordering | Deactivate local user |
| Auth Service | `auth.tenant.created` | Ordering, Subscriptions | Init tenant / trial |
| Auth Service | `auth.tenant.updated` | Ordering | Sync tenant |
| Ordering Service | `ordering.order.created` | Inventory (reserve), Notifications, Treasury | Reserve stock, confirm, payment intent |
| Ordering Service | `ordering.order.ready` | Logistics | Create delivery task |
| Ordering Service | `ordering.order.completed` | Inventory | Consume reservation |
| Inventory Service | `inventory.stock.updated`, `inventory.stock.low` | Ordering (optional) | Availability / out-of-stock flags |
| Inventory Service | `inventory.category.created/updated` | POS, Ordering | Sync hierarchical categories |
| Inventory Service | `inventory.lot.expiring_soon` | Notifications | Expiry alerts to tenant admins |
| Inventory Service | `inventory.purchase_order.received` | Notifications | PO receipt confirmation |
| Inventory Service | `inventory.transfer.shipped` | Notifications | Transfer dispatch notification |
| POS Service | `pos.sale.finalized` | Inventory | Backflush / consumption |
| POS Service | `pos.kds.ticket.ready` | Notifications | KDS ticket ready alert |
| POS Service | `pos.appointment.created/completed` | Notifications, Ordering | Appointment lifecycle sync |
| Ordering Service | `ordering.booking.created` | POS, Notifications | Service booking created |
| Treasury Service | Payment webhooks (HTTP) | Ordering | Update order payment status |
| Treasury Service | `treasury.settlement.completed` | Notifications | Settlement batch notification |
| Treasury Service | `treasury.installment.due` | Notifications | Installment due reminder |
| Logistics Service | Delivery webhooks (HTTP) | Ordering | Update order delivery status |

**Note:** Catalog and units are read via REST from inventory-api; ordering and POS do not duplicate product master. Event subjects follow `domain.entity.action` (e.g. `ordering.order.created`). See each service’s `integrations.md` for full event catalog.

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

   **From Ordering / Cafe UI** (ordering-backend; cafe-website and ordering-frontend call ordering-backend):
   ```
   1. User initiates rider onboarding in cafe/ordering UI
   2. Check tenant has logistics service enabled:
      GET /api/v1/tenants/{tenant_id}/services (subscriptions-api)
      → Verify "logistics" in enabled_services
   3. If not enabled: Show error "Logistics service not available. Upgrade plan."
   4. If enabled, choose one:
      Option A - API Push:
        - POST to ordering-backend → ordering-backend calls logistics-api:
          POST /v1/{tenant}/fleet-members
        - Logistics-api creates rider (auth user if needed)
        - Returns rider_id
        - Ordering-backend stores only rider_id reference
      Option B - UI Redirect:
        - Redirect to logistics UI for onboarding
        - User authenticates with auth-service (SSO)
        - Logistics-api stores rider profile; redirect back with rider_id
   ```

   **Standalone Logistics Service**:
   ```
   1. User goes directly to logistics-service UI
   2. User authenticates via auth-service (SSO)
   3. User completes rider onboarding
   4. All rider data stored in logistics-service (no duplication in ordering-backend)
   5. No ordering-backend involvement
   ```

### Pattern 2: Tenant Service Availability Check

**Before creating/referencing data in another service** (except auth-api, which is always available):

```go
// Pseudo-code example
func createRider(ctx context.Context, tenantID uuid.UUID, riderData RiderData) error {
    // 1. Check tenant has logistics service enabled (subscriptions-api)
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

    // 3. Create rider in logistics-service (only owner stores rider data)
    riderID, err := logisticsService.CreateFleetMember(ctx, tenantID, riderData)
    if err != nil {
        return err
    }

    // 4. Store only reference ID locally (no duplication of rider profile)
    return orderingRepo.StoreRiderReference(ctx, tenantID, riderID)
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

### Example 1: Creating a Rider from Ordering / Cafe

**Scenario**: Tenant has ordering and logistics enabled

1. User clicks "Become a Rider" in cafe/ordering UI
2. Frontend checks tenant services: `GET /api/v1/tenants/{tenant_id}/services` (subscriptions-api)
3. If logistics enabled:
   - Option A: Submit to ordering-backend → ordering-backend calls logistics-api (no rider data stored in ordering DB)
   - Option B: Redirect to logistics UI for self-onboarding
4. Logistics-api creates rider (and auth user if needed); stores all rider data
5. Returns `rider_id` to ordering-backend
6. Ordering-backend stores only `rider_id` reference (no duplication of rider profile)

### Example 2: Standalone Logistics Service

**Scenario**: Tenant only has logistics (no ordering)

1. User goes to logistics-service UI
2. User authenticates via auth-service (SSO)
3. User completes rider onboarding
4. All rider data stored in logistics-service
5. No ordering-backend involvement

### Example 3: Order Assignment with Rider

**Scenario**: Assign rider to order

1. Ordering-backend queries riders via logistics-api: `GET /v1/{tenant}/fleet-members?status=available`
2. Logistics-api returns rider list (data stays in logistics; ordering does not copy it)
3. Ordering-backend stores only `rider_id` in order_assignments
4. Ordering-backend creates delivery task: `POST /v1/{tenant}/tasks` with `order_id`, `rider_id`
5. Logistics-api owns task lifecycle; ordering-backend consumes events: `logistics.task.assigned`, `logistics.task.completed`

---

## Event Subscription Matrix (Detail)

| Publisher | Event | Subscribers |
|:---|:---|:---|
| auth-service | `auth.user.created` | subscription-service (trial), notifications-service (welcome) |
| auth-service | `auth.tenant.created` | subscription-service (trial), notifications-service (onboarding) |
| auth-service | `auth.user.password_changed` | notifications-service (security alert) |
| subscription-service | `subscription.activated` | auth-service (JWT refresh), notifications-service |
| subscription-service | `subscription.upgraded` / `cancelled` | auth-service, notifications-service |
| ordering-service | `ordering.order.created` | inventory (reserve), logistics (task), notifications, treasury |
| ordering-service | `ordering.order.ready` | logistics-service (delivery task) |
| ordering-service | `ordering.order.completed` | inventory (consume), notifications |
| inventory-service | `inventory.stock.updated`, `inventory.stock.low` | ordering (optional availability) |
| pos-service | `pos.sale.finalized` | inventory-service (backflush/consumption) |
| logistics-service | `logistics.task.completed`, `task.assigned` | ordering-service, notifications-service |
| treasury-service | Payment webhooks / `payment.completed` | ordering-service, notifications-service |

---

## Best Practices

1. **No data duplication:** Each entity lives in one service only; others hold references (IDs) and optionally minimal snapshots for audit.
2. **Check service availability:** Before creating or referencing data in another service, verify tenant has that service enabled (subscriptions-api); auth-api is always available.
3. **Store only references:** Never copy full entities across services; store `*_id` and call the owning service’s API or consume its events when you need data.
4. **Catalog from inventory:** Product master (items, units, recipes, categories) is owned by inventory-api; ordering and POS use REST or synced projection/cache only.
5. **Use events for lifecycle sync:** Use NATS for order lifecycle, stock updates, and auth sync; keep consumers idempotent.
6. **Support standalone mode:** Each service should work when it is the only one enabled for the tenant.

---

## Current State (Post-Cleanup Target)

- **Ordering-backend:** No proof_of_delivery, logistics_events, notification_* tables, or payment/payment_intent/refund/treasury_events tables. Only refs on orders and order_assignments; catalog from inventory (cache or proxy).
- **Logistics-api:** Single source of truth for proof_of_delivery, tasks, riders; erd.md reflects this.
- **Inventory-api:** Single source of truth for items (with barcode/compliance/weight/dimensions), units, recipes (with costing), recipe_ingredients, warehouses, balances (with auto-reorder), reservations, consumptions, hierarchical categories, custom fields, lots, variant attributes, bundles, suppliers, purchase orders, stock transfers, warranties.
- **POS-api:** Single source of truth for KDS stations/tickets, appointments, staff members, serial number logs, commission records; catalog items synced from inventory via NATS events (inventory.item.created/updated) with full compliance flags, item_type, inventory_item_id FK, barcode, duration_minutes. Sync handler in `internal/modules/catalog/inventory_events.go`. POS ModifierGroups reference inventory via `inventory_modifier_group_id` FK.
- **Logistics-api:** Single source of truth for expanded task types (food_delivery, retail_delivery, outlet_transfer, commercial_courier, drop_shipping), pricing rules, rider shifts with zone assignment; fleet members with specialization and capacity.
- **Notifications-api:** Owns templates and delivery; no template storage in ordering or POS.
- **Treasury-api:** Owns all payment entities including split payments, settlements/lines, reconciliation runs, installment plans/installments; ordering/POS hold only payment_intent_id and status refs.

---

## Migration Notes

- **No backward compatibility for wrong ownership.** Remove legacy or duplicate entities from non-owner services; do not keep them for compatibility.
- Legacy `riderprofile` and `riderdocument` in ordering-backend are **removed**. All rider data is in logistics-api; ordering-backend stores only `rider_id` and `logistics_task_id` refs.
- **Ordering-backend:** Remove ProofOfDelivery, LogisticsEvent, NotificationTemplate, NotificationEvent, NotificationSubscription, Payment, PaymentIntent, PaymentMethod, Refund, TreasuryEvent schemas and all related handlers/repos; Order keeps payment_intent_id (UUID), payment_status; get PoD from logistics-api, payment details from treasury-api, send notifications via notifications-api.
- Catalog/menu: Source of truth is inventory-api. Ordering-backend must not own menu_items/menu_categories as master — either remove and proxy inventory-api, or keep as read-only cache synced from inventory-api (see plan and service erd.md).

---

## Shared Libraries (Uniformity)

All Go services should use these shared libraries from `github.com/Bengo-Hub/`:

| Library | Purpose | Version | Services |
|---------|---------|---------|----------|
| `httpware` | HTTP middleware, tenant/user context, CORS | v0.3.0 | All 7 services |
| `shared-events` (events) | Transactional outbox, NATS publishing | v0.2.0 | All 7 services |
| `auth-client` | JWT validation, JWKS, permissions middleware | v0.4.x | All 7 services |
| `cache` | Redis tenant cache (branding, config) | v0.2.0 | ordering, inventory, logistics, notifications, subscriptions |
| `service-client` | gRPC/REST inter-service client | v0.2.0 | ordering, notifications, treasury, subscriptions |
| `pagination` | Cursor/offset pagination helpers | v0.1.0 | notifications (adopt in others as needed) |

Frontend shared package: `@bengo-hub/shared-ui-lib` v0.1.0 — SSOLoginModal, TreasuryPaymentModal, TrackingIframeModal. Used by ordering-frontend, pos-ui, inventory-ui, cafe-website. All must pin to `#v0.1.0`.

---

## References

- [Microservice Architecture for POS, Inventory, Orders](Microservice%20Architecture%20for%20POS,%20Inventory,%20Orders.md) — research and use cases per service
- Per-service docs: each backend’s `docs/erd.md`, `docs/integrations.md`, `docs/architecture.md` reference this document for cross-service ownership
- Auth: auth-api `docs/integrations.md`; Ordering: ordering-backend `docs/CROSS-SERVICE-DATA-OWNERSHIP.md` (service-specific extension)

