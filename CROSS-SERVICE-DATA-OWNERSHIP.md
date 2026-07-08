# Cross-Service Data Ownership & User Management

**Last updated:** 2026-06-07 — Retail-POS revamp: loyalty SoT → pos-api (ordering becomes a client); treasury gains AR `CustomerBalance` + AP `VendorBalance` (supplier opening/advance), supplier rebate credit notes, and a `cost_center` dimension; inventory gains a `StockBreakdown` (bulk→unit) op; pos services module gains `RepairJob`. See `/.claude/plans/_audit-parts/retail-pos-audit-and-roadmap-2026-06-07.md`. **Prior:** March 2026 — Multi-industry revamp (March 25): inventory-api gains hierarchical categories with icon field, compliance fields, custom fields, lot tracking, bundles, suppliers, purchase orders, stock transfers, warranties. pos-api gains KDS, appointments, staff/commission, serial tracking; POS catalog sync handler enriched with full compliance/physical/service fields from inventory events (inventory_item_id FK, item_type, requires_age_verification, barcode, duration_minutes). Use case is per-outlet (not per-tenant) — a single tenant can have outlets with different use cases. logistics-api gains dynamic pricing rules, rider shifts. treasury-api gains split payments, settlements, reconciliation, installments. Tenant schema reduced across all 7 downstream services (March 24). Services store only minimal tenant reference (id, slug, name, status, use_case, sync_status, last_sync_at). Branding, contact info, and subscription data fetched from auth-api Redis cache (cache v0.2.0) with JWT TTL. No data duplication; each service stores only its own data; references via REST, events, or gRPC.

## Overview

This document is the **canonical** definition of data ownership across Codevertex microservices. It ensures **no data duplication**: each service stores only the data it owns; any need for another service’s data is satisfied by **reference IDs** and access via **REST**, **events (NATS)**, or **gRPC** — never by copying entities into another service’s database.

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
| **CRM / Customer Relationship** | `marketflow-api` | Leads, Contacts, Deals, Pipelines, Accounts, Activities, Tasks, Campaigns, Funnels, NurtureSequences, ChatSessions, Meetings, CustomFields, AI Agents | REST (GET), `crm_contact_id` refs, NATS events |
| **Product Master** | `inventory-api` | Items (SKUs), BOM, Recipes, **Units**, **Categories** (hierarchical), **Variants**, **CustomFieldDefinition/Value**, **InventoryLot**, **VariantAttribute**, **Bundle/BundleComponent**, **Supplier**, **PurchaseOrder/Line**, **StockTransfer/Line**, **Warranty** | REST (GET), `sku`/`product_id` refs |
| **Sales Catalog** | `pos-api` | Catalogs, Modifier Groups, Local Prices, **KDSStation/KDSTicket**, **Appointment**, **StaffMember**, **SerialNumberLog**, **CommissionRecord** | Sync from Inventory, NATS `CatalogUpdated` |
| **Orders (Online)** | `ordering-backend` | Carts, Online Orders, **Catalog Projection**, Booking/Appointment refs (loyalty now read/written via pos-api, not owned here — 2026-06-07) | Projection of Global Catalog, NATS Events |
| **Logistics** | `logistics-api` | Riders, Tasks, Proof of Delivery, **PricingRule**, **RiderShift** | REST, Webhooks, `rider_id` refs |
| **Payments** | `treasury-api` | Intents, Transactions, Refunds, Taxes, **PaymentSplit**, **Settlement/SettlementLine**, **ReconciliationRun**, **InstallmentPlan/Installment** | REST, Webhooks, `payment_intent_id` refs |
| **Subscription plans, tenant entitlements** | subscriptions-api | All services: check plan before using inventory, POS, logistics, treasury, etc. |
| **Notification templates, delivery status, channel preferences** | notifications-api | Other services: trigger via events or API; store only `notification_message_id` etc. if needed |
| **IoT devices, telemetry, alerts** | iot-service-api | inventory-api (e.g. temperature/compliance), notifications; optional POS/inventory hardware integration |
| **Loyalty & Referrals** | `pos-api` | LoyaltyProgram, LoyaltyAccount, LoyaltyTransaction, **Referral** — keyed on `crm_contact_id`; ordering-backend is a client (2026-06-07) | REST, `pos.loyalty.*` events |
| **AR / AP balances** | `treasury-api` | **CustomerBalance** (credit sale, ageing, statements), **VendorBalance** (supplier opening/advance, ageing), supplier **rebate** credit notes, **cost_center** (2026-06-07) | REST, `customer_balance`/`vendor_balance` refs |
| **Procurement breakdown** | `inventory-api` | **StockBreakdown** (bulk→retail uom-explode; cost carried parent→child) (2026-06-07) | event `inventory.stock.broken_down` |
| **Repair / job-card** | `pos-api` (services module) | **RepairJob** (intake→diagnosis→parts→settle); parts from inventory, payment via treasury (2026-06-07) | REST, `pos.repair.*` events |
| **Financial documents** | `treasury-api` | **Invoices, Quotations, proforma, Sales Credit-Notes (eTIMS), AP vendor credit-notes** — pos NEVER duplicates these (2026-06-09) | S2S create from pos context (return→`/s2s/{t}/invoices/{id}/create-credit-note`; cart→quotation) |

