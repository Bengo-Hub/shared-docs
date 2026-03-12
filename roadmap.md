# BengoBox Microservices Implementation Roadmap

**Date**: December 31, 2025
**Last Updated**: February 14, 2026
**Current Status**: Phase 5/6 — Ordering, Logistics, Treasury, and Frontend Applications MVP

**Progress Update (February 14, 2026) — Production Readiness Sprint**:
- ✅ **Auth-UI Production Readiness** (P1): Forgot password UI, 2FA setup UI, org creation wiring, session management, API key management UI, return URL security fix
- ✅ **Auth Event Publishing** (P2): NATS outbox pattern integrated into auth-service; events published for user.created, user.login, user.logout, tenant.created across all auth flows (register, login, OAuth, logout)
- ✅ **Subscription Service Lifecycle** (P3): State machine (TRIAL→ACTIVE→CANCELLED/EXPIRED→RENEWED), lifecycle endpoints (create/upgrade/downgrade/cancel/renew), product activation/deactivation, NATS event publishing, multi-service product model (8 products, 3 bundles, 6 plans)
- ✅ **Notifications Service** (P4): SendGrid email provider (HTTP API), Twilio SMS provider (HTTP API), worker retry logic (3 attempts with NAck/redelivery), refactored worker into modular functions

**Previous Update (February 13, 2026)**:
- ✅ **Multi-Tenant URL Routing**: `[orgSlug]` implemented across all frontends and backends
- ✅ **Shared Libraries**: auth-client (TenantSlug in JWT), httpware (TenantV2 middleware), service-client (header propagation)
- ✅ **Auth Service**: JWT enrichment with `tenant_slug` claim
- ✅ **Ordering Service**: Backend + Frontend with `[orgSlug]` routes (16 routes, 37 test cases)
- ✅ **Logistics Service**: Backend + Rider App PWA with `[orgSlug]` routes (6 routes, 24 test cases)
- ✅ **Treasury Service**: Backend with TenantV2 middleware (20 test cases)
- ✅ **Cafe Website**: Upgraded to Next.js 16.1.6 with tenant-aware redirects (24 routes)
- ✅ **Deployment Pipelines**: ArgoCD configs for ordering-frontend, rider-app, cafe-website
- 📋 **Next**: Deploy to K8s cluster, E2E verification, Inventory Service Sprint 1

---

## Executive Summary

This roadmap outlines the implementation order for all BengoBox microservices, prioritized by dependencies and integration requirements. Services are grouped into implementation phases based on their dependencies on other services, ensuring that foundational services are implemented first before dependent services.

---

## Implementation Phases Overview

| Phase | Services | Duration | Dependencies |
|-------|----------|----------|--------------|
| **Phase 0: Infrastructure** | Redis, NATS, PostgreSQL | 1 week | None |
| **Phase 1: Foundation** | Auth Service | 2-3 weeks | Infrastructure |
| **Phase 2: Core Infrastructure** | Notifications, Subscription | 3-4 weeks | Auth Service |
| **Phase 3: Financial Foundation** | Treasury Service | 4-5 weeks | Auth, Notifications, Subscription |
| **Phase 4: Business Core** | Inventory Service | 3-4 weeks | Auth, Subscription |
| **Phase 5: Ordering & Fulfillment** | Ordering, Logistics, POS | 8-12 weeks | All previous phases |
| **Phase 6: Frontend Applications** | Cafe Website, Ordering UI, Rider App | 6-8 weeks | All backend services |
| **Phase 7: Additional Services** | ERP, Projects, IoT, Ticketing | Future | Varies |

---

## Phase 0: Infrastructure Setup (Week 1)

### Services to Deploy

1. **Redis** (Shared Cache & Session Store)
   - **Purpose**: Session sharing across services, caching, queues
   - **Dependencies**: None
   - **Priority**: Critical - Required by all services

2. **NATS JetStream** (Message Broker)
   - **Purpose**: Event-driven communication, async messaging
   - **Dependencies**: None
   - **Priority**: Critical - Required for event-driven architecture

3. **PostgreSQL** (Primary Database)
   - **Purpose**: Primary data store for all services
   - **Dependencies**: None
   - **Priority**: Critical - Required by all services

### Completion Criteria
- ✅ All infrastructure services running and accessible
- ✅ Connection strings configured for all services
- ✅ Monitoring and health checks in place

---

## Phase 1: Foundation Layer (Weeks 2-4)

