# Codevertex Africa — Revised Pricing Model & Strategy Report (2026)

> Supersedes the flat `CODEVERTEX AFRICA POS SYSTEMS PRICING MODEL` document. Covers all product
> lines and services, introduces the **PAYG (pay-as-you-go) service charge** for micro-businesses,
> separates **PAYG from prepaid credit bundles**, and maps platform features to tiers with the exact
> entitlement codes used by `subscriptions-api`.

---

## 1. Executive summary

The original document priced only the three POS product lines (POS / Duka / Dawa) on a monthly +
one-time-license + implementation + annual-support basis. Benchmarking against the 2026 Kenyan POS
market shows:

- **Monthly fees** are already competitive and were largely kept.
- **One-time licenses (90k–350k)** sat **above** the Kenyan market band of **KES 30k–150k** and have
  been **repositioned down** (value-competitive posture).
- The market has a large **micro-business segment** that cannot afford a subscription or a license but
  will pay a **small per-sale commission** (the way they already pay M-Pesa/Paystack). We introduce a
  **PAYG service charge of 1% of each sale, floored at KES 2 and capped at KES 50**, which **replaces**
  the subscription for that tenant.
- Inconsistent annual-support figures were normalized (the old Hospitality T3 support of 18k was below
  its own T2 of 32k — a typo).

The platform's feature depth (eTIMS, hotel/folio, multi-station KDS, recipe/BOM, AR/AP + double-entry
ledger, offline-sync PWA, integrated CRM) **exceeds** typical Loyverse / Kyte / Pesapal-RACK feature
sets — this is the competitive advantage to lead with in the higher tiers.

---

## 2. Market research (Kenya, 2026)

| Segment | Typical monthly (KES) | Notes |
|---|---|---|
| Budget / freemium | 0 – 2,000 | Loyverse, Kyte (free/freemium, ad-supported or feature-limited) |
| Starter cloud POS | 2,000 – 5,000 | 1 user, sales, basic inventory, receipts |
| Standard | 5,000 – 10,000 | 3–5 users, eTIMS, M-Pesa, reports, loyalty |
| Professional | 10,000 – 25,000 | 10+ users, multi-branch, analytics |
| Enterprise | 25,000+ | unlimited users, API, dedicated support |

- **One-time licenses:** cluster at **KES 30,000–150,000** (e.g. PharmaPOS 45k–150k one-time, no monthly).
- **Setup / implementation:** KES 5,000–30,000 (ours already in band).
- **Hardware:** KES 35,000–200,000; Pesapal POS terminal ~KES 12,000.

### Kenyan payment-gateway fees (the benchmark for our service charge)

| Provider | Fee |
|---|---|
| M-Pesa Till (merchant) | ~0.5% |
| Paystack (local) | 1.5% + flat |
| IntaSend / Flutterwave | ~1.5% – 3.8% |
| Pesapal | 3% – 5.5% (highest) |

Our **1% software commission sits below the gateway fee the merchant already pays**, so the all-in cost
to a micro-merchant stays reasonable while the platform earns predictably. This is defensible and
market-aware.

*Sources: cuteprofit (restaurant POS cost 2026), eliteteqpos (POS cost guide 2026), iosoftsolutions,
posmart, nids, medsoftwares (pharmacy 2026), creativekigen & transfer.co.ke (gateway fees), pesapal.*

---

## 3. Billing-model taxonomy (read this first)

These are **distinct** billing models. Conflating them (especially PAYG vs credit bundles) has caused
confusion; keep them separate.