### Retail POS Revamp — ownership deltas (2026-06-07)
Driven by the retail-POS competitive audit (`/.claude/plans/_audit-parts/retail-pos-audit-and-roadmap-2026-06-07.md`). Deltas to the canonical model:
1. **Loyalty SoT = pos-api** (was split pos + ordering). pos owns LoyaltyProgram/Account/Transaction + new **Referral**, keyed on `crm_contact_id` so online (ordering) + in-store (pos) earn into ONE balance. **ordering-backend stops owning loyalty** and calls pos loyalty endpoints (keeps refs only).
2. **AR/AP balances = treasury-api**: new **CustomerBalance** (credit-sale posting, ageing 0-30/31-60/61-90/90+, statements, dunning) and **VendorBalance** (AP subledger). **Supplier opening/advance balances live in treasury AP, NOT on inventory `supplier`** (inventory supplier stays a procurement master reference).
3. **Supplier rebates = treasury** vendor credit notes (inventory may flag a rebate accrual on PO lines). **cost_center** = treasury dimension on expense/journal lines.
4. **Breakdown (bulk→unit) = inventory-api** `StockBreakdown` (multi-UoM explode carrying cost parent→child; IAS-2 FIFO/moving-average), distinct from BOM production.
5. **Financial documents = treasury-api (2026-06-09)**: invoices, **quotations**, **sales credit-notes** (eTIMS VAT reversal, `invoice_type=credit_note` via `invoicing.CreateCreditNote`). pos NEVER defines a parallel quotation/credit-note entity (one was built + discarded) — it CREATES them via S2S from a pos context (return → `POST /s2s/{tenant}/invoices/{id}/create-credit-note`; "Save as Quotation" from a cart → treasury quotation S2S). **UI rule: pos-ui LINKS to treasury-ui / inventory-ui / marketflow-ui pages (external redirect; the target service enforces its own RBAC) — never recreate another service's pages; only the pos↔service integration ACTION lives in pos-ui.**
5. **Repair/job-card = pos-api services module** (not a new service, not ticketing-service).
6. New/used events: `pos.loyalty.earned`, `pos.loyalty.redeemed`, `pos.referral.rewarded`, `inventory.stock.broken_down`, `inventory.goods_receipt.posted` → treasury (GR/IR accrual + 3-way match), `treasury.customer_balance.updated`, `pos.repair.*`.
7. CRM unchanged: marketflow remains customer SoT; pos adds in-register contact search/create via marketflow S2S; **Customer Groups = marketflow segments**.

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