### 1.1 Auth Service (`auth-service`)

**Priority**: **CRITICAL - Must be implemented first**

**Dependencies**: Infrastructure (Redis, PostgreSQL)

**Dependents**: ALL other services depend on auth-service

**Why First?**
- All services require SSO authentication
- Tenant/user identity management foundation
- JWT token issuance for all services
- Tenant/outlet discovery webhooks

**Key Features to Implement**:
- ✅ User registration and login (already implemented)
- ✅ JWT token issuance and validation
- ✅ OAuth2/OIDC provider capabilities
- ✅ Tenant/outlet management
- ✅ User identity management
- ✅ Tenant/outlet discovery webhooks
- ✅ MFA support
- ✅ Session management
- ✅ **Role Management Endpoints** (role CRUD, user-role assignments, role-permission management) - **COMPLETED December 31, 2025**
- ✅ **Auth UI Modernization** (Next.js 15, Tailwind CSS, and Favicon branding)

**Completion Criteria**:
- ✅ SSO working with JWT tokens
- ✅ Tenant/outlet discovery webhooks functional
- ✅ All dependent services can validate JWT tokens
- ✅ User management APIs operational
- ✅ Role management APIs operational
- 🚧 **Frontend Role Management UI** (Next Sprint - Sprint 06)

**Estimated Duration**: 2-3 weeks (backend features complete, frontend pending)

---

## Phase 2: Core Infrastructure Services (Weeks 5-8) - **NEXT IN LINE** 📋

### 2.1 Notifications Service (`notifications-service`) - **Priority: Start Here**

**Priority**: **HIGH - Required by most services**

**Dependencies**: 
- Auth Service (user lookup, tenant context)
- Infrastructure (NATS for events, Redis for queues)

**Dependents**: 
- Treasury Service
- Subscription Service
- Ordering Service
- Logistics Service
- POS Service
- All other services for alerts

**Why Second?**
- Required for payment confirmations, order notifications, alerts
- Can work standalone but needs auth for user lookup
- Foundation for all user-facing notifications

**Key Features to Implement**:
- ✅ Multi-channel notifications (Email, SMS, Push)
- ✅ Template management
- ✅ Event-driven notification triggers
- ✅ Delivery status tracking
- ✅ OTP delivery for MFA (auth-service integration)

