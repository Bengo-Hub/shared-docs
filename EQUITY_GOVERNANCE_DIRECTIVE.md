# EQUITY GOVERNANCE & REVENUE ARCHITECTURE DIRECTIVE
## Codevertex Africa Limited — Formal Specification

**Date**: April 28, 2026  
**Scope**: All microservices and frontends  
**Compliance**: Kenya Companies Act, Data Protection Act, Financial Reporting Standards  

---

## EXECUTIVE DIRECTIVE

Codevertex must transition from a single-tier revenue model to a **dual-tier governance system**:
1. **Income-Generating Services** → Direct equity ownership by business operators and investors
2. **Platform Core Services** → Developer equity via **Infrastructure Royalty** dividend pool

This directive mandates implementation across **four critical workstreams** with specific technical requirements tied to existing services.

---

## SECTION 1: SERVICE CATEGORIZATION & INTERNAL LICENSING MODEL

### A. Income-Generating Services (Direct Equity)
These services directly manage tenant business operations and generate recurring revenue:

| Service | Type | Current Status | Revenue Model |
|---------|------|---|---|
| **treasury-api/ui** | Financial Hub | ✅ Production | Ledger + settlement fees |
| **TruLoad** (.NET) | Weighbridge/Scaling | ✅ Production | Per-transaction fees (10% commission) |
| **Subscriptions** (Go) | Tenant Management | ✅ MVP+ | Tiered plans ($50-$500/month) |
| **Logistics** (Go) | Order Fulfillment | ✅ Active | 7% commission on orders |
| **Ordering** (Go) | e-Commerce Platform | ✅ Active | 3-5% commission |
| **cafe-website** (Next.js) | Restaurant POS | ✅ Active | 2% commission |
| **POS** (Go) | Point of Sale | ✅ Active | 2% per transaction |
| **Inventory** (Go) | Stock Management | ✅ Active | Per-tenant licensing |
| **ERP** (Python) | Enterprise Resource | ✅ Active | Per-module licensing |
| **ISP-Billing** (Node) | Internet/Broadband | ✅ Active | 5% commission |
| **Marketflow** (Go) | Marketplace | ⚠️ Planned | Commission-based |
| **Projects** (Go) | Project Management | ✅ Active | Per-team licensing |
| **IoT-Service** (Go) | Device Management | ✅ Active | Per-device licensing |

### B. Platform Core Services (Infrastructure Royalty Pool)
These services provide essential infrastructure; developers receive equity via dividend:

| Service | Purpose | Current Status |
|---------|---------|---|
| **auth-service** (Go) | Identity & Access | ✅ Production |
| **subscriptions-service** (Go) | Tenant/Plan Management | ✅ MVP+ |
| **notifications-service** (Go) | Event Notifications | ✅ Production |

### C. Supporting Services
Order management, logistics dispatch, IoT integration—operate as utilities integrated into income services.

---

### Internal Licensing Model (ILM) — Revenue Sharing

**Mechanism**: Each income-generating service pays an **Infrastructure Royalty** to a **Core Treasury Pool** based on gross revenue.

```
┌─────────────────────────────────────────────────────┐
│ Tenant Pays $1,000 to Service (e.g., Logistics)    │
└─────────────────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        ▼                                  ▼
    SERVICE REVENUE               ROYALTY TO CORE POOL
    $930 (93%)                     $70 (7% ILM rate)
    │                              │
    ├─► Operational Costs          ├─► Auth-Service Dividend
    ├─► Service Team Payroll       ├─► Notifications Dividend
    ├─► Service-Specific Equity    ├─► Subscriptions Dividend
    └─► Reinvestment               └─► Platform Maintenance Fund
```

**Royalty Rates (By Service Revenue)**:
- **TruLoad**: 10% (mission-critical weighbridge)
- **Logistics**: 8% (complex routing/dispatch)
- **Subscriptions**: 12% (manages all tenants; highest dependency)
- **Ordering**: 5% (medium criticality)
- **Cafe**: 4% (integrated POS)
- **POS**: 4% (integrated POS)
- **Inventory**: 5% (cross-service data)
- **ERP**: 6% (enterprise backbone)
- **ISP-Billing**: 5% (telecom-specific)
- **Others**: 4-6% (baseline)

