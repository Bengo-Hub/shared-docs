# Maskani architecture

Maskani is the property and estate management product: `maskani-api` (Go, Ent, Atlas migrations),
`maskani-ui` (Next.js console, resident portal and gate tablet at `maskaniapp.codevertexafrica.com`)
and `maskani-commerce` (the public marketplace at `maskani.codevertexafrica.com`). The repositories'
own `docs/` folders hold the full API spec, ERD and event list; this page is the map.

## How it connects

```mermaid
flowchart LR
  UI[maskani-ui<br/>console, portal, gate] -->|REST + SSE| API[maskani-api]
  COM[maskani-commerce] -->|public market API| API
  API -->|S2S: invoices, credit notes,<br/>manual payments, ledgers, C2B routes| TR[treasury-api]
  TR -->|treasury.payment.succeeded| API
  API -->|outbox: maskani.*| NATS[(NATS JetStream)]
  NATS --> NOTIF[notifications-api<br/>WhatsApp, email, push]
  API -->|members, outlets| AUTH[auth-api]
  API -->|feature codes maskani_*| SUBS[subscriptions-api]
```

Ownership follows [Cross-Service Data Ownership](cross-service-data-ownership.md): Maskani owns the
register, billing runs, meters, works, gate, notices, documents and its own approvals; it never moves
money. Treasury's account ledger (by `account_ref`) is the balance of record.

## Tenancy and modules

- Every domain table carries `tenant_id` and an Ent tenant guard; requests are scoped to the caller's
  properties (staff) or unit links (portal).
- A property is also an auth-api outlet, so branch-scoped roles apply to properties.
- Modules (`properties`, `billing`, `utilities`, `sales`, `estate`, `maintenance`, `providers`, `gate`,
  `staff`, `communication`) are switched per tenant and overridden per property. A property's
  `use_case` picks a preset module set; subscriptions gate each module by the feature code
  `maskani_<module>`.

## Money flow

```mermaid
sequenceDiagram
  participant R as Resident
  participant M as maskani-api
  participant T as treasury-api
  participant N as notifications-api
  M->>T: Issue invoice (reference maskani_bill, metadata.account_ref)
  M->>N: bill.issued (itemised, pay instruction)
  R->>T: M-Pesa prompt or paybill (account_payment intent)
  T->>T: Allocate oldest due first, hold the rest as credit
  T-->>M: treasury.payment.succeeded
  M->>M: Refresh balance, record per-account collection
  M->>N: payment.applied (receipt)
```

- Bank paybills: a fund's `metadata.paybill_account_format` (`{ref}`, `2362010#{ref}` or the bank
  account alone) shapes the pay instruction; statement CSV imports match credits into manual payments.
- Manual payments (bank, cash, cheque, typed M-Pesa) book through
  `POST /s2s/{tenant}/accounts/{ref}/manual-payments` only after approval.
- Credit notes inherit the bill's `account_ref`; the ledger nets them off and the allocator skips
  them. Only unpaid amounts can be credited.
- Late charges are Treasury invoices with `metadata.kind = late_charge`, excluded from the overdue
  base so they never compound.

## Approvals

One engine, `internal/modules/approvals`, shaped like treasury's and inventory's. See the platform
standard [Approvals](../platform-standards/approvals.md). Modules on it: `credit_note`,
`adjustment`, `manual_payment`, `work_order_quote`, `restructure`. Inbox `GET /approvals`, rules
`/approvals/rules`.

## Sales after signing

- **Plan versions.** A contract's payment plan is a versioned `instalment_schedules` row. A
  restructure writes the next version as `proposed` for the lines not yet invoiced and submits it
  to the approvals engine (`restructure`). Once approved the buyer accepts it in the portal
  (`POST /me/plans/{id}/accept`) or reads back a one-time code at the office (`internal/shared/otp`,
  the same code store the privacy module uses). Acceptance supersedes the old version; lines already
  invoiced stay and keep syncing with Treasury, and a contract in default is cured.
- **Overpayment.** Treasury pays a newly sent account bill from credit the account holds, and
  instalment invoicing syncs progress for the accounts it issued on, so an overpayment reduces the
  next instalment without a separate path.
- **Handover.** One `handovers` row per contract (keys, checklist and snags as JSON). Completion
  writes a `handover` meter reading per unit meter (not billed; the next round measures from it),
  marks the unit and contract handed over, publishes `maskani.unit.handed_over` and links the buyer
  as owner through the register's link path, which starts estate billing prorated.