**Completion Criteria**:
- ✅ Email notifications working
- ✅ SMS notifications working (Twilio/Africa's Talking)
- ✅ Push notifications working
- ✅ Event consumption from NATS functional
- ✅ Template system operational

**Estimated Duration**: 2 weeks (already implemented, needs verification)

---

### 2.2 Subscription Service (`subscription-service`)

**Priority**: **HIGH - Required for licensing and feature gating**

**Dependencies**:
- Auth Service (tenant/user sync, JWT claims extension)
- Infrastructure (PostgreSQL, Redis, NATS)

**Dependents**:
- All business services (ordering, logistics, POS, inventory)
- Treasury Service (billing events)

**Why Second?**
- Required for feature gating across all services
- Usage tracking and limit enforcement
- Billing event generation (feeds treasury)
- Auto-assign Starter plan to new tenants

**Key Features to Implement**:
- ✅ Plan management (Starter, Growth, Professional)
- ✅ Tenant subscription lifecycle
- ✅ Feature entitlement validation
- ✅ Usage tracking aggregation
- ✅ Overage calculation
- ✅ JWT claims extension (for auth-service)
- ✅ Billing event emission (for treasury)

**Completion Criteria**:
- ✅ All 3 plans defined and seeded
- ✅ Feature gates working
- ✅ Usage tracking APIs functional
- ✅ JWT claims extension integrated with auth-service
- ✅ Billing events emitted to treasury

**Estimated Duration**: 3-4 weeks

---

## Phase 3: Financial Foundation (Weeks 9-13)

### 3.1 Treasury Service (`finance-service/treasury-api`)

**Priority**: **HIGH - Required for payments and billing**

**Dependencies**:
- Auth Service (user/tenant context, JWT validation)
- Notifications Service (payment alerts, invoice delivery)
- Subscription Service (billing events consumption)

**Dependents**:
- Ordering Service (payment processing)
- POS Service (payment processing)
- Logistics Service (expense export, payouts)
- Subscription Service (receives billing events)

**Why Third?**
- Required for all payment operations
- Handles subscription billing (from subscription-service)
- Processes payments for orders
- Manages financial ledger and reconciliation

**Key Features to Implement**:
- ⏳ **Sprint 1 (CRITICAL)**: Auth, RBAC & User Management (MUST BE FIRST)
- 🚧 Payment intent creation (Sprint 2 - blocked until auth/RBAC complete)
- ❌ M-Pesa integration (STK Push, C2B, B2C)
- ❌ Card payment integration (Stripe)
- ❌ Payment webhooks
- ❌ Invoice generation
- ❌ Billing event consumption (from subscription-service)
- ❌ Refund processing
- ❌ Payout orchestration
- ❌ General ledger (double-entry bookkeeping)

**Completion Criteria**:
- ✅ M-Pesa STK Push working
- ✅ Payment webhooks functional
- ✅ Invoice generation operational
- ✅ Billing events from subscription-service processed
- ✅ Refund APIs working

**Estimated Duration**: 4-5 weeks

---

## Phase 4: Business Core Services (Weeks 14-17)

### 4.1 Inventory Service (`inventory-service`)

**Priority**: **MEDIUM-HIGH - Required for stock management**

**Dependencies**:
- Auth Service (tenant/user context)
- Subscription Service (feature gating for inventory features)

**Dependents**:
- Ordering Service (stock availability queries)
- POS Service (stock consumption)
- Logistics Service (transfer tasks)

**Why Fourth?**
- Required before ordering-service can check stock
- POS service needs stock consumption tracking
- Can work standalone but ordering/POS depend on it

**Key Features to Implement**:
- ⏳ **Sprint 1 (CRITICAL)**: Auth, RBAC & User Management (MUST BE FIRST)
- ❌ Item/SKU management (blocked until auth/RBAC complete)
- ❌ Warehouse and location management
- ❌ Stock balances and movements
- ❌ Purchase orders
- ❌ Stock reservations
- ❌ Low-stock alerts
- ❌ Multi-warehouse support

**Completion Criteria**:
- ✅ Item catalog APIs working
- ✅ Stock availability queries functional
- ✅ Stock reservation system operational
- ✅ Events published for stock updates

**Estimated Duration**: 3-4 weeks

---

## Phase 5: Ordering & Fulfillment Services (Weeks 18-29)

### 5.1 Logistics Service (`logistics-service`) - PARTIAL

**Priority**: **HIGH - Required for delivery operations**

**Dependencies**:
- Auth Service (rider authentication, tenant context)
- Subscription Service (rider limit enforcement, feature gating)
- Notifications Service (delivery notifications)
- Treasury Service (expense export, payouts) - can be partial
- Infrastructure (NATS, Redis, PostgreSQL with PostGIS)

**Dependents**:
- Ordering Service (delivery tasks)
- POS Service (pickup tasks)

**Why Before Ordering?**
- Ordering service needs logistics for delivery tasks
- Can be implemented in parallel with ordering-service (MVP features only)
- Full features can come later

**Key Features to Implement (MVP)**:
- ✅ Fleet member (rider) management
- ✅ Task lifecycle (create, assign, complete)
- ✅ Basic routing (pickup → delivery)
- ✅ Real-time location tracking (WebSocket)
- ✅ Proof of delivery (photo, signature)
- ✅ Rider PWA (basic features)

**Completion Criteria**:
- ✅ Rider onboarding working
- ✅ Task creation from ordering-service working
- ✅ Real-time tracking functional
- ✅ Proof of delivery capture working
- ✅ Rider PWA operational (basic)

**Estimated Duration**: 4-5 weeks (MVP), full features later

---

### 5.2 Ordering Service (`ordering-service`)

**Priority**: **HIGH - Core business service**

**Dependencies**:
- Auth Service (customer authentication, SSO)
- Subscription Service (feature gating, usage tracking, limit enforcement)
- Treasury Service (payment processing)
- Inventory Service (stock availability)
- Logistics Service (delivery tasks) - can be partial
- Notifications Service (order notifications)

**Dependents**:
- Cafe Website (menu browsing, order placement)
- Ordering Frontend (customer PWA)

**Why After Logistics?**
- Needs logistics-service for delivery task creation
- Can start catalog/menu work in parallel with logistics

**Key Features to Implement**:
- ✅ **Sprint 1 (MOSTLY COMPLETE)**: Auth/RBAC implementation - **Event listeners verified, superuser handling needs verification**
- ⏳ Multi-tenant catalog/menu management (Sprint 2 - ready to proceed)
- ❌ Shopping cart (Redis-cached)
- ❌ Order placement (online delivery orders only)
- ❌ Payment integration (treasury-service)
- ❌ Delivery task creation (logistics-service)
- ❌ Real-time order tracking
- ❌ Promo codes and loyalty program
- ❌ Ordering PWA (customer-facing)

**Completion Criteria**:
- ✅ Menu browsing and cart working
- ✅ Order placement with payment working
- ✅ Delivery tasks created in logistics-service
- ✅ Real-time tracking functional
- ✅ Ordering PWA operational

**Estimated Duration**: 6-8 weeks

---

### 5.3 POS Service (`pos-service`)

**Priority**: **MEDIUM - Can be implemented in parallel**

**Dependencies**:
- Auth Service (cashier authentication)
- Subscription Service (feature gating)
- Treasury Service (payment processing)
- Inventory Service (stock consumption)
- Logistics Service (pickup tasks) - optional
- Notifications Service (order ready alerts)

**Dependents**:
- Cafe Website (admin dashboard integration)

**Why After Ordering?**
- Similar dependencies to ordering-service
- Can be implemented in parallel with ordering-service
- Lower priority for initial launch (online orders first)

**Key Features to Implement**:
- ⏳ **Sprint 1 (PLAN NEEDED)**: Auth, RBAC & User Management - **Sprint plan needs creation**
- ❌ POS order creation (over-the-counter, pickup, dine-in) - blocked until auth/RBAC
- ❌ Cash drawer management
- ❌ Kitchen ticket printing
- ❌ Payment processing (treasury-service)
- ❌ Stock consumption (inventory-service)
- ❌ Pickup task creation (logistics-service) - optional

**Completion Criteria**:
- ✅ POS orders working
- ✅ Cash drawer reconciliation functional
- ✅ Payment processing integrated
- ✅ Stock consumption tracked

**Estimated Duration**: 4-5 weeks

---

## Phase 6: Frontend Applications (Weeks 30-37)

### 6.1 Cafe Website (`Cafe/cafe-website`)

**Priority**: **HIGH - Converging point for all services**

**Dependencies**:
- Auth Service (SSO integration)
- Ordering Service (menu browsing, order placement)
- Logistics Service (order tracking)
- Booking Service (events, rooms, conferences) - if implemented
- All backend services (admin dashboard integration)

**Why Last?**
- Requires all backend services to be functional
- Acts as converging point for all services
- Needs SSO working across all services

**Key Features to Implement**:
- ✅ Public pages (Home, About, Menu, Services, Events, Contact, Careers, Franchising)
- ✅ Menu browsing (from ordering-service)
- ✅ Order tracking (real-time map from logistics-service)
- ✅ SSO login integration
- ✅ Admin dashboard with service navigation
- ✅ Event/room booking (if booking service exists)
- ✅ Responsive PWA-ready design

**Completion Criteria**:
- ✅ All public pages working
- ✅ Menu browsing functional
- ✅ Order tracking with live map working
- ✅ SSO login working (shared session across services)
- ✅ Admin dashboard with service transitions working

**Estimated Duration**: 4-5 weeks

---

### 6.2 Ordering Frontend PWA (`ordering-service/ordering-frontend`)

**Priority**: **HIGH - Customer ordering experience**

**Dependencies**:
- Ordering Backend (all APIs)
- Auth Service (SSO for checkout)

**Why Last?**
- Requires ordering-backend to be complete
- Can start development in parallel with backend (mock APIs)

**Key Features to Implement**:
- ✅ Menu browsing and filtering
- ✅ Shopping cart management
- ✅ Checkout flow
- ✅ Payment integration
- ✅ Order tracking
- ✅ PWA installation prompt
- ✅ Offline support (cached menu)

**Completion Criteria**:
- ✅ Full ordering flow working
- ✅ PWA installable on mobile
- ✅ Offline menu browsing functional
- ✅ Real-time order tracking working

**Estimated Duration**: 3-4 weeks

---

### 6.3 Rider App PWA (`logistics-service/rider-app`)

**Priority**: **HIGH - Rider delivery experience**

**Dependencies**:
- Logistics Backend (all APIs)
- Auth Service (SSO for riders)

**Why Last?**
- Requires logistics-backend to be complete
- Critical for delivery operations

**Key Features to Implement**:
- ✅ Task list and acceptance
- ✅ Navigation to pickup/delivery locations
- ✅ Real-time location tracking
- ✅ Proof of delivery capture
- ✅ Earnings dashboard
- ✅ PWA installation prompt
- ✅ Background location tracking

**Completion Criteria**:
- ✅ Task acceptance and navigation working
- ✅ Real-time location tracking functional
- ✅ Proof of delivery capture working
- ✅ PWA installable on mobile
- ✅ Background location tracking operational

**Estimated Duration**: 3-4 weeks

---

## Phase 7: Additional Services (Future)

### 7.1 ERP Service (`erp/erp-api`)

**Priority**: **LOW - Not required for Urban Loft Cafe MVP**

**Dependencies**: Auth, Treasury, Inventory, Notifications

**Status**: Already in production, can be used as-is

---

### 7.2 Projects Service (`projects-service`)

**Priority**: **LOW - Not required for Urban Loft Cafe MVP**

**Dependencies**: Auth, Treasury, ERP, Notifications

**Status**: Already in production

---

### 7.3 IoT Service (`iot-service`)

**Priority**: **LOW - Not required for Urban Loft Cafe MVP**

**Dependencies**: Auth, Notifications

---

### 7.4 Ticketing Service (`ticketing-service`)

**Priority**: **LOW - Optional for support**

**Dependencies**: Auth, Notifications

---

## Dependency Graph

```
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                      │
│              (Redis, NATS, PostgreSQL)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Phase 1: Foundation                         │
│                   Auth Service                               │
│            (SSO, JWT, User Identity)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌───────────────┐ ┌──────────────┐ ┌──────────────┐
│ Notifications │ │ Subscription │ │  (All other  │
│    Service    │ │   Service    │ │   services)  │
└───────┬───────┘ └──────┬───────┘ └──────┬───────┘
        │                │                 │
        └────────┬───────┴────────┬────────┘
                 │                │
        ┌────────▼────────┐ ┌─────▼─────────┐
        │ Treasury Service│ │Inventory Service│
        └────────┬────────┘ └──────┬─────────┘
                 │                 │
        ┌────────┴────────┬────────┴────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Ordering   │ │  Logistics   │ │     POS      │
│   Service    │ │   Service    │ │   Service    │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                 │
       └────────┬───────┴────────┬────────┘
                │                │
                ▼                ▼
       ┌────────────────────────────────────┐
       │      Frontend Applications          │
       │  (Cafe Website, Ordering UI,       │
       │        Rider App PWA)              │
       └────────────────────────────────────┘
```

---

## Implementation Order Summary

### Phase 0: Infrastructure (Week 1)
1. ✅ Redis - Session store and caching
2. ✅ NATS JetStream - Event broker
3. ✅ PostgreSQL - Primary database

### Phase 1: Foundation (Weeks 2-4)
1. ✅ **Auth Service** - SSO, JWT, user identity

### Phase 2: Core Infrastructure (Weeks 5-8)
2. ✅ **Notifications Service** - Multi-channel notifications
3. ✅ **Subscription Service** - Licensing and feature gating

### Phase 3: Financial Foundation (Weeks 9-13)
4. ✅ **Treasury Service** - Payments and billing

### Phase 4: Business Core (Weeks 14-17)
5. ✅ **Inventory Service** - Stock management

### Phase 5: Ordering & Fulfillment (Weeks 18-29)
6. ✅ **Logistics Service (MVP)** - Rider management, delivery tasks
7. ✅ **Ordering Service** - Online delivery orders
8. ✅ **POS Service** - Over-the-counter/pickup orders

### Phase 6: Frontend Applications (Weeks 30-37)
9. ✅ **Cafe Website** - Converging point for all services (Modernized to Next.js 15, TanStack Query, and centralized Auth)
10. ✅ **Ordering Frontend PWA** - Customer ordering app
11. ✅ **Rider App PWA** - Rider delivery app

---

## Critical Path Analysis

### Must-Have for MVP Launch

1. **Auth Service** → Foundation for all services
2. **Subscription Service** → Feature gating and licensing
3. **Treasury Service** → Payment processing
4. **Notifications Service** → Order and payment notifications
5. **Ordering Service** → Core business functionality
6. **Logistics Service (MVP)** → Delivery operations
7. **Cafe Website** → Customer-facing interface
8. **Ordering Frontend PWA** → Customer ordering experience
9. **Rider App PWA** → Rider delivery experience

### Nice-to-Have (Can Launch Without)

- **Inventory Service** - Can start with manual stock management
- **POS Service** - Online orders first, POS can come later
- **ERP Service** - Not required for MVP
- **Projects Service** - Not required for MVP

---

## Parallel Implementation Opportunities

### Can Be Implemented in Parallel

**Phase 2** (Weeks 5-8):
- Notifications Service ↔ Subscription Service (independent)

**Phase 5** (Weeks 18-29):
- Logistics Service (MVP) ↔ Ordering Service (can start catalog work)
- POS Service ↔ Ordering Service (independent domains)

**Phase 6** (Weeks 30-37):
- Ordering Frontend ↔ Rider App (independent)
- Cafe Website (can start public pages in parallel)

---

## Risk Mitigation

### High-Risk Dependencies

1. **Auth Service Failure** → All services affected
   - **Mitigation**: Implement circuit breakers, graceful degradation
   - **Fallback**: Service-specific auth (not recommended, breaks SSO)

2. **Treasury Service Failure** → Payment processing blocked
   - **Mitigation**: Queue payment requests, retry mechanism
   - **Fallback**: Manual payment reconciliation

3. **Subscription Service Failure** → Feature gating blocked
   - **Mitigation**: Cache feature gates (stale data acceptable)
   - **Fallback**: Fail closed (deny access if check fails)

### Medium-Risk Dependencies

4. **Logistics Service Failure** → Delivery tasks blocked
   - **Mitigation**: Queue delivery requests, manual assignment
   - **Fallback**: Manual rider assignment

5. **Notifications Service Failure** → Alerts blocked
   - **Mitigation**: Queue notifications, retry mechanism
   - **Fallback**: Email directly (not recommended)

---

## Success Criteria Per Phase

### Phase 1 Success Criteria
- ✅ Users can register and login via SSO
- ✅ JWT tokens validated by all services
- ✅ Tenant/outlet discovery webhooks working

### Phase 2 Success Criteria
- ✅ Notifications sent via email/SMS/push
- ✅ Subscription plans defined and functional
- ✅ Feature gates working
- ✅ Usage tracking operational

### Phase 3 Success Criteria
- ✅ M-Pesa payments working
- ✅ Payment webhooks functional
- ✅ Invoices generated automatically
- ✅ Billing events from subscription-service processed

### Phase 4 Success Criteria
- ✅ Item catalog APIs working
- ✅ Stock availability queries functional
- ✅ Stock reservations working

### Phase 5 Success Criteria
- ✅ Online orders placed successfully
- ✅ Payments processed via treasury
- ✅ Delivery tasks created in logistics
- ✅ Real-time tracking working
- ✅ POS orders working (if implemented)

### Phase 6 Success Criteria
- ✅ Cafe website accessible and functional
- ✅ Customers can browse menu and place orders
- ✅ Order tracking with live map working
- ✅ Admin dashboard with service navigation working
- ✅ Ordering PWA installable
- ✅ Rider App PWA installable

---

## Timeline Summary

| Phase | Duration | Cumulative Weeks | Key Deliverables |
|-------|----------|------------------|------------------|
| Phase 0 | 1 week | Week 1 | Infrastructure ready |
| Phase 1 | 2-3 weeks | Weeks 2-4 | SSO working |
| Phase 2 | 3-4 weeks | Weeks 5-8 | Notifications & Licensing |
| Phase 3 | 4-5 weeks | Weeks 9-13 | Payments working |
| Phase 4 | 3-4 weeks | Weeks 14-17 | Inventory management |
| Phase 5 | 8-12 weeks | Weeks 18-29 | Ordering & Logistics MVP |
| Phase 6 | 6-8 weeks | Weeks 30-37 | Frontend applications |
| **Total** | **27-37 weeks** | **~7-9 months** | **MVP Launch Ready** |

---

## References

- **[Auth & RBAC Audit Summary](./auth-rbac-audit-summary.md)** - **CRITICAL: All services must complete Sprint 1 (Auth/RBAC) before domain features**
- [Microservices Architecture Audit Summary](./MICROSERVICES-ARCHITECTURE-AUDIT-SUMMARY.md)
- [Cross-Service Data Ownership](./CROSS-SERVICE-DATA-OWNERSHIP.md)
- [Trinity Authorization Pattern](./TRINITY-AUTHORIZATION-PATTERN.md)
- [Subscription Service Integrations](../subscription-service/docs/integrations.md)
- [Cafe Website Plan](../Cafe/cafe-website/docs/plan.md)