**Implementation Requirement** (treasury-api):
- Add `royalty_rate` to `service_config` table
- Create monthly `royalty_payable` ledger entries (journal code: `ROYALTY_OUT`)
- Publish `treasury.royalty.accrued` events to trigger Core Pool crediting
- Expose royalty dashboard in treasury-ui showing per-service rates + YTD payouts

---

## SECTION 2: LOGISTICS & TASK ASSIGNMENT TECHNICAL REQUIREMENTS

### Current State
Task assignment payloads in **logistics-service** and **cafe-website** currently lack order context:

```go
// ❌ CURRENT — Missing order_id
type TaskEventData struct {
    TaskID        string                `json:"task_id"`
    AssignedRiderID string             `json:"assigned_rider_id"`
    Status        string                `json:"status"`          // ASSIGNED|IN_TRANSIT|DELIVERED
    PickupLocation map[string]interface{} `json:"pickup_location"`
    DeliveryLocation map[string]interface{} `json:"delivery_location"`
    EstimatedETAMinutes int             `json:"estimated_eta_minutes"`
    // MISSING: order_id, customer_id, service_type
}
```

### Requirement: Mandatory Order Traceability

**Scope**: Every task assignment across **logistics-service**, **cafe-website**, and **ordering-service** must include order context.

**Technical Changes**:

1. **logistics-service** (`logistics-api/internal/platform/events/publisher.go`):
   ```go
   type TaskEventData struct {
       TaskID             string                `json:"task_id"`
       OrderID            string                `json:"order_id"`              // ← NEW
       CustomerID         string                `json:"customer_id"`           // ← NEW
       ServiceType        string                `json:"service_type"`          // ← NEW (e.g., "logistics", "cafe_delivery")
       AssignedRiderID    string                `json:"assigned_rider_id"`
       Status             string                `json:"status"`
       PickupLocation     map[string]interface{} `json:"pickup_location"`
       DeliveryLocation   map[string]interface{} `json:"delivery_location"`
       EstimatedETAMinutes int                  `json:"estimated_eta_minutes"`
       CreatedAt          time.Time             `json:"created_at"`           // ← NEW for audit
       UpdatedAt          time.Time             `json:"updated_at"`           // ← NEW for audit
   }
   ```

2. **cafe-website** (`Cafe/cafe-website/src/pages/orders`):
   - Intercept task assignment form submission
   - Extract `orderId` from route params or order context
   - Inject into payload sent to logistics-service

3. **Event Publishing**:
   - Subject: `logistics.task.assigned` → include `order_id` + `customer_id`
   - Subject: `logistics.task.status_changed` → include `order_id` for audit trail
   - Consumed by: **treasury-api** (revenue reconciliation), **audit-logs** (compliance)

4. **Audit Trail** (New):
   - All `logistics.task.*` events logged to `audit_events` table with `order_id` reference
   - Enable treasury reconciliation: Order → Task → Fulfillment → Settlement

**Timeline**: Week 1 (High Priority)  
**Testing**: Verify order-to-rider-to-delivery chain completeness in logistics dashboard

---

## SECTION 3: MULTI-TIER REFERRAL ARCHITECTURE

### Current Gap
❌ No referral system exists. Subscriptions-service has plan features but no referrer tracking.

### Requirement: Existing Tenant + External Referrer Dual Flow

Referral system must distinguish between:
- **Type A**: Existing tenants referring new tenants → **tiered benefits**
- **Type B**: External (non-tenant) referrers → **full equity + commission options**

### Implementation: auth-service + subscriptions-service + treasury-api

#### 1. Data Schema (auth-service)