| Model | What the customer pays | When | Mechanism in code |
|---|---|---|---|
| **Subscription** | Recurring tier fee (monthly/annual) | Each cycle | `subscription_plan.base_price`, `billing_cycle` |
| **One-time license** | Perpetual access fee | Once | `billing_cycle = ONE_TIME`, `IsPerpetual` |
| **Implementation / setup** | One-off onboarding | Once at start | `subscription_plan.setup_fee` / `cmd/seed/setup_fees.go` |
| **PAYG service charge** | **% commission on their own sales** | Per transaction | `service_charge_plan` (PERCENTAGE), `billing_mode = service_charge` |
| **Prepaid credit bundles** | **Consumable top-ups** (SMS / WhatsApp / AI) | Bought upfront, drawn down per unit | notifications `TenantCredit` ledger (TOPUP/DEDUCTION); `ai_credits_monthly` |
| **Overage** | Pay-as-you-go on metered throughput over a subscription cap | At renewal | `allow_overage` + `overage_charge` |

### PAYG vs Prepaid credit bundles — the critical distinction

- **PAYG service charge** is a **percentage of the tenant's sales/transactions**. It is the tenant's
  *primary billing relationship* (replaces subscription). Collected by netting the platform's cut at
  settlement (`PaymentIntent.service_charge_amount` / `net_amount` in treasury).
- **Prepaid credit bundles** are **consumables** (SMS, WhatsApp messages, AI chat credits) bought in
  advance and consumed per unit. They are **add-ons available to ANY tenant** — a subscription tenant, a
  one-time-license tenant, or a PAYG tenant can all buy SMS/AI credits. They are **not** a percentage of
  sales and are **not** a billing mode.

> **Cleanup item:** `SC_MARKETFLOW_AI_CREDIT` is currently modelled as a `service_charge_plan` but
> behaves as a consumable credit. It should be presented and sold as a **prepaid AI-credit pack**
> (consistent with the notifications `TenantCredit` SMS/WhatsApp model and the `ai_credits_monthly`
> catalog limit), not as a PAYG commission. See §8.

---

## 4. PAYG service charge — design

**Chosen structure (Paystack-style): 1% of sale · minimum KES 2 · capped at KES 50 per transaction.**

| Parameter | Value | Rationale |
|---|---|---|
| Percentage | **1.0%** | Below every Kenyan gateway fee; merchant's all-in stays sane |
| Floor (min) | **KES 2** | Tiny sales still cover platform processing |
| Cap (max) | **KES 50** | Large baskets aren't over-charged; predictable ceiling |
| Waiver | sales under ~KES 100 effectively pay only the KES 2 floor | Protects very small tickets |
| Applies to | POS transactions (extendable to retail/pharmacy via the same plan) | |

**Worked examples:** KES 80 sale → KES 2 (floor). KES 500 sale → KES 5 (1%). KES 2,000 sale → KES 20.
KES 10,000 sale → KES 50 (cap). KES 50,000 sale → KES 50 (cap).

### PAYG payment-method restriction (so the platform can actually collect)

A merchant on PAYG pays nothing up front, so the platform's only revenue is the per-sale commission.
**Cash and offline/manual payments cannot be auto-deducted** — they would let commission leak. Therefore
**PAYG tenants are restricted to platform-collectable online rails**:

- ✅ Allowed: **platform-routed M-Pesa**, **card via the platform gateway (Paystack)** — methods where
  treasury nets `service_charge_amount` at settlement.
- ❌ Hidden for PAYG tenants: **cash**, **manual**, **room-charge**, **cash-on-delivery (COD)**, and
  **on-account / credit** tenders.

This is enforced at the gateway-list chokepoint (treasury) and defended again at the POS/ordering tender
list. A subscription or one-time-license tenant is unaffected — they keep all payment methods, because
the platform's revenue from them does not depend on intercepting each sale.

---

## 5. Revised pricing — POS product lines

> **Micro / PAYG** rows have **no monthly fee** — the tenant pays only the 1% service charge (min 2 / cap
> 50) and is restricted to online payment methods. Implementation is optional.

### 5.1 Codevertex POS (Hospitality — hotels, restaurants, bars)

| Tier | Monthly | Implementation | One-time License | Annual Support |
|---|---|---|---|---|
| **Micro / PAYG** | 1% (min 2 / cap 50) | 0 – 5,000 | — | — |
| Starter | 2,500 | 10,000 | 45,000 | 9,000 |
| Professional | 5,500 | 18,000 | 95,000 | 19,000 |
| Hospitality | 9,500 | 30,000 | 150,000 | 30,000 |

