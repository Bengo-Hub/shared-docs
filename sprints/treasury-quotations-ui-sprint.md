# Treasury UI — Quotations Module Sprint

**Service:** `treasury-ui`
**Branch:** `master`
**Last Updated:** 2026-05-22

---

## Overview

Full revamp of the quotations module to match Refrens-level feature parity, based on a 15-screenshot audit. The original 1,193-line monolith (`quotations/page.tsx`) was modularised into focused sub-components and wired to real API mutations.

---

## Completed

### Phase 0 — Cleanup
- [x] Removed all `navy-*` custom CSS tokens from `globals.css` (`--color-navy-950/900/800/accent/muted/subtle`)
- [x] Removed `@utility bg-dark-panel` and `@utility bg-dark-panel-video`
- [x] Replaced all `navy-*` classes in `invoices/page.tsx` and `quotations/page.tsx` with `slate-*` equivalents

### Phase 1 — Modularisation
- [x] `_components/FiltersPanel.tsx` — collapsible filter panel with Applied Filters chips display
- [x] `_components/TagReportTab.tsx` — tag-wise report tab with date range + status filter
- [x] `_components/ClientsTab.tsx` — manage clients tab with full table + actions
- [x] `_components/CreateQuotationView.tsx` — create/edit quotation form (accepts optional `editId`)
- [x] `_components/QuotationList.tsx` — table with expand line items, inline actions, full context menu
- [x] `_components/QuotationPreview.tsx` — right-side slide-in preview panel
- [x] `_components/QuotationStats.tsx` — lifetime stats block + per-status summary collapsible
- [x] `quotations/page.tsx` rewritten as <180-line tab router importing all sub-components

### Phase 5 — Frontend API & Hook Parity
- [x] `lib/api/invoices.ts` — new functions: `updateQuotation`, `deleteQuotation`, `duplicateQuotation`, `cancelQuotation`, `getQuotationStats`, `getQuotationSummary`, `getQuotationGraph`
- [x] New TS types: `UpdateQuotationRequest`, `QuotationStats`, `QuotationStatusCount`, `QuotationGraphPoint`
- [x] `hooks/use-invoices.ts` — new hooks: `useUpdateQuotation`, `useDeleteQuotation`, `useDuplicateQuotation`, `useCancelQuotation`, `useQuotationStats`, `useQuotationSummary`, `useQuotationGraph`

### Phase 6A — UI: Preview, Expand, Actions
- [x] Quick Preview panel (`QuotationPreview`) — eye icon opens slide-in panel with full document view
- [x] Expand Line Items — `+/-` toggle per row reveals inline sub-table (Item, HSN/SAC, Tax Rate, Qty, Rate, Sub Total, Total)
- [x] Applied Filters chips shown in `FiltersPanel` when any filter is active
- [x] All 12 row inline actions wired: Preview, Open, Edit, Duplicate, Send for Approval (stub), Copy Link, Send Email, Send WhatsApp (stub), Convert to Invoice, Decline, Cancel, Delete

### Phase 6B — UI: Stats & Summary
- [x] Lifetime Data stats block (Total Quotations count + Total Quoted Amount) via `useQuotationStats`
- [x] Quotation Summary collapsible (per-status counts) via `useQuotationSummary`

---

## Pending

### Phase 3 — Per-Tenant Branding
- [ ] `hooks/use-org-branding.ts` — wrap `fetchTenantBySlug(orgSlug)` to return org name, logo, address, email, phone
- [ ] Wire into `CreateQuotationView` "Quotation From" block (replace hardcoded "Codevertex IT Solutions")
- [ ] Show org logo in preview panel header

### Phase 4 — CRM Contact Integration
- [ ] `lib/api/crm.ts` — `searchContacts(tenant, query): Promise<CRMContact[]>` via S2S to marketflow-api
- [ ] `hooks/use-crm-contacts.ts` — debounced search hook
- [ ] Replace static client input in `CreateQuotationView` with combobox that searches CRM contacts
- [ ] Populate `customer_id`, `customer_name`, `customer_email` from CRM selection

### Phase 6C — Show/Hide Columns Modal
- [ ] `_components/ColumnManager.tsx` — modal with two checkboxes per column (Show in CSV / Show in Table), drag-to-reorder, persisted to localStorage
- [ ] "Show/Hide Columns" button (top + bottom of table) opens `ColumnManager`
- [ ] Full 38-column list as specified in audit plan

### Phase 6D — Remaining Row Actions
- [ ] Edit action: opens `CreateQuotationView` in edit mode, pre-populated with existing data via `useQuotation(id)`
- [ ] Download PDF: stub → future PDF generation endpoint
- [ ] Send WhatsApp: open `wa.me/` link with pre-filled message
- [ ] View Invoice: navigate to converted invoice when `converted_invoice_id` is set
- [ ] Send Reminder by Email / WhatsApp (stubs)

### Phase 6E — Form Improvements
- [ ] Auto-increment quote number from `GET /quotations/graph` (use last number)
- [ ] "Total in Words" utility (number → English words for PDF footers)
- [ ] Quote number editable field (pencil icon)
- [ ] "+Add Subtitle" field
- [ ] "+Add Custom Fields" (bottom of form)
- [ ] "+Add Notes", "+Add Attachments", "+Add Signature" sections

### Phase 6B Remaining
- [ ] `_components/QuotationGraph.tsx` — line chart (recharts) consuming `useQuotationGraph`

### Phase 7 — Shared Document Template
- [ ] `src/components/documents/DocumentTemplate.tsx` — shared layout for quotation + invoice PDF views
- [ ] `src/components/documents/LineItemsTable.tsx` — shared line item component

### Phase 9 — Step 2: Design & Share
- [ ] `app/[orgSlug]/quotations/[id]/design/page.tsx`
- [ ] Advanced settings: PDF signature, watermark, page size, margins, scale
- [ ] Payment schedule section
- [ ] Approval history section
- [ ] Acceptance history section
- [ ] Linked Documents section
- [ ] Audit Trail event log

---

## File Map

| File | Purpose |
|------|---------|
| `src/app/[orgSlug]/quotations/page.tsx` | Tab router (~180 lines) |
| `_components/FiltersPanel.tsx` | Collapsible filter panel |
| `_components/CreateQuotationView.tsx` | Create/edit form |
| `_components/QuotationList.tsx` | Table with expand + actions |
| `_components/QuotationPreview.tsx` | Quick preview side panel |
| `_components/QuotationStats.tsx` | Lifetime stats + summary |
| `_components/ClientsTab.tsx` | Manage Clients tab |
| `_components/TagReportTab.tsx` | Tag-wise Report tab |
| `src/lib/api/invoices.ts` | All quotation + invoice API functions |
| `src/hooks/use-invoices.ts` | All quotation + invoice TanStack Query hooks |

---

## Key Design Decisions

- **CRM owns customer data**: `customer_id` in quotations is a nullable FK reference to CRM Contact UUID. The form must search via S2S to marketflow-api — never store customer details locally beyond name/email cache on the quotation itself.
- **Shared hooks**: Invoice and quotation hooks live together in `use-invoices.ts` to avoid duplication; may be split later when either exceeds 400 lines.
- **Preview is a route-level portal**: `QuotationPreview` renders as a fixed overlay on the page, not a separate route, to allow fast preview without losing filter state.
- **Stats are Go-side aggregates**: `GetQuotationStats` and `GetQuotationGraph` aggregate in Go over fetched rows (not raw SQL) for portability; acceptable at quotation list scale.