### CRM Service (marketflow-api)
**Owns** (single source of truth for all customer relationship data):
- **Lead** — potential customers/recruits captured via ads, funnels, chat, manual entry
- **Contact** — known customers/partners with full profile, lifecycle stage, account link
- **Deal / Opportunity** — sales pipeline records with value, stage, probability, close date
- **Pipeline / PipelineStage** — tenant-configurable sales pipeline with ordered stages
- **Account** — company/organization-level records linked to contacts
- **Activity** — unified timeline of all interactions per entity (emails, calls, notes, meetings, SMS, WhatsApp)
- **Task** — follow-up reminders and action items linked to leads/contacts/deals
- **Campaign** — Meta/TikTok/Google/manual marketing campaigns
- **Funnel** — multi-step landing pages for lead capture and qualification
- **NurtureSequence** — automated multi-channel follow-up sequences (email/SMS/WhatsApp)
- **ChatSession** — AI chatbot conversations (web widget, WhatsApp, funnel)
- **ScheduledMeeting** — Cal.com meeting bookings linked to leads/contacts
- **CustomFieldDef / CustomFieldValue** — per-tenant extensible fields for leads/contacts/deals
- **LeadScoringRule** — configurable rule-based lead scoring conditions
- **CustomAgent / AgentRun** — tenant-defined AI automation agents and their execution logs
- **ShortLink** — URL shortener for tracking

**Other services MUST NOT store** lead profiles, contact email/phone/name, deal records, activity logs, pipeline data, or any CRM entity. They store only `crm_contact_id` (nullable UUID) as a reference FK.

**Cross-service reference pattern:**
- `pos-api` LoyaltyAccount and Appointment: add nullable `crm_contact_id` UUID FK
- `ordering-backend` Order: add nullable `crm_contact_id` UUID FK
- `treasury-api` PaymentIntent: add nullable `crm_contact_id` UUID FK
- `ticketing-api` Ticket: add nullable `crm_contact_id` and `crm_lead_id` UUID FKs
- All FKs are **nullable** — existing records function without CRM; linkage is opt-in

**Integration pattern (no duplication):**
- `marketflow-worker` subscribes to `ordering.order.created`, `pos.sale.finalized`, `treasury.payment.succeeded`, `pos.appointment.completed` — when `crm_contact_id` is set on the event payload, logs an Activity on the CRM contact timeline
- Other services query contact details via `GET /api/v1/contacts/{crm_contact_id}` on marketflow-api using `X-API-Key: INTERNAL_SERVICE_KEY` when they need contact name/email for display
- `GET /api/v1/contacts/{id}/360` on marketflow-api aggregates cross-service data (orders from ordering-backend, payments from treasury-api, loyalty from pos-api) in one response

**Events published by marketflow-api (via NATS outbox):**
- `crm.lead.created`, `crm.lead.qualified`, `crm.lead.converted`
- `crm.contact.created`, `crm.contact.updated`, `crm.contact.enriched`
- `crm.deal.created`, `crm.deal.stage_moved`, `crm.deal.won`, `crm.deal.lost`
- `crm.activity.logged`
- `crm.task.created`, `crm.task.overdue`
- `crm.agent.action_taken`

**Other services reference**: `crm_contact_id`, `crm_lead_id`; contact/deal data via marketflow-api REST when needed.

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
- **Hospitality SERVICE items** — Items with `use_case` ∈ {`HOSPITALITY_ROOM`, `HOSPITALITY_FACILITY`, `CONFERENCE`, `SALON_SERVICE`, `AMENITY`} are the **master** for room-types, conference halls, facilities, and amenities, including their rates (via `ItemPricing`), `meal_plan` (RO/BB/HB/FB/AI), occupancy basis and capacity. pos-api references these by `inventory_item_id` and projects price via catalog sync. (NEW — June 2026)
- **Conference / event packages** — modeled as `Bundle` (parent SERVICE Item) + `BundleComponent` rows (meal periods, AV, stationery, consumables, sessions). `package_type` ∈ {`ROOM_RATE_PLAN`, `DDR`, `RDR`, `HALF_BOARD`, `FULL_BOARD`, `HALL_HIRE_ONLY`, `SERVICE_SESSIONS`}; `price_basis` ∈ {`per_delegate_per_day`, `per_person_sharing`, `flat`, `per_session`}. This **replaces** any pricing/package authoring in pos-api (`Room.rate_per_night`, `Facility.rate_per_session`, `ServicePackage.price`). (NEW — June 2026)
- **ItemPricing outlet override** — `outlet_id` (nullable) + `tier_basis` (nightly/per_session/per_delegate_per_day/peak/off_peak) for outlet-level and seasonal rate tiers. (NEW — June 2026)

