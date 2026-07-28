# Sourcing & Traceability Platform - Flow & BPMN Walkthrough

<!-- Each "## " heading below becomes one landscape slide. Keep sections short. -->

## Executive Summary

Processa proved the problem is real: Kenyan agro-processors need farm-to-shelf traceability,
weighbridge-accurate intake, quality-gated release, and transparent grower payouts. Its
implementation duplicated the Codevertex ecosystem instead of joining it.

- **Reuse everything that already exists**: identity, suppliers, purchase orders, GRN,
  warehouses, stock, production, weighbridge, cold chain, financial approvals, payouts.
- **Build only the genuinely new ground**: two services, `sourcing-api` and `traceability-api`.
- **Zero duplicate systems of record** - every new table holds an ID reference, never a copy.

## The Real Problem

- **eTIMS (2026)**: KRA validates stock movements against fiscal data - uncertified costs get
  disallowed. `treasury-api` is already the fleet's single fiscalisation point.
- **Warehouse Receipt System (EAGC/WRSC)**: a certified receipt unlocks 60 to 70 percent bank
  credit against deposited grain - a real Kenyan financing instrument, unmodelled today.
- **KEBS/HACCP/FSSC 22000**: aflatoxin limit 10 &micro;g/kg on maize; digital traceability, CCP
  monitoring, NC/CAPA and mock-recall drills are now the entry ticket to formal-channel buyers.
- **EUDR**: binds micro/small operators from 30 December 2026 - plot-level geolocation and a
  due-diligence statement per export consignment, no relief for Kenya.
- **Outgrower trust**: farmers often keep only 31 to 34 percent of gross value because settlement
  deductions are opaque - a transparent settlement ledger with M-Pesa payout is the single
  highest-trust feature a processor can ship.

## Reuse-First: The Current Ecosystem

```mermaid
flowchart LR
    A[auth-api<br/>identity and RBAC] --> S[sourcing-api]
    A --> T[traceability-api]
    I[inventory-api<br/>suppliers, GRN, stock, lots] --> S
    I --> T
    W[TruLoad<br/>commercial weighbridge] --> S
    R[treasury-api<br/>payments, payouts, tax] --> S
    L[logistics-api<br/>fleet, cold chain] --> T
    N[subscriptions-api and notifications-api] --> S
    N --> T
```

Nothing in this diagram is rebuilt. `sourcing-api` and `traceability-api` are the only new boxes.

## Flow 1 - Grower Intake to Settlement (BPMN-style)

```mermaid
flowchart LR
    A(["Grower arrives<br/>with delivery"]) --> B[["Weighbridge<br/>gross and tare"]]
    B --> C[["Intake grading<br/>moisture and impurities"]]
    C --> D{"Grade meets<br/>spec?"}
    D -- yes --> E[["Create GRN<br/>in inventory-api"]]
    D -- reject --> X(["Reject and<br/>return load"])
    E --> F[["Settlement run<br/>per grower, per period"]]
    F --> G[["M-Pesa B2C payout<br/>via treasury-api"]]
    G --> H(["Grower notified"])
```

## Flow 2 - Lot Genealogy Through Dispatch (BPMN-style)

```mermaid
flowchart LR
    A(["Lot received<br/>at intake"]) --> B[["Sampling event"]]
    B --> C[["Lab test result<br/>vs spec range"]]
    C --> D{"Within<br/>spec?"}
    D -- release --> E[["Process route<br/>dry, sort, mill"]]
    D -- hold --> F[["Quarantine<br/>pending review"]]
    F --> D
    E --> G[["Co-product output<br/>oil and seedcake"]]
    G --> H[["Packaging"]]
    H --> I(["Dispatch to<br/>distribution"])
```

## Flow 3 - Recall & Mock-Recall Traversal

```mermaid
flowchart TB
    A(["Recall triggered<br/>on a finished lot"]) --> B[["Walk genealogy<br/>one level up"]]
    B --> C[["Identify source<br/>raw material lots"]]
    A --> D[["Walk genealogy<br/>one level down"]]
    D --> E[["Identify affected<br/>finished lots and shipments"]]
    C --> F(["Scope report:<br/>suppliers implicated"])
    E --> G(["Scope report:<br/>customers and outlets affected"])
    F --> H(["Recall or mock<br/>recall drill closed"])
    G --> H
```

