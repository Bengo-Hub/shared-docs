# REVENUE-AGNOSTIC EQUITY FRAMEWORK
## Percentage-Based Entitlement Across All Services

**Refined Principle**: Equity holders' entitlement is defined by **percentage of service revenue**, not by the specific pricing model (subscription plans, per-transaction charges, licensing, service charges, or commission-based revenue).

---

## CORE CONCEPT: SERVICE REVENUE AGGREGATION

### Revenue Is Revenue
Every income-generating service generates revenue through whatever mechanism it chooses:
- **Subscriptions-service**: Tiered SaaS plans (2.5K–12.5K KES/month)
- **Logistics**: Per-delivery commission (8%)
- **Ordering**: Per-order commission (5%)
- **POS**: Per-transaction charge (4%)
- **TruLoad**: Per-weighing fee (10%)
- **Inventory**: Per-unit licensing ($5/month/location)
- **ERP**: Module licensing (varies)
- **Cafe**: Integrated with Ordering
- **ISP-Billing**: 5% commission on billing cycles

**The mechanism doesn't matter.** What matters is:
```
For ANY service X with revenue $R:
  → Gross Revenue: $R (collected regardless of model)
  → Platform Royalty (owed to Core Pool): $R × royalty_rate
  → Service Net Revenue: $R × (1 - royalty_rate)
  → Equity Holder Y's Entitlement: $R × equity_percentage_for_service
```

---

## TREASURY LEDGER STRUCTURE (SIMPLIFIED)

### Single Source of Truth: Revenue by Service

```sql
-- Core revenue aggregation (NEW)
CREATE TABLE service_revenue_summary (
    month DATE,
    service_id TEXT (e.g., 'ordering', 'logistics', 'truload'),
    gross_revenue_cents BIGINT,  -- SUM of all payments for service this month
    transaction_count INT,
    updated_at TIMESTAMP
);

-- Example:
-- 2026-04-30 | ordering | 50000000 | 1523 → $500,000 in April orders
-- 2026-04-30 | logistics | 30000000 | 892 → $300,000 in April deliveries
-- 2026-04-30 | subscriptions | 20000000 | 40 → $200,000 in April subscriptions
```

### Platform Royalty Calculation (AUTOMATIC)

```
For each service monthly:
  platform_royalty = gross_revenue_cents × royalty_rate / 100

  ORDER_royalty_04_2026 = 50000000 × 5% = 2500000 (25K)
  LOGISTICS_royalty_04_2026 = 30000000 × 8% = 2400000 (24K)
  SUBSCRIPTIONS_royalty_04_2026 = 20000000 × 12% = 2400000 (24K)
  
  Total Core Pool this month: 7300000 (73K KES)
```

### Equity Holder Entitlement (IMMEDIATE)

```sql
-- Link equity holders to services + percentage
CREATE TABLE equity_entitlements (
    id UUID PRIMARY KEY,
    holder_id UUID,
    service_id TEXT,
    equity_percentage NUMERIC(5,2), -- e.g., 3.50 = 3.5%
    vesting_start_date DATE,
    vesting_end_date DATE,
    is_active BOOLEAN,
    created_at TIMESTAMP
);

-- Example:
-- holder_1 | 'ordering' | 3.0% (gets 3% of all ordering revenue)
-- holder_1 | 'logistics' | 2.0% (gets 2% of all logistics revenue)
-- holder_2 | 'truload' | 5.0% (gets 5% of all weighing revenue)
```

### Monthly Equity Payout Calculation

```
For holder_1 with 3.0% 'ordering':
  April ordering gross revenue = 50M cents = $500K
  holder_1 April entitlement = 500000 × 3.0% = 15000 USD
  
For holder_1 with 2.0% 'logistics':
  April logistics gross revenue = 30M cents = $300K
  holder_1 April entitlement = 300000 × 2.0% = 6000 USD
  
Total holder_1 April payout = 15000 + 6000 = 21000 USD
```

---

## EQUITY HOLDER PORTAL: TRANSPARENCY FRAMEWORK

**What equity holders need to see** (per service, per month):