**Other services do not store** items, units, recipes, lots, suppliers, purchase orders, **or hospitality rates/packages**; they reference by `inventory_item_id`, `sku`, `recipe_id`, `lot_id`, `supplier_id` and get data via REST (e.g. GET /items, GET /units, GET /recipes, GET /lots, GET /suppliers) or events. Ordering and POS may keep a **read-only projection/cache** of catalog synced from inventory.

**Other services reference**: `inventory_item_id`, `inventory_sku`, `recipe_id`, `reservation_id`, `lot_id`, `supplier_id`, `purchase_order_id`, `transfer_id`, `warranty_id`; catalog and units via inventory-api APIs or sync.

---

### Ordering-Service (ordering-backend)
**Owns** (order lifecycle and cafe context only):
- Online orders (now with appointment_id, staff_preference_id, preferred_carrier), order_items (now with item_type, service_start_time, duration_minutes), carts, cart_items
- Cafe/outlet context (cafes, outlets) as used by ordering
- Promo codes, redemptions (loyalty accounts/transactions are now owned by **pos-api**; ordering reads/writes via pos loyalty API — see 2026-06-07 retail revamp)
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
- **LoyaltyProgram / LoyaltyAccount / LoyaltyTransaction / Referral** — in-store + cross-channel loyalty **SoT**, keyed on `crm_contact_id`; ordering-backend reads/writes via pos loyalty API and does not own a second balance (2026-06-07)
- **RepairJob** (services module) — repair/job-card lifecycle (intake→diagnosis→parts→settle); parts referenced from inventory, settled via treasury (2026-06-07)
- **Hotel operations** — `Room`/`RoomGuest` (guest stay, check-in/out), `RoomBooking` (multi-room group header), `RoomFolioItem` (folio charges), `RoomAmenity` assignment, `Facility`/`FacilityBooking`, `HousekeepingTask`. These hold **operational state only** (status, occupancy, guest data); rates and room-type/facility/amenity masters live in inventory-api (referenced via `inventory_item_id`). (NEW — June 2026)
- **EventBooking (BEO)** — conference/wedding/party bookings referencing an inventory `Bundle` (`inventory_bundle_id`) for the package master. (NEW — June 2026)
- **MealEntitlement** — meal-card/voucher issuance & redemption per delegate × conference-day × meal-period (one-time `issued→redeemed` with validity window). The *template* of included meals lives on the inventory Bundle; redemption backflushes meal BOM to inventory. (NEW — June 2026)
- **Happy-hour promotions** — `Promotion`/`PromotionRule` extended with `promo_kind=happy_hour`, daily `window_start`/`window_end`, `days_of_week`, `outlet_id`, `auto_apply`, and category/item scoping that **references inventory category ids** (synced via `inventory.category.*`). Happy hour is a sales-pricing operation on the projection, not a product master. (NEW — June 2026)
- **Guest ID document** — `RoomGuest.id_document_url` stores only an **object-storage key** (PII; never the blob). The file lives in object storage with presigned, expiring access.

