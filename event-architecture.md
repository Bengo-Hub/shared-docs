# BengoBox Event Architecture

**Last Updated:** March 2026
**Status:** Production — All MVP backend services publish and consume events via NATS JetStream with transactional outbox pattern.

---

## Overview

All inter-service communication uses NATS (plain or JetStream) with the **transactional outbox pattern** for reliable event delivery. Events are written to an `outbox_events` table within the same DB transaction as the domain operation, then published asynchronously by a background poller.

---

## Event Envelope Format

### Outbox Events (shared-events library)
```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "aggregate_type": "treasury",
  "aggregate_id": "uuid",
  "event_type": "payment.succeeded",
  "payload": { ... },
  "timestamp": "RFC3339",
  "version": "1.0"
}
```
Subject derivation: `{aggregate_type}.{event_type}` (e.g., `treasury.payment.succeeded`)

### CloudEvents (ordering-backend, logistics-api)
```json
{
  "id": "uuid",
  "source": "ordering-service",
  "specversion": "1.0",
  "type": "ordering.order.created",
  "tenantId": "uuid",
  "data": { ... }
}
```

---

## Service Event Catalog

### auth-api (Plain NATS, not JetStream)

| Subject | Trigger | Key Payload Fields |
|---------|---------|-------------------|
| `auth.user.created` | User registration (email, Google, GitHub, Microsoft) | user_id, email, full_name, tenant_id, tenant_slug, roles, method |
| `auth.user.login` | User login (all methods) | user_id, email, tenant_id, tenant_slug, method, ip_address |
| `auth.user.logout` | Session revocation | user_id, session_id, tenant_id |
| `auth.tenant.created` | Tenant creation (registration, admin) | tenant_id, name, slug, use_case, created_by |
| `auth.tenant.branch.created` | Branch creation with tenant | tenant_id, name, is_default, use_case |

### ordering-backend (JetStream, stream: `ordering`)

| Subject | Trigger | Key Payload Fields |
|---------|---------|-------------------|
| `ordering.order.created` | Checkout / order creation | order_id, order_number, customer_id, total_amount, currency |
| `ordering.order.status.changed` | Any status transition | order_id, previous_status, new_status |
| `ordering.order.confirmed` | Order confirmed | order_id, customer_name, customer_email, total_amount |
| `ordering.order.ready` | Order ready for pickup/delivery | order_id, outlet_id, customer_id, delivery_address, items |
| `ordering.order.completed` | Order delivered/completed | order_id, customer_id, total_amount, completed_at |
| `ordering.order.cancelled` | Order cancelled | order_id, customer_id, reason, cancelled_by |
| `ordering.order.for_pickup` | POS pickup order | order_id, customer_name, customer_phone, items |

### inventory-api (JetStream, stream: `inventory`)

| Subject | Trigger | Key Payload Fields |
|---------|---------|-------------------|
| `inventory.item.created` | New item created | id, sku, name, category_name, is_active |
| `inventory.item.updated` | Item updated | id, sku, name, category_name, is_active |
| `inventory.stock.low` | Available stock <= reorder level | item_id, sku, name, available, reorder_level, warehouse_id |
| `inventory.stock.out` | Available stock reaches zero | item_id, sku, name, available, warehouse_id |
| `inventory.unit.created` | New unit created | id, name, abbreviation |
| `reservation.confirmed` | Stock reservation created | order_id, warehouse_id, items |
| `reservation.released` | Reservation cancelled | order_id, reason |
| `stock.consumed` | Reservation consumed (order completed) | order_id, consumed_at, items_count |

### logistics-api (JetStream, stream: `logistics`)

| Subject | Trigger | Key Payload Fields |
|---------|---------|-------------------|
| `logistics.fleet.member_invited` | Rider invited to fleet | member_id, user_id, fleet_id, user_email, user_name |
| `logistics.fleet.member_approved` | Rider application approved | member_id, user_id, fleet_id, user_email, user_name |
| `logistics.fleet.member_suspended` | Rider suspended | member_id, user_id, fleet_id, user_email, user_name |

### treasury-api (JetStream, stream: `treasury`)

| Subject | Trigger | Key Payload Fields |
|---------|---------|-------------------|
| `treasury.payment.created` | Payment intent created | intent_id, reference_id, reference_type, amount, currency, payment_method, status |
| `treasury.payment.succeeded` | Gateway callback success | intent_id, reference_id, amount, currency, provider, provider_reference, fee, customer_email |
| `treasury.payment.failed` | Gateway callback failure | intent_id, reference_id, amount, currency, provider, customer_email |