### 5.2 Codevertex Duka (General retail — shops, supermarkets, hardware)

| Tier | Monthly | Implementation | One-time License | Annual Support |
|---|---|---|---|---|
| **Micro / PAYG** | 1% (min 2 / cap 50) | 0 – 5,000 | — | — |
| Starter | 2,500 | 10,000 | 45,000 | 9,000 |
| Professional | 5,500 | 18,000 | 90,000 | 18,000 |
| Enterprise | 9,500 | 30,000 | 150,000 | 30,000 |

### 5.3 Codevertex Dawa (Pharmacy — chemists, pharmacies, dispensaries)

Priced slightly higher for compliance depth (batch/expiry, PPB controls, NHIF claims).

| Tier | Monthly | Implementation | One-time License | Annual Support |
|---|---|---|---|---|
| **Micro / PAYG** | 1% (min 2 / cap 50) | 0 – 6,000 | — | — |
| Starter | 3,500 | 12,000 | 55,000 | 11,000 |
| Professional | 6,500 | 22,000 | 110,000 | 22,000 |
| Enterprise | 11,000 | 35,000 | 165,000 | 33,000 |

### 5.4 Hardware bundles (optional — customer can BYOD)

Unchanged from the original document (Mobile Starter 13–15k, Tablet Bundle 25–30k, Retail Pro 40–50k,
Pharmacy Pro 60–75k, Hospitality Pro 75–100k).

---

## 6. Pricing — all other services

These services are already tiered in `subscriptions-api`; the values below are the published, value-
competitive reference (reconcile with `cmd/seed/plans_<svc>.go`). Each also has a PAYG option where a
transaction/fee stream exists.

| Service | Starter | Growth / Pro | Enterprise / Pro+ | PAYG option |
|---|---|---|---|---|
| **Ordering** (storefront + delivery) | 2,500 | 6,000 | 12,500 | 5% of order value (`SC_ORDERING_5PCT`), 3% high-volume |
| **Inventory** (standalone WMS) | 2,000 | 4,500 | 9,000 | — |
| **Treasury / Finance** (invoicing, AR/AP, eTIMS) | 2,500 | 6,000 | 12,000 | — |
| **Logistics** (fleet / dispatch) | 3,000 | 7,000 | 14,000 | 7% of delivery fees (`SC_LOGISTICS_7PCT`) |
| **ERP** (HR, payroll, procurement) | — | 15,000 | 30,000+ | — (implementation-heavy) |
| **MarketFlow** (CRM / ads / AI) | 3,000 | 7,500 | 15,000 | Ads 5% (`SC_MARKETFLOW_ADS`) + AI credit packs (§8) |
| **TruLoad** (weighbridge) | 4,000 | 9,000 | — | 10% of weighing/fine txns (`SC_TRULOAD_10PCT`) |
| **ISP Billing** | 3,500 | 8,000 | 16,000 | — |
| **Projects & Invoicing** | 2,500 | 8,000 | — | — |

**Bundles** (`POS_SUITE_*`, `POWERSUITE_*`) remain available and combine product lines at a discount.

---

## 7. Feature → tier mapping (core POS vs competitive differentiators)

Codes in `code` font are the **exact entitlement codes** in `subscriptions-api`
`cmd/seed/feature_catalog.go`, so gating is real and enforceable.

### 7.1 Core POS — included in EVERY tier, including Micro / PAYG

`pos_terminal`, `order_management`, `receipt_printing`, `daily_reports`, `shift_reports`, `mpesa_pos`
(M-Pesa Till), basic inventory deduction (`basic_inventory_access`), cash drawer, single outlet, basic
treasury (`basic_treasury_access`). These are the non-negotiable point-of-sale essentials.

### 7.2 Competitive differentiators by tier