**Does not own**: Units, items, recipes, **room-type/facility/amenity masters, conference/event package definitions, or any hospitality rate** — obtained from inventory-api via REST or sync. Guest contact identity converges on marketflow-api CRM (`crm_contact_id`). Stock consumption reported to inventory-api via REST (POST /consumption) or event (`pos.sale.finalized`).

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
- **CustomerBalance** — AR running balance, ageing, statements, **credit-sale** posting (keyed on `crm_contact_id`) (2026-06-07)
- **VendorBalance** — AP running balance, supplier **opening/advance balance**, ageing, statements; supplier master stays in inventory-api (2026-06-07)
- **Supplier rebate / vendor credit notes** + **cost_center** dimension on expense/journal lines (2026-06-07)
- **Quotations / QuotationLines** — sales quotations and line items (from ERP finance)
- **Expenses / ExpenseCategories / ExpenseClaims** — expense tracking and claims (from ERP finance)
- **TaxCodes / TaxPeriods / TaxFilings** — tax configuration and compliance (from ERP finance)
- **eTIMSDevices / eTIMSInvoices** — KRA eTIMS device registration and invoice transmission (from ERP finance)
- **Budgets / BudgetLines** — budget management (from ERP finance)
- **ApprovalWorkflows / ApprovalSteps / ApprovalRecords** — approval workflows for financial entities (from ERP finance)
- **VendorBills / VendorBillLines** — vendor bill management (from ERP finance)
- **BankAccounts / BankStatements / BankStatementLines / ReconciliationRules** — banking and reconciliation (from ERP finance)
- **Forecasts / ForecastDataPoints** — cash flow forecasting (from ERP finance)
- **EquityTransactions / DividendDeclarations / ShareholderReports** — equity management (from ERP finance)

**Other services** store only payment references and minimal snapshots (e.g. amount at payment time); they do not duplicate treasury entities.

**Other services reference**: `payment_intent_id`, `payment_id`, `payout_id`, `settlement_id`, `installment_plan_id`, `quotation_id`, `expense_id`, `budget_id`, `vendor_bill_id`, `bank_account_id`; payment status via webhooks or events.

#### Quotation ↔ CRM Customer Integration Pattern (May 2026)

Quotations in treasury-api reference CRM customers from marketflow-api. The ownership rule:

- **CRM (marketflow-api) owns** all customer/contact data: name, email, phone, address, company, lifecycle stage, custom fields.
- **treasury-api stores** a nullable `customer_id` UUID FK (the CRM Contact UUID) on `Quotation`. It also caches `customer_name` and `customer_email` as snapshot strings directly on the quotation row for display/export without requiring a live CRM lookup.

**Integration pattern for quotation creation:**
1. UI calls `GET /api/v1/marketflow/{tenant}/contacts?search=<query>` (S2S with `X-API-Key: INTERNAL_SERVICE_KEY`) to search CRM contacts.
2. User selects a contact → UI populates `customer_id` (UUID), `customer_name`, `customer_email` in the form.
3. UI posts `POST /api/v1/{tenant}/quotations` with all three fields.
4. treasury-api stores them; `customer_id` is the authoritative FK.

**Access pattern for display:** treasury-api returns `customer_name` and `customer_email` from the quotation row (snapshot). For live CRM data (phone, address, 360 view), call `GET /api/v1/marketflow/{tenant}/contacts/{customer_id}`.

**Services that must NOT store customer master data:** treasury-api, pos-api, ordering-backend, logistics-api, inventory-api. These services store only `crm_contact_id` (nullable UUID FK) and optional snapshot fields (`customer_name`, `customer_email`) for audit/display.

#### Financial Documents ↔ Cross-Service Integration Patterns (May 2026)

All financial document types (Quotation, Invoice, Proforma Invoice, Credit Note, Sales Order, Delivery Challan, Payment Receipt) in treasury-api follow these data ownership rules for cross-service references:

**Line Items ↔ Inventory-API (Product Catalog)**
- **inventory-api owns** all product master data: item name, SKU, description, unit of measure, cost price, tax rate, images, variants.
- **treasury-api stores** a nullable `item_id` UUID FK (inventory-api `inventory_item_id`) and `sku` string on each line item.
- `rate` (unit price), `tax_rate`, and `description` on the line item are **snapshot values** captured at the time the document is created — they do not change if the inventory item is later updated.
- **Integration pattern:** treasury-ui calls `GET /api/v1/{tenant}/inventory?search=<query>` (inventory-api) to search products in the line items combobox. Selecting a product auto-fills rate and tax_rate from the current inventory master; these values are then submitted as part of the document and stored as snapshots.
- **treasury-api must NOT** mirror or sync inventory items locally. Line item `item_id` is the authoritative reference; live product data is fetched from inventory-api on demand.

