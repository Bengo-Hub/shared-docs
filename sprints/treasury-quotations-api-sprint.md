# Treasury API — Quotations Module Sprint

**Service:** `treasury-api` (`finance-service/treasury-api`)
**Branch:** `main`
**Last Updated:** 2026-05-22

---

## Overview

Backend audit and extension of the quotations module in treasury-api. The existing implementation had Create/Read/List/Send/Accept/Decline. This sprint adds Update, Delete, Duplicate, Cancel, and three analytics endpoints (stats, summary, graph), and documents all gaps.

---

## Completed

### New Endpoints

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| PUT | `/{tenant}/quotations/{id}` | Update draft quotation + replace lines | ✅ Done |
| DELETE | `/{tenant}/quotations/{id}` | Delete draft or declined quotation | ✅ Done |
| POST | `/{tenant}/quotations/{id}/duplicate` | Clone quotation as new draft | ✅ Done |
| POST | `/{tenant}/quotations/{id}/cancel` | Cancel any non-converted quotation | ✅ Done |
| GET | `/{tenant}/quotations/stats` | Lifetime total count + total amount | ✅ Done |
| GET | `/{tenant}/quotations/summary` | Per-status count array | ✅ Done |
| GET | `/{tenant}/quotations/graph` | Monthly count + amount trend | ✅ Done |

### New Models / DTOs
```go
UpdateQuotationRequest   // PATCH-style update: all fields optional
QuotationStats           // { total_count, total_amount, currency }
QuotationStatusCount     // { status, count }
QuotationGraphPoint      // { month "YYYY-MM", count, total_amount }
```

### Business Logic Guards
- `UpdateQuotation`: only allowed on `status = "draft"` → returns `ErrInvalidTransition` otherwise
- `DeleteQuotation`: only `draft` or `declined` → `ErrInvalidTransition` otherwise
- `CancelQuotation`: blocked for `converted` and `cancelled` statuses
- `DuplicateQuotation`: clones all fields + line items, generates new quote number, sets `status = "draft"`, sets `ValidUntil = now + 1 month`

### Repository Additions (Ent ORM)
- `UpdateQuotation`: updates scalar fields + replaces all `QuotationLine` rows (delete-then-insert)
- `DeleteQuotation`: hard delete with tenant scoping
- `GetQuotationStats`: count + Go-side sum over `total_amount`
- `GetQuotationStatusCounts`: Go-side group-by over `status` field
- `GetQuotationGraph`: Go-side group-by over `quote_date.Format("2006-01")` → sorted monthly points

---

## Existing Endpoints (Pre-Sprint)

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| GET | `/{tenant}/quotations` | List with filters (status, from, to, page, limit) | ✅ |
| POST | `/{tenant}/quotations` | Create new quotation | ✅ |
| GET | `/{tenant}/quotations/{id}` | Get single quotation with lines | ✅ |
| POST | `/{tenant}/quotations/{id}/send` | Mark as sent (from draft only) | ✅ |
| POST | `/{tenant}/quotations/{id}/accept` | Accept → auto-create invoice, mark converted | ✅ |
| POST | `/{tenant}/quotations/{id}/decline` | Mark as declined | ✅ |

---

## Pending

### NATS Event Publishing
- [ ] Publish `treasury.quotation.created` on `CreateQuotation`
- [ ] Publish `treasury.quotation.sent` on `SendQuotation`
- [ ] Publish `treasury.quotation.accepted` on `AcceptQuotation` (include invoice ID)
- [ ] Publish `treasury.quotation.declined` on `DeclineQuotation`
- [ ] Publish `treasury.quotation.cancelled` on `CancelQuotation`
- [ ] Publish `treasury.quotation.deleted` on `DeleteQuotation`

### Invoice Parity
- [ ] `PUT /{tenant}/invoices/{id}` — update draft invoice (currently read-only after creation)
- [ ] `POST /{tenant}/invoices/{id}/duplicate` — clone invoice as draft

### Quote Number Auto-Increment Endpoint
- [ ] `GET /{tenant}/quotations/next-number` — returns preview of the next quote number without consuming it (used by the form to show "Last No: QT-000042")

### Bulk Operations
- [ ] `POST /{tenant}/quotations/bulk-upload` — CSV import of quotations
- [ ] `POST /{tenant}/quotations/bulk-delete` — batch delete (array of IDs)

### Convert to Proforma Invoice
- [ ] `POST /{tenant}/quotations/{id}/proforma` — creates a proforma invoice (type="proforma") from quotation, similar to `accept` but does not mark as converted

### Approval Workflow
- [ ] `POST /{tenant}/quotations/{id}/submit-approval` — triggers approval workflow
- [ ] `GET /{tenant}/quotations/{id}/approval-history` — returns approval events
- [ ] Backend: ApprovalRecord entity already in Ent schema — needs wiring for quotations

### Acceptance Tracking
- [ ] `POST /{tenant}/quotations/{id}/client-accept` — client-side accept (email link flow)
- [ ] `POST /{tenant}/quotations/{id}/client-decline` — client-side decline
- [ ] `GET /{tenant}/quotations/{id}/acceptance-history` — audit of client actions

### Linked Documents
- [ ] `GET /{tenant}/quotations/{id}/linked` — returns related invoice, proforma, sales order, delivery challan

### Audit Trail
- [ ] Wire `AuditLog` entity (already in Ent schema) to quotation lifecycle events
- [ ] `GET /{tenant}/quotations/{id}/audit` — returns event log

---

## Service Architecture

```
handlers/invoicing.go       HTTP layer — parse, validate, delegate
modules/invoicing/service.go  Business logic — guards, orchestration
modules/invoicing/repository.go  Interface (Ent ORM + testable)
modules/invoicing/repository_ent.go  Ent implementation
modules/invoicing/models.go  DTOs + domain structs
```

### Tenant Scoping Pattern
All queries use `WHERE tenant_id = $tenantID` — never trust client-provided tenant from body. `ResolveTenantForRequest(r)` extracts from JWT claims (middleware-set context).

### Status Machine

```
draft → sent → accepted → converted
      ↘ declined
      ↘ cancelled
      ↘ expired (time-based, not yet implemented)
```

Delete is only allowed from `draft` or `declined`.

---

## Key Decisions

- **Go-side aggregation for stats/graph**: Avoids raw SQL `Modify()` calls (not supported in this Ent version). Acceptable at quotation list scale; switch to raw SQL aggregate if performance becomes an issue.
- **Hard delete**: `DeleteQuotation` physically removes the row. A future soft-delete (add `deleted_at` to schema) is preferred for audit compliance — noted as P2.
- **Line item replacement on update**: `UpdateQuotation` deletes all existing `QuotationLine` rows then inserts new ones in a single DB round-trip. This avoids diff-matching complexity.
- **Quote number format**: `QT-000001` (sequential per tenant). `GetNextQuoteNumber` uses `COUNT(*) + 1` — not race-safe under concurrent creation; acceptable until high concurrency is needed (fix: DB sequence or advisory lock).