| Tier | Hospitality (POS) | Retail (Duka) | Pharmacy (Dawa) |
|---|---|---|---|
| **Starter** | + `loyalty_program` (basic), `table_management` | + `loyalty_program`, `barcode_scanning` | + `etims_integration`, `batch_expiry_tracking`, `prescription_management` |
| **Professional** | + `kds`, bill-splitting, recipe/BOM, `etims_integration`, `invoice_generation`, supplier mgmt & POs, `multi_cashier` | + real-time stock, low-stock alerts, supplier lists, `etims_integration`, sales analytics | + `patient_history`, `insurance_claims` (NHIF), PPB audit reports, `multi_cashier` |
| **Enterprise / Hospitality** | + `hotel_module` (reception, check-in/out, room inventory, charge-to-room, guest folio), `conference_events`, `multi_outlet`, `advanced_analytics`, `api_access`, `offline_sync`, `priority_support` | + `multi_outlet`, consolidated reporting, `advanced_analytics`, `api_access`, `priority_support` | + `multi_outlet`, consolidated reporting, `advanced_analytics`, `api_access`, label-printer integration, `priority_support` |

### 7.3 Competitive-advantage call-outs (vs Loyverse / Kyte / Pesapal-RACK)

eTIMS / KRA compliance, hotel & guest-folio module, multi-station KDS, recipe/BOM costing, full AR/AP +
double-entry ledger, offline-first PWA with auto-sync, integrated CRM (MarketFlow), and pharmacy
batch/expiry + NHIF claims. Lead with these in Professional/Enterprise sales.

---

## 8. Prepaid credit bundles (separate from PAYG)

Consumables, available to **any** tenant regardless of billing mode:

| Bundle | Unit price | Ledger |
|---|---|---|
| SMS | ~KES 1 / SMS (provider cost + platform margin) | notifications `TenantCredit` (type=SMS) |
| WhatsApp | per-message | notifications `TenantCredit` (type=WHATSAPP) |
| AI chat credits | KES 10 / credit | `ai_credits_monthly` allowance + prepaid top-up pack |

Sold as **TOPUP** transactions and drawn down via **DEDUCTION** as messages/credits are consumed. These
must **not** be modelled as PAYG service charges.

---

## 9. Subscription-gating correctness (data-sync entitlement)

Gating historically applied only at the HTTP/API layer. Cross-service **event consumers** wrote data into
their own schema **without checking entitlements**, so blocked-feature data (KDS tickets, eTIMS invoice
numbers, inventory availability) could still land for an un-entitled tenant.

**Fix:** event consumers now check the tenant's entitlements (via the subscriptions S2S
`GetEntitlements`) before writing, and **drop** (Ack without writing) when the corresponding feature is
not entitled. Demo / platform-owner / `service_charge` tenants remain exempt. Identity-provisioning
consumers (outlet → warehouse/outlet projection) stay ungated.

| Synced data | Required feature |
|---|---|
| Inventory stock → POS catalog availability | `basic_inventory_access` |
| Ordering status → POS KDS tickets | `kds` |
| Treasury eTIMS → POS order tax fields | `etims_integration` |
| Treasury payments → POS / ordering order status | `basic_treasury_access` |
| Inventory item → ordering catalog override | `basic_inventory_access` |

---

## 10. Implementation status & references

- **Pricing data** lives in `subscriptions-api` seeds: `cmd/seed/plans_pos_lines.go` (the three POS
  product lines), `cmd/seed/service_charges.go` (`SC_POS_MICRO_1PCT` PAYG), `cmd/seed/feature_catalog.go`
  (pharmacy feature codes), and the per-service `plans_*.go`.
- **Gating-sync fix** lives in the POS and ordering event consumers.
- **PAYG payment restriction** lives in `treasury-api` gateway listing + POS/ordering tender lists.
- The subscriptions UI (`subscriptions-ui/src/app/plans/page.tsx`) is catalog-driven and renders new
  plans automatically by plan-code prefix.

*All figures in KES. Tier values are the recommended, tunable reference; adjust in the seed files and
re-run the seed (must be warning-free) to publish.*
