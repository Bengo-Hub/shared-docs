# BengoBox Event Architecture

**Last Updated:** March 25, 2026 — Multi-industry revamp: Added inventory.category.created/updated, inventory.lot.expiring_soon, inventory.purchase_order.received, inventory.transfer.shipped, pos.kds.ticket.ready, pos.appointment.created/completed, ordering.booking.created, treasury.settlement.completed, treasury.installment.due. Previous (March 24): ordering.order.refunded/scheduled/rated, logistics.task.eta_updated, treasury.refund.completed. All events include `notification` block with explicit target (customer/tenant_admin/staff/rider) and recipient details.
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
| `auth.user.password_reset.requested` | Password reset requested | user_id, email, tenant_id |
| `auth.user.password_reset.completed` | Password reset completed | user_id, email |

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
| `ordering.order.refunded` | Order refunded | order_id, customer_id, amount, reason, notification{target=customer} |
| `ordering.order.scheduled` | Scheduled order created | order_id, scheduled_for, customer_email, notification{target=customer} |
| `ordering.order.rated` | Customer rated order | order_id, outlet_id, rating, comment |
| `ordering.booking.created` | Service booking/appointment order created | order_id, appointment_id, staff_preference_id, service_start_time, duration_minutes |

### inventory-api (JetStream, stream: `inventory`)

| Subject | Trigger | Key Payload Fields |
|---------|---------|-------------------|
| `inventory.item.created` | New item created | id, sku, name, category_name, is_active |
| `inventory.item.updated` | Item updated | id, sku, name, category_name, is_active |
| `inventory.category.created` | New category created | id, name, slug, parent_id, depth, path |
| `inventory.category.updated` | Category updated | id, name, slug, parent_id, depth, path |
| `inventory.stock.low` | Available stock <= reorder level | item_id, sku, name, available, reorder_level, warehouse_id |
| `inventory.stock.out` | Available stock reaches zero | item_id, sku, name, available, warehouse_id |
| `inventory.lot.expiring_soon` | Lot approaching expiry date | lot_id, item_id, sku, lot_number, expiry_date, warehouse_id, quantity_remaining |
| `inventory.purchase_order.received` | Purchase order goods received | purchase_order_id, supplier_id, lines, warehouse_id, received_at |
| `inventory.transfer.shipped` | Stock transfer dispatched | transfer_id, source_warehouse_id, destination_warehouse_id, lines, shipped_at |
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
| `logistics.task.assigned` | Task assigned to fleet member | task_id, tracking_code, external_reference, fleet_member_id, status |
| `logistics.task.{status}` | Task status changed | task_id, tracking_code, status, previous_status, source_service |
| `logistics.task.completed` | Delivery completed (PoD submitted) | task_id, tracking_code, external_reference, fleet_member_id |
| `logistics.task.eta_updated` | ETA recalculated for active delivery | task_id, tracking_code, external_reference, eta_minutes, distance_km, rider_lat, rider_lng |

### treasury-api (JetStream, stream: `treasury`)

| Subject | Trigger | Key Payload Fields |
|---------|---------|-------------------|
| `treasury.payment.created` | Payment intent created | intent_id, reference_id, reference_type, amount, currency, payment_method, status |
| `treasury.payment.succeeded` | Gateway callback success | intent_id, reference_id, amount, currency, provider, provider_reference, fee, customer_email |
| `treasury.payment.failed` | Gateway callback failure | intent_id, reference_id, amount, currency, provider, customer_email |
| `treasury.payout.completed` | Payout settlement processed | reference, gross_amount, fee, net_amount, currency, transfer_code, transaction_count |
| `treasury.refund.completed` | Refund processed | intent_id, transaction_id, reference_id, amount, currency, source_service, reason, notification{target=customer} |
| `treasury.settlement.completed` | Merchant settlement batch processed | settlement_id, tenant_id, total_amount, currency, line_count, settled_at |
| `treasury.installment.due` | Installment payment due date approaching | installment_plan_id, installment_id, customer_id, amount, currency, due_date, notification{target=customer} |