### subscriptions-api (JetStream, stream: `subscription`)

| Subject | Trigger | Key Payload Fields |
|---------|---------|-------------------|
| `subscription.created` | New subscription provisioned | tenant_id, plan_code, status, bundle_code, trial_days |
| `subscription.upgraded` | Plan tier increased | tenant_id, new_plan_code, old_plan_id, direction |
| `subscription.downgraded` | Plan tier decreased | tenant_id, new_plan_code, old_plan_id, direction |
| `subscription.cancelled` | Subscription cancelled | tenant_id, reason |
| `subscription.renewed` | Subscription renewed | tenant_id |

---

## Consumers by Service

### notifications-api (Worker Process)

| Consumer | Stream | Subjects | Notifications Triggered |
|----------|--------|----------|------------------------|
| Order Status | `ordering` | `ordering.order.>` | order_placed, order_ready, order_out_for_delivery, order_delivered, order_cancelled |
| Fleet Lifecycle | `logistics` | `logistics.fleet.>` | rider_invite, rider_onboarding_approved, rider_suspended |
| Inventory Stock | `inventory` | `inventory.>` | low_stock_alert, stock_out |
| Subscription Lifecycle | `subscription` | `subscription.>` | subscription_created, subscription_upgraded, subscription_downgraded, subscription_cancelled, subscription_renewed |
| Treasury Payments | `treasury` | `treasury.>` | payment_success, payment_failed |
| Auth Welcome | plain NATS | `auth.user.created` | welcome email |
| Identity Sync | plain NATS | `auth.user.*`, `auth.tenant.*` | (no notification — DB sync only) |

### ordering-backend

| Consumer | Subjects | Action |
|----------|----------|--------|
| Identity Sync | `auth.user.*`, `auth.tenant.*` | Sync users/tenants from auth-api |
| Branch Sync | `auth.tenant.branch.created` | Auto-create Outlet from branch |
| Inventory Sync | `inventory.item.created/updated` | Sync catalog projection |
| Fulfilment | `ordering.order.ready` | Auto-create delivery tasks |

### inventory-api

| Consumer | Subjects | Action |
|----------|----------|--------|
| Branch Sync | `auth.tenant.branch.created` | Auto-create Warehouse from branch |
| Order Lifecycle | `ordering.order.completed/cancelled` | Auto-consume/release reservations |

### logistics-api

| Consumer | Subjects | Action |
|----------|----------|--------|
| Identity Sync | `auth.user.created/updated` | Sync users, link to drivers |
| Order Ready | `ordering.order.ready` | Create delivery tasks |

### treasury-api

| Consumer | Subjects | Action |
|----------|----------|--------|
| Identity Sync | `auth.user.created/updated` | Sync users for RBAC |

### subscriptions-api

| Consumer | Subjects | Action |
|----------|----------|--------|
| Tenant Provisioning | `auth.tenant.created` | Auto-provision Starter subscription with 14-day trial |

### pos-api

| Consumer | Subjects | Action |
|----------|----------|--------|
| Inventory Sync | `inventory.item.created/updated` | Create/update CatalogItem projection |

---

## Outbox Pattern

All services use the transactional outbox pattern from `github.com/Bengo-Hub/shared-events`:

1. Domain operation + outbox record written in same DB transaction
2. Background publisher polls `outbox_events` table (default: every 2-5s, batch 100)
3. Events published to NATS JetStream
4. Records marked as PUBLISHED on success, retried up to 10 attempts

**Exception:** auth-api publishes via plain NATS `conn.Publish()` (not JetStream), so consumers use `nc.Subscribe()` instead of JetStream durable consumers.

---

## JetStream Durable Consumers (notifications-api worker)

| Durable Name | Stream | Subject |
|-------------|--------|---------|
| `notifications-worker` | `notifications` | `notifications.events` |
| `notifications-ordering-status` | `ordering` | `ordering.order.>` |
| `notifications-logistics-fleet` | `logistics` | `logistics.fleet.>` |
| `notifications-inventory-stock` | `inventory` | `inventory.>` |
| `notifications-subscription-lifecycle` | `subscription` | `subscription.>` |
| `notifications-treasury-payments` | `treasury` | `treasury.>` |
