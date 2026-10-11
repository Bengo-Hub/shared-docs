# Repairs and vendors

## A work order's life

Residents raise requests from the portal with photos; staff raise work orders from the console or a
phone. Every work order carries a priority with response and fix times.

| Priority | Respond within | Fix within |
|---|---|---|
| Emergency | 1 hour | 4 hours |
| High | 4 hours | 24 hours |
| Normal | 24 hours | 72 hours |
| Low | 3 days | 14 days |

```mermaid
stateDiagram-v2
  [*] --> Requested
  Requested --> Assigned: assign a vendor or staff member
  Assigned --> Quoted: record a quote
  Quoted --> Approved: quote approved
  Quoted --> Assigned: quote rejected, quote again
  Assigned --> InProgress: start
  Approved --> InProgress: start
  InProgress --> Completed: complete with photos
  Completed --> Confirmed: resident confirms
  Completed --> Reopened: resident reopens within 7 days
  Reopened --> Assigned
  Confirmed --> Closed
```

Work past its fix time is flagged and the manager is told. When a job is complete the resident is
asked to confirm; they can reopen it within seven days.

## Quotes

When a vendor quotes, record it on the work order. The quote then waits in
[Approvals](approvals.md): by default one approval by someone who manages works, never the person who
entered the quote. Larger quotes can need more steps if you set a rule. Approved, the work can start;
rejected, it goes back for a new quote with your reason. A repair caused by an owner can be recharged
to their unit.

## Vendors

Under **Vendors** keep each contractor with its category and documents. Each category lists the
documents it must hold (a security agency needs its PSRA licence, a garbage collector its NEMA
licence, and so on). Maskani warns before a document expires.