```
SERVICE: Logistics
├─ Gross Revenue (April 2026): $300,000
├─ Your Equity %: 2.0%
├─ Your Entitlement: $6,000
├─ Platform Royalty Paid to Core: $24,000
├─ Logistics Operating Costs: $150,000
├─ Logistics Net (after platform royalty): $276,000
└─ Ledger Detail:
   ├─ Task #1234: $15 → Your share: $0.30
   ├─ Task #1235: $18 → Your share: $0.36
   ├─ [... 890 more tasks ...]
   └─ Total: $300,000 → Your share: $6,000

SERVICE: Ordering
├─ Gross Revenue (April 2026): $500,000
├─ Your Equity %: 3.0%
├─ Your Entitlement: $15,000
├─ Platform Royalty Paid to Core: $25,000
├─ Ordering Operating Costs: $200,000
├─ Ordering Net (after platform royalty): $475,000
└─ Ledger Detail:
   ├─ Order #O5678: $42 → Your share: $1.26
   ├─ Order #O5679: $38 → Your share: $1.14
   ├─ [... 1,520 more orders ...]
   └─ Total: $500,000 → Your share: $15,000

MONTH TOTAL (April 2026):
├─ Total Entitlements: $21,000
├─ Tax Withholding (10%): -$2,100
├─ Payout Method: M-Pesa
├─ Payout Status: Completed (2026-04-30)
└─ Reference: APR_2026_EQUITY_PAYOUT
```

---

## IMPLEMENTATION: SERVICE-AGNOSTIC REVENUE TRACKING

### Step 1: Standardized Revenue Event (ALL Services)

Every service must publish a **unified event** after processing payment:

```go
type RevenueEvent struct {
    EventID           string              `json:"event_id"`        // UUID
    Timestamp         time.Time           `json:"timestamp"`
    ServiceID         string              `json:"service_id"`      // 'ordering', 'logistics', 'pos', etc.
    TenantID          string              `json:"tenant_id"`       // Who paid
    Amount            int64               `json:"amount_cents"`    // 100000 = $1,000
    Currency          string              `json:"currency"`        // 'USD', 'KES'
    TransactionID     string              `json:"transaction_id"`  // Payment reference
    SourceType        string              `json:"source_type"`     // 'order', 'delivery', 'subscription_renewal', 'pos_sale'
    SourceID          string              `json:"source_id"`       // e.g., order_id, task_id
    TransactionFee    int64               `json:"transaction_fee_cents"` // Gateway fee
}

Subject (NATS): "revenue.{service}.received"
// Examples:
// revenue.ordering.received
// revenue.logistics.received
// revenue.truload.received
// revenue.subscriptions.received
```

### Step 2: Treasury Aggregator Worker

```go
// treasury-service/cmd/worker/revenue_aggregator.go
func (w *Worker) AggregateMonthlyRevenue(ctx context.Context) {
    // For each service, sum all revenue_events from this month
    for _, service := range []string{"ordering", "logistics", "pos", "truload", ...} {
        query := `
            SELECT 
                service_id,
                DATE_TRUNC('month', timestamp),
                SUM(amount_cents) as gross_revenue_cents,
                COUNT(*) as transaction_count
            FROM revenue_events
            WHERE service_id = $1 AND DATE_TRUNC('month', timestamp) = $2
            GROUP BY service_id, DATE_TRUNC('month', timestamp)
        `
        // Store result in service_revenue_summary table
        // Publish: treasury.revenue_aggregated event
    }
}
```

### Step 3: Equity Payout Calculator

```go
// treasury-service/internal/handler/equity_payout.go
func (h *EquityHandler) CalculateMonthlyPayouts(ctx context.Context, month time.Time) {
    // 1. Get service_revenue_summary for month
    // 2. For each equity_entitlement:
    //    a. Fetch gross_revenue from service_revenue_summary
    //    b. Calculate: gross_revenue × equity_percentage
    //    c. Create equity_payout ledger entry
    // 3. Aggregate payouts by holder
    // 4. Apply tax withholding (KRA rates)
    // 5. Create transfer instructions (M-Pesa, Bank)
    // 6. Publish: treasury.equity_payout.created event
}
```

### Step 4: Ledger Structure (Double-Entry)

```
WHEN: Payment received for Ordering ($1,000)
  DEBIT:  bank / payment_gateway (1,000) [cash in]
  CREDIT: service_revenue.ordering (1,000) [ordering earned]

WHEN: Platform Royalty accrued (Ordering $50, 5%)
  DEBIT:  service_revenue.ordering (50) [deduction]
  CREDIT: core_pool_royalty_payable (50) [owed to core pool]

WHEN: Equity payout (holder_1 gets 3% of $1,000)
  DEBIT:  equity_liability (30) [obligation to holder]
  CREDIT: (when paid): bank / mpesa_transfer (30)
```

---

## MULTI-TIER REFERRAL REVENUE (ALIGNED WITH EQUITY)

### Referral Generates Revenue Too

When holder_1 refers tenant_B who signs up:

```
tenant_B subscribes to Ordering (generates revenue stream)
  ↓
referral.converted event published
  ↓
Treasury calculates referral benefit:
  - Option A: 3% equity stake in Ordering → holder_1 now gets 3% of ALL Ordering revenue from tenant_B going forward
  - Option B: Lump-sum bonus → $500 one-time
  - Option C: 10% commission on tenant_B's monthly revenue for 24 months
  
All tracked in service_revenue_summary by tenant/referrer
```