### subscriptions-api (JetStream, stream: `subscription`)

| Subject | Trigger | Key Payload Fields |
|---------|---------|-------------------|
| `subscription.created` | New subscription provisioned | tenant_id, plan_code, status, bundle_code, trial_days |
| `subscription.upgraded` | Plan tier increased | tenant_id, new_plan_code, old_plan_id, direction |
| `subscription.downgraded` | Plan tier decreased | tenant_id, new_plan_code, old_plan_id, direction |
| `subscription.cancelled` | Subscription cancelled | tenant_id, reason |
| `subscription.renewed` | Subscription renewed | tenant_id |

### ticketing-api (JetStream, stream: `ticketing`)

| Subject | Trigger | Key Payload Fields |
|---------|---------|-------------------|
| `ticketing.ticket.assigned` | Ticket assigned to agent | ticket_id, ticket_number, subject, agent_id, priority |
| `ticketing.ticket.resolved` | Ticket resolved | ticket_id, ticket_number, subject |

### pos-api (JetStream, stream: `pos`)

| Subject | Trigger | Key Payload Fields |
|---------|---------|-------------------|
| `pos.order.created` | POS order created | order_id, order_number, outlet_id, total_amount, currency, item_count |
| `pos.order.status_changed` | POS order status transition | order_id, order_number, previous_status, new_status |
| `pos.payment.recorded` | Payment recorded against POS order | (planned) |
| `pos.kds.ticket.ready` | KDS ticket marked ready for pickup/serve | ticket_id, station_id, order_id, outlet_id, ready_at |
| `pos.appointment.created` | Appointment scheduled | appointment_id, outlet_id, staff_member_id, customer_id, service_items, start_time, end_time |
| `pos.appointment.completed` | Appointment service completed | appointment_id, outlet_id, staff_member_id, completed_at, total_amount |

---

## Consumers by Service

### notifications-api (Worker Process)

| Consumer | Stream | Subjects | Notifications Triggered |
|----------|--------|----------|------------------------|
| Order Status | `ordering` | `ordering.order.>` | order_placed, order_ready, order_out_for_delivery, order_delivered, order_cancelled, booking_created |
| Fleet Lifecycle | `logistics` | `logistics.fleet.>` | rider_invite, rider_onboarding_approved, rider_suspended |
| Inventory Stock | `inventory` | `inventory.>` | low_stock_alert, stock_out, lot_expiring_soon, purchase_order_received, transfer_shipped, category_created |
| Subscription Lifecycle | `subscription` | `subscription.>` | subscription_created, subscription_upgraded, subscription_downgraded, subscription_cancelled, subscription_renewed |
| Treasury Payments | `treasury` | `treasury.>` | payment_success, payment_failed, payment_receipt, payout_completed, settlement_completed, installment_due |
| Delivery Tasks | `logistics` | `logistics.task.>` | delivery_assigned, delivery_completed, delivery_failed |
| POS Orders | `pos` | `pos.>` | pos_order_ready, pos_payment_receipt, kds_ticket_ready, appointment_created, appointment_completed |
| Ticketing | `ticketing` | `ticketing.>` | ticket_assigned, ticket_resolved |
| Projects | `projects` | `project.>` | project_milestone_reached |
| Auth Welcome | plain NATS | `auth.user.created` | welcome email |
| Auth Password Reset | plain NATS | `auth.user.password_reset.requested` | password_reset email |
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
| POS Sale | `pos.sale.finalized` | Backflush stock, update lot quantities |

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
| Inventory Sync | `inventory.item.created/updated` | Create/update CatalogItem projection (with item_type, compliance flags) |
| Category Sync | `inventory.category.created/updated` | Sync hierarchical categories for catalog |

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
| `notifications-logistics-delivery` | `logistics` | `logistics.task.>` |
| `notifications-pos-orders` | `pos` | `pos.>` |
| `notifications-ticketing` | `ticketing` | `ticketing.>` |
| `notifications-projects` | `projects` | `project.>` |