```sql
-- Track referrer relationships
CREATE TABLE referral_links (
    id UUID PRIMARY KEY,
    referrer_id UUID NOT NULL REFERENCES users(id),
    referrer_type TEXT NOT NULL, -- 'existing_tenant' | 'external'
    referral_code TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Track referral outcomes
CREATE TABLE referral_conversions (
    id UUID PRIMARY KEY,
    referral_link_id UUID NOT NULL REFERENCES referral_links(id),
    new_tenant_id UUID NOT NULL,
    referred_service TEXT NOT NULL, -- 'subscriptions', 'inventory', etc.
    conversion_date TIMESTAMP,
    benefit_type TEXT, -- 'equity_percentage', 'subscription_discount', 'one_time_bonus'
    benefit_value NUMERIC, -- % for equity, $ for discount/bonus
    benefit_paid BOOLEAN DEFAULT FALSE,
    paid_date TIMESTAMP,
    UNIQUE(referral_link_id, new_tenant_id)
);
```

#### 2. Referral Benefits (By Type)

**Type A: Existing Tenant Refers New Tenant**
- ✅ **Equity Percentage**: 2-5% of referred tenant's revenue for 24 months (e.g., "You get 3% of every payment they make")
- ✅ **Subscription Discount**: 15-25% discount on referrer's next 6 months (e.g., "Get 20% off your plan")
- ✅ **One-Time Bonus**: $50-$500 upon new tenant's first successful payment (service-dependent)

**Type B: External Referrer**
- ✅ All Type A benefits PLUS:
- ✅ **Equity Grant**: 0.1-1% equity stake in the specific service(s) referred (cumulative, capped at 10%)
- ✅ **Revenue Share**: Lifetime 5-10% commission on monthly subscriptions from referred tenants

#### 3. API Endpoints (auth-service)

```
POST   /api/v1/referrals/generate       → Create referral link (existing tenant OR external)
GET    /api/v1/referrals/:code/validate  → Check if code valid + benefit terms
POST   /api/v1/referrals/:code/redeem     → Activate benefits for new tenant
GET    /api/v1/referrals/me/conversions   → List my referral conversions + payouts
```

#### 4. Event Flow

```
[Existing Tenant Signs Up New Tenant]
    ↓
subscriptions.tenant.created (with referrer_id)
    ↓
[auth-service] Validates referrer is existing tenant
    ↓
referral.created event → treasury-service
    ↓
[treasury-api] Creates benefit obligation ledger entry
    ↓
[Monthly Settlement] Pays benefit to referrer_id account
    ↓
treasury.benefit.paid event → notifications-service
    ↓
[Notifications] Sends email: "You earned $X from referral of ABC Company"
```

#### 5. Dashboard Changes

- **referrer-portal** (new UI): Shows all referral links, conversion count, YTD benefits
- **treasury-ui**: Referral benefits as line-item in "Earnings" breakdown
- **admin-dashboard**: Referral leaderboard (by conversion count, by payout value)

**Timeline**: Week 2-3 (High Priority)  
**Compliance**: Referral terms must be pre-approved by legal; display in onboarding.

---

## SECTION 4: LEGAL ONBOARDING & EQUITY HOLDER PORTAL

### Current Gap
- ❌ No legal acceptance tracking
- ❌ Missing e-signature integration
- ❌ Payout account KYC incomplete
- ❌ No equity-holder audit access

### Requirement: Legally Binding Digital Onboarding + Equity Portal

#### 4.1 Equity Participation Agreement & Terms

**Documents** (Draft + Compliance Review):

1. **Equity Participation Agreement** (EPA)
   - Legally binding; complies with Kenya Companies Act 2015
   - Specifies: equity %, revenue entitlement, vesting schedule, exit terms
   - Informs basis: `codevertex-website/docs/Codevertex-IT-Solutions-Business-Profile.md`
   - Signature required before equity grant

2. **Master Service Agreement** (MSA)
   - Tenant terms; incorporation of all service-specific terms
   - Specifies: usage rights, data ownership, IP, liability
   - References privacy policy + DPA

3. **Privacy Policy & Data Processing Agreement** (DPA)
   - Kenya Data Protection Act 2019 compliant
   - Specifies: data collection, retention, third-party sharing
   - Links to auth-ui "Privacy" page; must be updated to reference full DPA