---

## CONFIGURATION EXAMPLE: SERVICES & EQUITY HOLDERS

### Service Configuration (Treasury Admin)

```json
{
  "services": [
    {
      "id": "ordering",
      "name": "Ordering Service",
      "revenue_model": "commission",  // documentation only
      "commission_rate": 5,           // documentation only
      "platform_royalty_rate": 5,
      "is_active": true,
      "holders": [
        { "holder_id": "uuid_alice", "equity_percentage": 3.0, "vesting": "2026-01-01 to 2029-01-01" },
        { "holder_id": "uuid_bob", "equity_percentage": 2.0, "vesting": "2026-06-01 to 2029-06-01" }
      ]
    },
    {
      "id": "logistics",
      "name": "Logistics Service",
      "revenue_model": "commission",  // documentation only
      "commission_rate": 8,           // documentation only
      "platform_royalty_rate": 8,
      "is_active": true,
      "holders": [
        { "holder_id": "uuid_charlie", "equity_percentage": 5.0, "vesting": "2026-02-01 to 2029-02-01" }
      ]
    },
    {
      "id": "subscriptions",
      "name": "Subscriptions (Core)",
      "revenue_model": "saas_plans",  // documentation only
      "platform_royalty_rate": 12,
      "is_active": true,
      "holders": [
        { "holder_id": "uuid_dev_team", "equity_percentage": 15.0, "vesting": "2025-01-01 to 2030-01-01" }
      ]
    }
  ]
}
```

---

## SCHEMA SUMMARY (UNIFIED)

```sql
-- Revenue fact table (immutable)
CREATE TABLE revenue_events (
    id UUID PRIMARY KEY,
    service_id TEXT NOT NULL,
    tenant_id UUID NOT NULL,
    amount_cents BIGINT NOT NULL,
    currency TEXT DEFAULT 'KES',
    transaction_id TEXT UNIQUE,
    source_type TEXT,
    source_id TEXT,
    transaction_fee_cents BIGINT DEFAULT 0,
    occurred_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ON revenue_events(service_id, DATE_TRUNC('month', occurred_at));

-- Monthly aggregates (pre-calculated)
CREATE TABLE service_revenue_summary (
    month DATE NOT NULL,
    service_id TEXT NOT NULL,
    gross_revenue_cents BIGINT DEFAULT 0,
    transaction_count INT DEFAULT 0,
    updated_at TIMESTAMP,
    PRIMARY KEY (month, service_id)
);

-- Equity entitlement configuration
CREATE TABLE equity_entitlements (
    id UUID PRIMARY KEY,
    holder_id UUID NOT NULL,
    service_id TEXT NOT NULL,
    equity_percentage NUMERIC(5,2) NOT NULL,
    vesting_start_date DATE,
    vesting_end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    UNIQUE(holder_id, service_id)
);

-- Calculated monthly payouts
CREATE TABLE equity_payouts (
    id UUID PRIMARY KEY,
    holder_id UUID NOT NULL,
    month DATE NOT NULL,
    service_id TEXT,
    gross_revenue_cents BIGINT,
    equity_percentage NUMERIC(5,2),
    payout_amount_cents BIGINT,
    tax_withholding_cents BIGINT,
    net_payout_cents BIGINT,
    status TEXT DEFAULT 'pending', -- pending, processing, completed, failed
    payout_method TEXT, -- mpesa, bank, etc.
    payout_reference TEXT,
    created_at TIMESTAMP,
    paid_at TIMESTAMP,
    PRIMARY KEY (holder_id, month, service_id)
);
```

---

## EXAMPLE CALCULATION: APRIL 2026 PAYOUTS

### Services Revenue (Actual)
```
Ordering gross:     $500,000 (1,523 orders)
Logistics gross:    $300,000 (892 deliveries)
TruLoad gross:      $100,000 (50 weighings)
Subscriptions gross: $200,000 (40 plan renewals)
───────────────────────────────
Total Platform:   $1,100,000
```

### Platform Royalty (Core Pool)
```
Ordering: $500K × 5% = $25,000
Logistics: $300K × 8% = $24,000
TruLoad: $100K × 10% = $10,000
Subscriptions: $200K × 12% = $24,000
───────────────────────────────
Core Pool Total: $83,000

Core Pool Dividend (to auth/notifications/subscriptions developers):
  Auth-service team: $41,500 (50% of pool)
  Notifications team: $24,900 (30% of pool)
  Subscriptions team: $16,600 (20% of pool)
```