**Delivery Challan Conversion ↔ Logistics-API**
- **logistics-api owns** all delivery task data: task lifecycle, proof of delivery, rider assignment, tracking, dispatch notes.
- When a quotation is converted to a delivery challan, treasury-api calls `POST /api/v1/{tenant}/tasks` on logistics-api (S2S with `X-API-Key: INTERNAL_SERVICE_KEY`) with the quotation line items, shipping details, and source document reference.
- **treasury-api stores** the returned `logistics_task_id` UUID on the quotation as a reference.
- treasury-api does **NOT** store delivery task lifecycle, rider details, proof of delivery, or tracking status. These are fetched from logistics-api when needed.
- NATS event `treasury.quotation.delivery_challan_created` is published with `{quotation_id, logistics_task_id, tenant_id}`.

**Sales Order Conversion ↔ Ordering-Backend**
- **ordering-backend owns** all sales order/online order data including order lifecycle, fulfillment state, and customer-facing order status.
- When a quotation is converted to a sales order, treasury-api calls `POST /api/v1/{tenant}/orders` on ordering-backend (S2S with `X-API-Key: INTERNAL_SERVICE_KEY`) with the quotation line items, customer reference, and source quotation ID.
- **treasury-api stores** the returned `order_id` UUID on the quotation as a reference.
- treasury-api does **NOT** store order lifecycle, fulfillment, or cart data. These are owned by ordering-backend.
- NATS event `treasury.quotation.converted_to_order` is published with `{quotation_id, order_id, tenant_id}`.

**Payment Receipts ↔ Banking Accounts**
- Bank accounts (for the "Deposited To" field in Payment Receipts) are owned by **treasury-api** itself (`BankAccounts` entity). No cross-service reference needed — treasury-api queries its own bank accounts.
- `GET /{tenant}/banking/accounts` is the endpoint treasury-ui calls to populate the "Deposited To" dropdown in the RecordPaymentModal.

**Financial Document Public Share Links**
- Public share pages (`/q/{token}`, `/i/{token}`) serve document data via a `public_token` UUID field stored on each document row.
- Public endpoints (`GET /api/v1/public/quotations/{token}`, `GET /api/v1/public/invoices/{token}`) do not require authentication and are rendered as Next.js server components.
- PDF/CSV/XLSX exports for authenticated users use blob download (TruLoad pattern): `GET /{tenant}/quotations/{id}/pdf` returns bytes; the client creates an object URL and triggers `<a>.click()`. Public pages use direct `<a href>` to treasury-api public endpoints.

**Document Email/WhatsApp Delivery ↔ Notifications-API**
- treasury-api does **NOT** directly send email or WhatsApp messages. On `SendQuotation` / `SendInvoice`, treasury-api publishes NATS events:
  - `treasury.quotation.sent` — `{quotation_id, tenant_id, recipient_email, public_token}`
  - `treasury.invoice.sent` — `{invoice_id, tenant_id, recipient_email, public_token}`
- notifications-api subscribes to these events and delivers the email/WhatsApp using the appropriate template (`quotation_sent`, `invoice_sent`).
- For payment reminders: treasury-ui "Send Reminder" action triggers `POST /{tenant}/invoices/{id}/send-reminder` → treasury-api publishes `treasury.invoice.reminder_sent` → notifications-api delivers.

**Summary of Cross-Service References on Financial Documents:**