4. **Service-Specific Addenda**
   - Logistics, Cafe, ERP, etc. have supplementary terms
   - E.g., Logistics Addendum covers liability for delayed deliveries

**Storage**: `legal-management-system/templates/` (integrate with onboarding)

#### 4.2 Digital Onboarding Flow (auth-service)

**Current Flow** (auth-ui):
```
Email + Password → Organization Name → Dashboard
```

**Required Changes**:
```
1. Email + Password
   ↓
2. Organization Name + Tax ID
   ↓
3. ⭐ LEGAL ACCEPTANCE (NEW)
   ├─ MSA + privacy policy summary
   ├─ Checkbox: "I have read and agree to MSA and Privacy Policy"
   └─ (Skip for now if non-equity; flag for later acceptance)
   ↓
4. ⭐ EQUITY ELIGIBILITY (NEW)
   ├─ "Are you an equity holder in Codevertex?" [Yes/No]
   ├─ If YES → Equity Portal enrollment (see 4.3)
   └─ If NO → Dashboard access (limited)
   ↓
5. ⭐ PAYOUT ACCOUNT SETUP (NEW)
   ├─ Bank account (Name, Account, SWIFT, Branch)
   ├─ OR M-Pesa (Phone Number, Registered Name)
   └─ Verify with KYC (see 4.4)
   ↓
6. Dashboard
```

**Implementation** (auth-service):

- Add `legal_acceptance_required` flag to `organizations` table
- Add `legal_acceptance_tracking` table:
  ```sql
  CREATE TABLE legal_acceptances (
      id UUID PRIMARY KEY,
      org_id UUID NOT NULL,
      user_id UUID NOT NULL,
      document_type TEXT, -- 'msa' | 'dpa' | 'epa'
      document_version TEXT,
      accepted_at TIMESTAMP,
      accepted_by_ip TEXT,
      signature_url TEXT, -- e-signature provider URL
      signature_timestamp TIMESTAMP,
      is_active BOOLEAN DEFAULT TRUE
  );
  ```

- Add `equity_holder_applications` table:
  ```sql
  CREATE TABLE equity_holder_applications (
      id UUID PRIMARY KEY,
      user_id UUID NOT NULL,
      org_id UUID NOT NULL,
      equity_percentage NUMERIC,
      equity_grant_date DATE,
      vesting_months INT DEFAULT 36,
      status TEXT, -- 'pending_legal' | 'pending_kyc' | 'active' | 'revoked'
      created_at TIMESTAMP
  );
  ```

#### 4.3 Equity Holder Portal

**Access**: Shared via public link + email redirect by platform admin

**Link Format**:
```
https://auth.codevertex.app/equity-holder/onboard?token=<signed_jwt>
No login required; JWT includes org_id, equity_percentage, vesting_schedule
```

**Portal UI** (new route: `auth-ui/app/equity-holder`):

1. **Dashboard Tab**
   - Equity stake %, vesting status, vesting cliff date
   - YTD dividends + projected annual dividend
   - Account status (Active/Pending KYC/Revoked)

2. **Documents Tab**
   - Download Equity Participation Agreement
   - View dated MSA + DPA versions signed
   - Upload e-signature (via DocuSign/SignEasy embed)
   - Signature audit trail (timestamp, IP, device fingerprint)

3. **Payout Configuration Tab**
   - Edit bank account details (Name, IBAN/Account, SWIFT)
   - Update M-Pesa phone number
   - KYC verification status (Pending/Approved/Rejected)
   - Upload ID scan + proof of address

4. **Treasury & Audit Tab** ⭐ **Real-Time Access to Revenue**
   - Monthly ledger view: "Subscriptions revenue: $50,000 | Your 3% stake: $1,500"
   - Service-by-service breakdown (TruLoad, Logistics, Cafe, etc.)
   - Dividend accrual calendar (monthly/quarterly settlement)
   - Tax withholding breakdown (KRA rates per service)
   - Export audit report (PDF/Excel) for tax/accounting