- **Title.** Stages come from the estate's `title_stage` catalogue; the `title_released` stage done
  marks the contract and unit titled.

## Reports

One registry (`internal/modules/reports/registry.go`) defines every report once: name, module,
filters and, for table reports, columns and SQL. Three things read it, so a report is added in one
place:

```mermaid
flowchart LR
  REG[(Report registry)] --> CAT[GET /reports/catalog<br/>by module, filtered by modules and rights]
  REG --> TAB[GET /reports/id/table<br/>grouped SQL on the replica, cached]
  REG --> EXP[GET /reports/id/export<br/>docs.Export, branded PDF, Excel, CSV]
  CAT --> UI[Reports page]
  TAB --> UI
  EXP --> UI
```

Downloads all go through the docs module's `Export`, the same branded engine as statements and
letters; the older arrears, performance and water balance download URLs are aliases of it. This is
the TruLoad report catalog pattern.

## Audit, limits and privacy

- **Audit trail.** One middleware records an allowlist of critical security workflows (access,
  configuration, money decisions, ownership, personal data) after they succeed. Routine work is never
  logged. A router test fails if an allowlisted route stops existing.
- **Plan limits.** Units and staff users are checked against the token's `max_units` and
  `max_users`, answering 402 `usage_limit_exceeded` as pos-api does; exempt tenants pass.
- **Privacy.** Residents and owners are Maskani's own data subjects, so their requests live here,
  not in the auth consent ledger (platform users only). `internal/modules/privacy` holds requests
  (access, correction, erasure with 7 and 14 day deadlines), identity by a one-time code through
  notifications' shared auth OTP templates or in person, an export zip built on demand (never
  stored), anonymisation that keeps financial records, and the single retention schedule.
- **Terms history.** Each acceptance is appended to the party's `consents.terms_history` with the
  privacy notice version, time and address.

```mermaid
flowchart LR
  P[Portal request] --> V[verified]
  O[Office request] --> R[received] -->|code to phone on record, or in person| V
  V -->|access| X[export zip on demand] --> C[completed]
  V -->|correction| C
  V -->|erasure, no active unit link| A[anonymise party, keep finance] --> C
  R --> J[rejected]
  V --> J
```

## Background jobs

Every job runs once per period across pods (`sharedcache.ClaimPeriod`), per the
[multi-replica jobs](../platform-standards/multi-replica-jobs.md) standard.

| Job | Every | Does |
|---|---|---|
| `maskani:c2b-routes` | minute | Registers paybill account routes in Treasury |
| `maskani:billing-resume` | minute | Resumes billing runs a stopped pod left issuing |
| `maskani:billing-schedules` | hour | Starts scheduled runs, reminds about missing readings |
| `maskani:collections-ladder` | hour | Payment plan checks, then one ladder step a day per owing account, working hours only |
| `maskani:late-charges` | hour | Monthly late charge per owing account where switched on |
| `maskani:occupancy-links` | hour | Ends links on their date with their effects; clears stale bill-to |
| `maskani:instalment-reminders`, `instalment-invoicing` | hour | Sale instalments: reminders, overdue, defaults, invoices |
| `maskani:collections-backfill` | hour | Per-account collections from Treasury ledgers for history |
| `maskani:sla-breaches` | minute | Flags work orders past their fix time |
| `maskani:vendor-doc-expiry` | hour | Warns before vendor documents expire |
| `maskani:gate-offline` | minute | Gate tablet health |
| `maskani:retention` | day | The retention schedule: gate data, finished passes, lapsed visitors, document access logs, audit trail |
| `maskani:scheduled-notices` | minute | Sends notices on their schedule |
| `maskani:daily-stats-rebuild` | hour | Rebuilds dashboard figures |
| `maskani:reservation-expiry` | minute | Releases unpaid reservations |

## Events

Published through the outbox on `maskani.*`, consumed by notifications-api (and Treasury where
noted in the API repo's `docs/events.md`). Staff alerts carry `responders` (the people to reach)
resolved in Maskani: property staff by property role, or role holders for an approval step.

## Media

Uploads live under `tenants/{id}/{kind}/...`. Estate and unit photos are public and cached
immutably; every other kind (documents, readings, works, incidents, vendors) needs a signed link
from `POST /media/sign`.