| Field on Document | Owner Service | Reference Type |
|-------------------|---------------|----------------|
| `customer_id` | marketflow-api | Nullable UUID FK + `customer_name/email/phone` snapshot |
| line item `item_id` | inventory-api | Nullable UUID FK + rate/tax_rate/description snapshot |
| line item `sku` | inventory-api | String snapshot (authoritative via `item_id`) |
| `logistics_task_id` (on quotation after DC conversion) | logistics-api | Nullable UUID FK |
| `order_id` (on quotation after SO conversion) | ordering-backend | Nullable UUID FK |
| `bank_account_id` (on payment receipt) | treasury-api (self) | Internal FK |

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
| Room/RoomGuest/RoomBooking/RoomFolioItem, Facility/FacilityBooking, EventBooking, MealEntitlement, HousekeepingTask (hotel **operations**) | **pos-api** | inventory-api, ordering-backend (only refs e.g. `room_guest_id`, `event_booking_id`) |
| Room-type/facility/amenity masters & **rates**, conference/event **package** definitions (room/facility pricing must NOT be authored in pos-api) | **inventory-api** | pos-api stores only `inventory_item_id`/`inventory_bundle_id` refs + synced price snapshot |
| PricingRule, RiderShift | **logistics-api** | ordering-backend, pos-api, treasury-api |
| Rider/fleet member profiles, KYC, vehicles, shifts | **logistics-api** | ordering-backend (only `rider_id`, `logistics_task_id` refs in order_assignments) |
| Tenant and user identity (full profile, sessions, MFA, OAuth) | **auth-api** | ordering-backend, pos-api (only `tenant_id`, `user_id` refs; minimal JIT cache allowed for FK only) |
| Quotations, quotation lines | **treasury-api** | erp (remove after migration), ordering-backend, pos-api |
| Expenses, expense categories, expense claims | **treasury-api** | erp (remove after migration), ordering-backend, pos-api |
| Tax codes, tax periods, tax filings, eTIMS devices, eTIMS invoices | **treasury-api** | erp (remove after migration), pos-api, inventory-api |
| Budgets, budget lines | **treasury-api** | erp (remove after migration), ordering-backend, pos-api |
| Approval workflow config for financial entities (approval workflows, steps, records) | **treasury-api** | erp (generic approvals module stays for non-financial workflows; financial approval config migrates to treasury) |
| Vendor bills, vendor bill lines | **treasury-api** | erp (remove after migration), inventory-api |
| Bank accounts, bank statements, bank statement lines, reconciliation rules | **treasury-api** | erp (remove after migration) |
| Forecasts, forecast data points | **treasury-api** | erp (remove after migration) |
| Equity transactions, dividend declarations, shareholder reports | **treasury-api** | erp (remove after migration) |
| Leads, Contacts, Deals, Pipeline stages, Accounts, CRM Activities, CRM Tasks | **marketflow-api** | ordering-backend, pos-api, treasury-api, inventory-api, logistics-api (store only `crm_contact_id` nullable FK) |

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
| Inventory Service | `inventory.bundle.created/updated` | POS | Project conference/event packages & rate plans into POS catalog |
| Inventory Service | `inventory.lot.expiring_soon` | Notifications | Expiry alerts to tenant admins |
| Inventory Service | `inventory.purchase_order.received` | Notifications | PO receipt confirmation |
| Inventory Service | `inventory.transfer.shipped` | Notifications | Transfer dispatch notification |
| POS Service | `pos.sale.finalized` | Inventory | Backflush / consumption |
| POS Service | `pos.kds.ticket.ready` | Notifications | KDS ticket ready alert |
| POS Service | `pos.appointment.created/completed` | Notifications, Ordering | Appointment lifecycle sync |
| POS Service | `hotel.booking.created` | Notifications | Multi-room booking confirmation |
| POS Service | `conference.event.booked` | Notifications | Conference/event (BEO) booked |
| POS Service | `conference.mealcard.issued` | Notifications | Delegate meal cards generated |
| POS Service | `conference.mealcard.redeemed` | Inventory, Notifications | Meal voucher redeemed → backflush meal BOM |
| POS Service | `pos.inventory.consumption.failed` | Notifications | Backflush failure alert (retry queue) |
| Ordering Service | `ordering.booking.created` | POS, Notifications | Service booking created |
| Treasury Service | Payment webhooks (HTTP) | Ordering | Update order payment status |
| Treasury Service | `treasury.settlement.completed` | Notifications | Settlement batch notification |
| Treasury Service | `treasury.installment.due` | Notifications | Installment due reminder |
| Treasury Service | `treasury.invoice.created` | Notifications | Invoice created notification |
| Treasury Service | `treasury.invoice.paid` | Notifications | Invoice payment confirmation |
| Treasury Service | `treasury.invoice.overdue` | Notifications | Overdue invoice alert |
| Treasury Service | `treasury.expense.submitted` | Notifications | Expense claim submitted for review |
| Treasury Service | `treasury.expense.approved` | Notifications | Expense claim approved notification |
| Treasury Service | `treasury.quotation.sent` | Notifications | Quotation email/WhatsApp delivery (recipient_email, public_token) |
| Treasury Service | `treasury.quotation.accepted` | Notifications | Quotation accepted notification |
| Treasury Service | `treasury.quotation.delivery_challan_created` | Logistics, Notifications | Delivery challan created from quotation (logistics_task_id ref) |
| Treasury Service | `treasury.quotation.converted_to_order` | Ordering, Notifications | Quotation converted to sales order (order_id ref) |
| Treasury Service | `treasury.invoice.sent` | Notifications | Invoice email/WhatsApp delivery (recipient_email, public_token) |
| Treasury Service | `treasury.invoice.reminder_sent` | Notifications | Payment reminder delivery |
| Treasury Service | `treasury.etims.transmitted` | Notifications | eTIMS transmission confirmation |
| Treasury Service | `treasury.budget.approved` | Projects, ERP | Budget approved — update project/ERP budget refs |
| Treasury Service | `treasury.budget.rejected` | Projects, ERP | Budget rejected — notify requestor |
| Subscriptions Service | `subscription.billing.renewal` | Treasury | Process subscription renewal payment |
| Subscriptions Service | `subscription.billing.overage` | Treasury | Process overage charges |
| Subscriptions Service | `subscription.billing.proration` | Treasury | Process proration adjustment |
| ERP Service | `erp.payroll.processed` | Treasury | Create payroll payment journal entries |
| ERP Service | `erp.purchase_order.received` | Treasury | Create vendor bill from received PO |
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
| treasury-service | `treasury.invoice.created` | notifications-service (invoice notification) |
| treasury-service | `treasury.invoice.paid` | notifications-service (payment confirmation) |
| treasury-service | `treasury.invoice.overdue` | notifications-service (overdue alert) |
| treasury-service | `treasury.expense.submitted` | notifications-service (expense review) |
| treasury-service | `treasury.expense.approved` | notifications-service (expense approved) |
| treasury-service | `treasury.quotation.sent` | notifications-service (quotation email/WhatsApp delivery) |
| treasury-service | `treasury.quotation.accepted` | notifications-service (quotation accepted) |
| treasury-service | `treasury.quotation.delivery_challan_created` | logistics-service (task created from quotation), notifications-service |
| treasury-service | `treasury.quotation.converted_to_order` | ordering-backend (order created from quotation), notifications-service |
| treasury-service | `treasury.invoice.sent` | notifications-service (invoice email/WhatsApp delivery) |
| treasury-service | `treasury.invoice.reminder_sent` | notifications-service (payment reminder) |
| treasury-service | `treasury.etims.transmitted` | notifications-service (eTIMS confirmation) |
| treasury-service | `treasury.budget.approved` / `rejected` | projects-service, erp (budget lifecycle) |
| subscription-service | `subscription.billing.renewal` | treasury-service (renewal payment) |
| subscription-service | `subscription.billing.overage` | treasury-service (overage charges) |
| subscription-service | `subscription.billing.proration` | treasury-service (proration adjustment) |
| erp-service | `erp.payroll.processed` | treasury-service (payroll journal entries) |
| erp-service | `erp.purchase_order.received` | treasury-service (vendor bill creation) |

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