5. **Support Tab**
   - Contact Codevertex finance team
   - FAQ: vesting, tax, payout schedules

#### 4.4 KYC Integration

**Flow**:
1. Equity holder uploads ID + proof of address in equity portal
2. treasury-api calls KYC provider (e.g., Jumio, Onfido)
3. Verification result → stored in `kyc_verifications` table
4. If approved: unlock payout account; send welcome email
5. If rejected: flag for manual review; notify finance team

**Schema** (treasury-service):
```sql
CREATE TABLE kyc_verifications (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    verification_provider TEXT, -- 'jumio' | 'onfido'
    verification_id TEXT,
    id_type TEXT, -- 'passport' | 'national_id' | 'driver_license'
    status TEXT, -- 'pending' | 'approved' | 'rejected'
    result_json JSONB,
    verified_at TIMESTAMP,
    expires_at TIMESTAMP
);
```

#### 4.5 E-Signature Integration

**Requirement**: Equity Participation Agreement must be digitally signed (legally binding).

**Provider**: DocuSign or SignEasy (Kenya-compliant)

**Flow**:
1. Platform admin clicks "Send Agreement" in treasury-ui admin console
2. System sends equity holder email with signed link
3. Equity holder opens portal → clicks "Sign Agreement"
4. DocuSign embed displays EPA with auto-filled name + org details
5. Holder signs via signature pad / digital ID
6. Signature timestamped + stored; agreement marked "Signed"
7. Finance team notified; equity grant activated

**Implementation** (treasury-service):
```go
POST /api/v1/equity/send-agreement
{
    "user_id": "...",
    "document_url": "...",
    "equity_percentage": 3.0,
    "vesting_months": 36
}
↓
Creates DocuSign envelope → sends invite email
↓
Webhook: agreement_signed → treasury.equity_grant.activated event
```

#### 4.6 Audit Logging & Compliance

