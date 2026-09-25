# Online Order Fulfilment

How an order placed on the ordering storefront (guest or signed-in) reaches the outlet, the
kitchen, the counter and the rider, for hospitality, retail and service tenants. Covers the
events between ordering-backend, pos-api, logistics-api, treasury-api and notifications-api,
the payment options, the acceptance policy, who may act at each stage, and per-tenant app naming.

Last reviewed 2026-09-25.

## Services and ownership

| Concern | Owner | Notes |
|---|---|---|
| The order, its status, payment state, customer messages | ordering-backend | Source of truth for the online order |
| Outlet record, KDS tickets, kitchen chits, counter queue, appointments | pos-api | Mirror order keyed by `online:<order id>` (OrderLink) |
| Delivery task, rider assignment, proof of delivery, rider cash | logistics-api | Task keyed by the order id (external reference) |
| Stock | inventory-api | Reserved at checkout, consumed at the end, released on cancel |
| Money | treasury-api | Payment intents; pay-on-collection settled with method and reference |
| Messages | notifications-api | Email, SMS, WhatsApp (approved Meta templates), web push |

## Order lifecycle

1. **Checkout.** Prices are re-derived server side, promo codes applied, stock reserved (BOM and
   modifiers exploded). The order is `pending`. A 6-digit hand-over code is generated: the rider
   proof-of-delivery code for delivery orders, the counter collection code for pickup orders
   (bookings and dine-in get none).
2. **Payment.** Online payment (STK, card, wallet) marks it paid through the treasury callback.
   Pay-on-collection and manual M-Pesa orders do not wait for payment.
3. **Acceptance.** Tenant setting `orders.auto_accept` (ordering service config, default
   `false`):
   - Manual (default): ordering publishes `ordering.order.awaiting_acceptance`. pos-api creates the
     POS record held in status `awaiting_acceptance` (no KDS tickets, no chit) and the online
     orders queue rings until someone accepts or rejects.
   - Automatic: ordering confirms at once (online payments when paid).
   Accepting (POS queue or ordering staff dashboard) confirms the order in ordering, which
   publishes `ordering.order.confirmed`; pos-api releases the held record: KDS tickets routed by
   category or override, kitchen chit printed. Rejecting cancels in ordering, which refunds a
   prepaid order, releases stock and tells the customer.
4. **Scheduled orders** are handed to the outlet by the scheduler at the prep window.
5. **Kitchen.** KDS Start publishes `pos.online_order.preparing`; ordering moves the order to
   `preparing` and the customer sees it. All tickets ready (or the counter's **Ready** for
   printer-only kitchens and retail packing) publishes `pos.kds.order.ready`; ordering moves it to
   `ready` and either tells a pickup customer, or for delivery creates the logistics task.
6. **Pickup hand-over.** The counter asks for the collection code (POS keeps only a salted hash;
   a missing code needs a recorded reason), takes any money due, and marks it collected:
   `pos.online_order.collected`, ordering completes the order, settles cash on collection and
   consumes the stock reservation.
7. **Delivery.** The task is auto-assigned to the nearest rider (`logistics.auto_assign_enabled`),
   assigned by a dispatcher, or taken by a rider from **Open jobs**
   (`logistics.rider_self_claim_enabled`, default on; one conditional update so only one rider
   wins). `logistics.task.picked_up` moves the order to `out_for_delivery`; the rider submits proof
   of delivery with the customer's code and, for pay on delivery, the cash or M-Pesa code taken.
   `logistics.task.completed` delivers the order, settles it with the method used and consumes
   stock. An outlet delivering with its own staff marks it delivered from the POS queue instead.
8. **Cancellation** at any point releases stock, refunds a prepaid order, voids the POS record
   and its tickets, and cancels the delivery task.

Service bookings (salon, barber, garage) create a POS appointment instead of a takeaway ticket;
the storefront hides booked slots (public `GET /{tenant}/pos/appointments/booked-slots`).

## Payment options

| Option | Offered when | Confirmed by | Settled |
|---|---|---|---|
| Integrated M-Pesa / card | treasury gateway active | treasury callback | platform collected |
| Manual M-Pesa (customer pays Till/Paybill, types the code) | outlet has a Till/Paybill/Pochi | counter verifies the code against the business M-Pesa message | treasury settled as `mpesa_manual` with the code |
| Pay on delivery / at the counter | treasury `cod` gateway active | at hand-over or proof of delivery | treasury settled with `cod` (cash) or `mpesa_manual` + code |

Manual M-Pesa uses `payment_method = mpesa` with `metadata.payment_channel = mpesa_manual` and
`metadata.mpesa_code`; a code can be used once per tenant.

## Rider cash on delivery

A rider holds the business's cash from pay-on-delivery drop-offs until they hand it in. The
ledger is the cash proofs of delivery without `metadata.remitted_at`; the amount owed is the
order's COD amount (change given is not owed).

| Endpoint | Who |
|---|---|
| `GET /{tenant}/riders/me/cash` | the rider |
| `GET /{tenant}/cash/riders` | `logistics.tasks.manage` |
| `POST /{tenant}/cash/riders/{memberId}/remit` `{amount_received, notes}` | `logistics.tasks.manage` |