## Flow 4 - EUDR Due-Diligence Assembly (Phase 2)

```mermaid
flowchart LR
    A[["Farm geolocation<br/>point or polygon"]] --> D[["Due diligence<br/>statement"]]
    B[["Grower and supplier<br/>chain"]] --> D
    C[["Lot genealogy<br/>to export consignment"]] --> D
    D --> E(["Filed against<br/>export consignment"])
```

## Data Flow - Grower Registration

```mermaid
sequenceDiagram
    participant U as Field officer
    participant S as sourcing-api
    participant I as inventory-api
    U->>S: Register grower and farm
    S->>I: Create Supplier (category Farmer)
    I-->>S: supplier_id
    S->>S: Store Farm geolocation and consent
    S-->>U: Grower profile ready
```

## Data Flow - Intake Grading & GRN

```mermaid
sequenceDiagram
    participant O as Receiving bay
    participant T as TruLoad
    participant S as sourcing-api
    participant I as inventory-api
    O->>T: Weigh vehicle, two pass
    T-->>S: Weigh ticket, gross tare net
    S->>S: Apply moisture and impurity grading
    S->>I: Create GRN with adjusted net weight
    I-->>S: grn_id
    S-->>O: Payable weight and price confirmed
```

## Data Flow - Sampling, Lab & Disposition

```mermaid
sequenceDiagram
    participant Q as QA technician
    participant TR as traceability-api
    participant I as inventory-api
    Q->>TR: Record sampling event on lot
    TR->>TR: Run lab test vs spec range
    TR->>Q: Result flagged pass or fail
    Q->>TR: Approve disposition, release or hold
    TR->>I: Reference lot_id, no stock duplication
```

## Data Flow - Process Route & Mass Balance

```mermaid
sequenceDiagram
    participant TR as traceability-api
    participant I as inventory-api
    TR->>I: Read ProductionBatch by id
    TR->>TR: Record step weight in and weight out
    TR->>TR: Compute yield and loss per step
    TR->>I: Post completion, oil output
    TR->>I: Post completion, seedcake output
    I-->>TR: Both co-products land in stock
```

## Data Flow - Settlement & Payout

```mermaid
sequenceDiagram
    participant S as sourcing-api
    participant TE as treasury-api
    participant M as M-Pesa
    S->>S: Aggregate payable lines per grower
    S->>TE: Disburse payout request
    TE->>M: B2C payment request
    M-->>TE: Result callback
    TE-->>S: Payout confirmed
    S->>S: Mark settlement line paid
```

## New Services At a Glance

| Service | Owns | Never duplicates |
|---|---|---|
| `sourcing-api` | Grower overlay, farm geolocation, intake grading, settlement runs | Supplier master, GRN, payment rails |
| `traceability-api` | Lot genealogy, sampling/lab/CoA, process routes, HACCP (Phase 2) | Stock ledger, production batch, cold-chain data |

Both built on the confirmed `library-api`/`library-ui` template: Go 1.26, Ent + Atlas, chi,
NATS outbox, Next.js 16.2.3, SSO PKCE.

## Phased Implementation

| Phase | Scope |
|---|---|
| 0 | Scaffold both services, wire S2S clients, register in devops-k8s/subscriptions/notifications/auth |
| 1 | Grower and farm registry, intake grading, lot genealogy, sampling/lab/CoA, process route with mass balance, settlement and payout |
| 2 | Outgrower contracts, warehouse receipts, HACCP/CCP, NC/CAPA, recall drills, EUDR DDS |
| Decommission | Migrate a pilot tenant off Processa once Phase 1 is validated |

## Next Steps

- Approve Phase 0 scaffolding for `sourcing-api` and `traceability-api`.
- Confirm the additive `inventory-api` schema changes (lot lineage, quality attributes, GRN
  gross/tare weight) with the inventory-api maintainers.
- Confirm the TruLoad weigh-ticket S2S contract and the TruLoad-to-Codevertex tenant mapping.
- Schedule the Phase 1 end-to-end pilot on a demo tenant.