**New Table** (audit-service):
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    entity_type TEXT, -- 'equity_grant' | 'legal_acceptance' | 'kyc_verification'
    entity_id UUID,
    action TEXT, -- 'created' | 'updated' | 'signed' | 'verified'
    actor_id UUID,
    actor_role TEXT, -- 'admin' | 'equity_holder' | 'system'
    change_details JSONB,
    timestamp TIMESTAMP,
    ip_address TEXT,
    user_agent TEXT
);
```

**Compliance**: All legal acceptance, KYC verification, and equity grants logged for:
- KRA tax reporting
- Regulatory audit trail
- Fraud detection

---

## SECTION 5: IMPLEMENTATION ROADMAP

### Week 1: Logistics Order Traceability ⚡ CRITICAL
- [ ] Extend `TaskEventData` struct in logistics-service
- [ ] Update cafe-website task assignment form
- [ ] Publish `logistics.task.assigned` with order_id
- [ ] Update audit-logs consumer

### Week 2: Referral System Architecture 🟠 HIGH
- [ ] Design referral schema (auth-service)
- [ ] Implement referral code generation API
- [ ] Build referrer validation logic (existing tenant vs. external)
- [ ] Define benefit obligation ledger entries (treasury-api)

### Week 3: Referral Benefits & Treasury Integration
- [ ] Implement benefit crediting (monthly settlement)
- [ ] Build referral-earnings dashboard (treasury-ui)
- [ ] Publish referral events (treasury.benefit.created, treasury.benefit.paid)
- [ ] Test end-to-end referral conversion

### Week 4: Legal Onboarding & KYC
- [ ] Draft EPA + MSA + DPA (legal review)
- [ ] Add legal_acceptance_tracking table (auth-service)
- [ ] Integrate legal acceptance into auth-ui signup flow
- [ ] Design KYC schema (treasury-service)

### Week 5: E-Signature Integration
- [ ] Select DocuSign or SignEasy provider
- [ ] Implement envelope creation + webhook handling
- [ ] Embed signature UI in equity-holder portal
- [ ] Test legally binding signature flow

### Week 6: Equity Holder Portal
- [ ] Build auth-ui/app/equity-holder routes
- [ ] Dashboard: equity stake + vesting + dividend projections
- [ ] Treasury tab: real-time revenue access per service
- [ ] Payout configuration: bank account + M-Pesa
- [ ] Audit export: PDF treasury reports for tax filing

### Week 7: Compliance & Audit Layer
- [ ] Implement audit_logs table + middleware
- [ ] Create KRA reporting export (tax withholding summary)
- [ ] Enable manual KYC review workflow
- [ ] Final testing + UAT with finance team

---

## SECTION 6: KEY DEPENDENCIES & INTEGRATIONS

### Services Requiring Changes
1. **auth-service** (Go): Legal acceptance, equity eligibility, referral validation
2. **treasury-api** (Go): Royalty ledger, benefit crediting, KYC verification
3. **subscriptions-service** (Go): Referral trigger on tenant creation
4. **logistics-service** (Go): Task event payload (add order_id)
5. **cafe-website** (Next.js): Task assignment form (inject order_id)
6. **treasury-ui** (Next.js): Referral dashboard, equity-holder portal, audit export
7. **audit-service** (new or existing): Central audit logging

### External Integrations
- **DocuSign/SignEasy**: E-signature for EPA
- **Jumio/Onfido**: KYC verification provider
- **KRA**: Tax withholding schedules (query on monthly settlement)

### Communication Patterns
- Event subjects: `treasury.royalty.accrued`, `referral.created`, `referral.converted`, `treasury.benefit.paid`, `auth.legal_acceptance.completed`, `treasury.kyc.approved`
- All events published to NATS JetStream; consumed by treasury-api, audit-service, notifications-service

---

## SECTION 7: COMPLIANCE & GOVERNANCE

### Regulatory Alignment
- **Kenya Companies Act 2015**: Equity participation terms, shareholder disclosure
- **Kenya Data Protection Act 2019**: Privacy policy, DPA, data retention
- **Financial Reporting Standards**: Revenue recognition (IAS 18), equity accounting
- **KRA Tax Code**: Commission withholding, royalty deductibility

### Audit & Transparency
- **Equity holders**: Self-service audit portal with real-time treasury access
- **Finance team**: Monthly reconciliation dashboard (revenue → royalties → benefits → tax withholding)
- **External auditors**: Exportable ledger reports with full transaction history

### Risk Mitigation
- **Fraud detection**: Referral conversion rate limits (max 50 conversions/month per referrer)
- **Double-spend prevention**: Each referral_link redeemable once only
- **Account compromise**: IP address + device fingerprint tracking for all equity actions

---

## SECTION 8: SUCCESS METRICS

| Metric | Target | Owner |
|--------|--------|-------|
| Order → Rider → Delivery traceability | 100% | Logistics Team |
| Referral conversion rate | >5% of onboarded tenants | Growth Team |
| Equity holder KYC completion | >80% in Q3 | Finance Team |
| Legal acceptance audit trail | 100% compliance | Legal Team |
| Avg. time to equity portal access | <5 min | DevOps Team |
| Treasury audit export reliability | 99.9% uptime | Platform Team |

---

## APPENDIX A: Document References

**Business Foundation**:
- `codevertex-website/docs/Codevertex-IT-Solutions-Business-Profile.md` → Informs EPA scope
- Auth-UI privacy page → Basis for full DPA
- Treasury-UI current dashboard → Foundation for equity-holder analytics

**Technical Specifications**:
- `.github/copilot-instructions.md` → Service architecture conventions
- `shared/events/` → NATS JetStream subject naming
- `shared/auth-client/` → JWT validation (shared across services)

**Legal Templates** (to be created):
- `legal-management-system/templates/equity-participation-agreement-ke.md`
- `legal-management-system/templates/master-service-agreement.md`
- `legal-management-system/templates/data-processing-agreement-ke.md`

---

## SIGN-OFF

This directive is binding for all teams and services. Platform admins retain authority to prioritize implementation sequencing. Finance team must approve all royalty rate changes; legal team must review all documents before publication.

**Effective Date**: May 1, 2026  
**Next Review**: August 1, 2026

---