A hand-in stamps every outstanding cash delivery with one remittance id, the amount expected,
received and any shortfall.

## Who does what

| Stage | Where | Permission | Default roles |
|---|---|---|---|
| Accept / reject | POS online orders queue | `pos.online_orders.change` (or `pos.orders.change`/`manage`) | cashier, waiter, floor supervisor, receptionist, manager |
| Accept / reject | ordering staff dashboard | `ordering.orders.manage` | ordering staff, admin |
| Verify manual M-Pesa | POS queue or dashboard | as above | as above |
| Start / Ready / Served | KDS | `pos.kds.change` | kitchen, bar, barista, manager |
| Ready without KDS, hand over | POS queue | `pos.online_orders.change` | counter roles |
| Assign rider | POS queue or logistics-ui | `pos.online_orders.change` / `logistics.tasks.manage` | counter roles, dispatcher |
| Take an open job, legs, proof of delivery | rider app | the rider's own fleet membership | rider |
| Record rider cash hand-in | logistics-ui Rider Cash | `logistics.tasks.manage` | dispatcher, manager |
| Acceptance policy | ordering settings | ordering config manage | tenant admin |

## Messages

| Event | Customer | Business | Rider |
|---|---|---|---|
| `ordering.order.created` | "We have received your order" (+ delivery or collection code) | | |
| `ordering.order.awaiting_acceptance` / `confirmed` | accepted (on confirmed) | new order alert, once per order (email, WhatsApp) | |
| `ordering.order.for_pickup` | ready at `<outlet>`, show code | | |
| `ordering.order.out_for_delivery` | on its way, rider name, delivery code | | |
| `logistics.task.assigned` | none for ordering orders | | push to the rider's devices, email |

WhatsApp business-initiated messages use approved Meta templates only
(`internal/whatsapp/templatesync/templates.json` in notifications-api); local phone numbers are
sent with the tenant's dial code. Customer-facing logistics emails are sent only when the task
event carries a customer email and the task is not an ordering order.

Rider push uses FCM web push, configured once in notifications-service (see below): the rider app
reads the browser config from `GET /api/v1/push/web-config?tenant=<slug>`, registers its token
(`POST /api/v1/push/tokens`) and notifications-api pushes `logistics/rider_job_assigned`. Until
push is configured, riders rely on the Open jobs list.

## Notification provider scoping

Shared accounts are configured once at platform level (notifications-ui Platform > Providers,
stored under tenant `platform`) and used by every tenant that has not brought its own. A tenant's
own account (notifications-ui Settings > Providers) is used as a whole. Credentials are never
mixed across tiers.

| Channel | Tenant's own account when | Otherwise | Tenant may still set on the platform account |
|---|---|---|---|
| Email SMTP | it saved a host (not overridden by a platform-managed value) | platform DB settings, then env | sender address |
| Email Brevo | it saved an API key | platform key | sender address and name |
| SMS Africa's Talking | it saved an API key (with its own username) | platform account | sender ID |
| WhatsApp | it saved a phone number id | the platform's number | (tenant number is sent with the platform system-user token, the Tech Provider model) |
| Push FCM | it saved a complete Firebase project (service account + web values) | platform project, then env `PROVIDERS_FCM_*` | nothing |

Push has two halves from the same Firebase project: the service account (secret, encrypted at
rest, only used server side) and the web values (API key, sender id, app id, VAPID key), served
publicly by `/push/web-config` so no app carries Firebase build settings. Device tokens FCM
reports as unregistered are deactivated automatically.

## Per-tenant app names and icons

Tenant metadata `service_branding` in auth-api names each app for the tenant:

```json
"service_branding": {
  "ordering": {"name": "Urban Eats", "short_name": "Urban Eats", "icon_url": "data:image/svg+xml;base64,..."},
  "rider": {"name": "Loft Riders"}
}
```

Keys: `ordering`, `rider`, `pos`, `logistics` (any lowercase key is accepted). Fields: `name`
(60), `short_name` (24), `tagline`, `theme_color` (hex), `icon_url` (https or uploaded image;
SVGs are checked for scripts, event handlers and external references). A `null` or blank entry
removes the override. Tenant updates clear the shared `tenant:<slug>` cache.

Edited in Accounts > My Organisation > Branding > App Names and Icons. Used by:

- ordering-frontend: manifest, page title and iOS title, header, install prompt, and square PNG
  icons generated at `/{slug}/app-icon/{size}` (any and maskable) from the icon or logo, with an
  initials fallback; ordering-backend `/config` returns `app_name`, `app_short_name`,
  `app_icon_url`, `app_theme_color`.
- rider-app, pos-ui, logistics-ui: manifest name, label, icon and theme colour; rider-app and
  logistics-ui headers.
- auth-ui sign-in: "Continue to <app>" from the OAuth `client_id` in `return_to`.

Without an entry the app is "<Business> <Service>" with the business logo.