### Equity Holders Payouts
```
alice (3% Ordering, 2% Logistics):
  Ordering: $500K × 3% = $15,000
  Logistics: $300K × 2% = $6,000
  Subtotal: $21,000
  Tax withholding (10% KRA): -$2,100
  Payout: $18,900 (M-Pesa)

bob (2% Ordering, 1% TruLoad):
  Ordering: $500K × 2% = $10,000
  TruLoad: $100K × 1% = $1,000
  Subtotal: $11,000
  Tax withholding (10% KRA): -$1,100
  Payout: $9,900 (Bank)

charlie (5% Logistics):
  Logistics: $300K × 5% = $15,000
  Subtotal: $15,000
  Tax withholding (10% KRA): -$1,500
  Payout: $13,500 (M-Pesa)

dev_team (15% Subscriptions):
  Subscriptions: $200K × 15% = $30,000
  Subtotal: $30,000
  Tax withholding (15% KRA - corp): -$4,500
  Payout: $25,500 (Bank)
───────────────────────────────
Total Payouts: $67,800 (April 2026)
```

---

## EQUITY HOLDER PORTAL: DASHBOARD TABS

### 1. SERVICE REVENUE BREAKDOWN (Current Month)

| Service | Gross Revenue | Your % | Your Entitlement | Vesting Status |
|---------|---|---|---|---|
| Ordering | $500,000 | 3.0% | **$15,000** | 60% vested (24 mo) |
| Logistics | $300,000 | 2.0% | **$6,000** | 75% vested (36 mo) |
| **MONTH TOTAL** | — | — | **$21,000** | — |
| Tax Withholding (KRA) | — | — | **-$2,100** | — |
| **NET PAYOUT** | — | — | **$18,900** | — |

### 2. HISTORICAL LEDGER (Last 12 Months)

```
Month    | Ordering | Logistics | TruLoad | TOTAL | Status
────────────────────────────────────────────────────────
Apr 2026 | $15,000  | $6,000    | –       | $21,000 | ✅ Paid
Mar 2026 | $12,000  | $5,000    | –       | $17,000 | ✅ Paid
Feb 2026 | $10,500  | $4,500    | $500    | $15,500 | ✅ Paid
...      | ...      | ...       | ...     | ...     | ...
May 2025 | $8,000   | $3,000    | –       | $11,000 | ✅ Paid
```

### 3. VESTING SCHEDULE

```
Service: Ordering
├─ Grant Date: 2025-12-01
├─ Grant %: 3.0%
├─ Vesting: 3 years (36 months)
├─ Cliff: 12 months
├─ Status: 17 months vested (47%)
├─ Next Cliff: 2026-12-01 (unlock another 25%)
└─ Projected Full Vesting: 2028-12-01

Service: Logistics
├─ Grant Date: 2025-09-01
├─ Grant %: 2.0%
├─ Vesting: 3 years (36 months)
├─ Cliff: 6 months
├─ Status: 31 months vested (86%)
├─ Next Milestone: Fully vested 2028-09-01
└─ Projected: ~2 months remaining
```

### 4. TAX & COMPLIANCE

```
YTD Summary (Jan–Apr 2026):
├─ Total Entitlements: $71,400
├─ Total Payouts: $64,260
├─ Total Tax Withheld: $7,140
├─ KRA Withholding Rate: 10%
├─ YTD Pin Reference: KRA-2026-[...]
└─ Compliance: ✅ All withholding remitted to KRA

Download Tax Report (for accountant):
  → PDF: Annual Income Statement
  → PDF: Tax Withholding Certificate (Form E1)
  → CSV: Monthly transaction ledger
```

---

## KEY BENEFITS OF THIS FRAMEWORK

✅ **Service-Agnostic**: Works with ANY revenue model (commission %, fixed fees, subscriptions, licensing)  
✅ **Transparent**: Equity holders see exactly which $$ they're entitled to from each service  
✅ **Scalable**: Adding new services requires only config change (service_id, revenue_model, holders)  
✅ **Auditable**: Every $ tracked from collection → aggregation → platform royalty → equity payout  
✅ **Flexible**: Equity % can differ per service (5% Logistics, 3% Ordering, 15% Subscriptions)  
✅ **Vesting-Ready**: Support cliff + gradual unlock regardless of dollar amounts  
✅ **Tax-Compliant**: KRA withholding calculated per holder, service, tax rules  

---

## SUMMARY: EQUITY = PERCENTAGE, NOT MODEL

| Aspect | Old Thinking | New Framework |
|--------|---|---|
| Equity Calculation | "What % of service revenue?" | Revenue in → aggregate by service → % entitlement |
| Revenue Model | Matters for configuration | Irrelevant for calculation |
| Portal Display | By revenue model type | By **service name + $$ + your %** |
| Holder Setup | Complex per-model rules | Simple: service_id + equity_percentage + vesting |
| Tax Reporting | Model-specific logic | Single: gross – tax = net per month |
| Scalability | Hard (new models = rework) | Easy (new service = add config row) |

---
