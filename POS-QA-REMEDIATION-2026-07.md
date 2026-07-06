# POS QA Remediation Sprint — 2026-07-06

Source: `pos-service/pos-QA-review/POS_QA_Requirements_and_Defects.docx.md` (REQ-001–009 + DEF-001)
plus the screenshot audit (date-range, outlets filter, 404s, partial-payment filter, payments modal).
Plan: `D:\Projects\Codevertex\.claude\plans\pos-qa-remediation-sprint.md`.

## Shipped (per repo, main/master)

| Repo | Commits | What |
|---|---|---|
| pos-api | `ca827f0`, `79c6a09`, `5d7bbcc` | DEF-001 draft-500 fix (subtype normalize → 400 never 500); Sell-Details/Return-by-Invoice 404 fix (outlet predicate removed from single reads); stored `paid_total` + unified paid/partial/due filter↔badge semantics (+ backfill migration); `completeOrderIfFullyPaid` double-count fix; REQ-007 server-side cashier scoping (`view_own` + open-bill carve-out; by-number stays tenant-wide for returns); payment edit/void/notify endpoints (manual tenders only; treasury reversal); gateway settled-amount honoring + `settled_via` marker; reason-based refund-method policy; on-account returns default/force `offset_invoice`; real exchange flow (replacement order + exchange-credit discount + top-up/leftover) |
| treasury-api | `3f8760b`, `5aa762e`, `7301542`, `d5f785f`, `edfb677` | `InvoicePayment` records + cumulative `Invoice.amount_paid` (+ migration/backfill); `treasury.payment_received` now fires on EVERY payment with amount/amount_paid/balance/is_partial/method/reference; payment PATCH/VOID/notify endpoints (change/manage-gated); MarkPaid synthetic row; ARTransaction itemized ledger + full credit-history statements (REQ-009); `offset_invoice` refunds now reduce CustomerBalance; Transactions `customer_name` (REQ-005); approval OTP 2FA (REQ-004: hashed 6-digit, 5-min TTL, 3 attempts, 45s cooldown, outbox email delivery) |
| pos-ui | `cc81027`, `0803984`, `e45e013` | My Sales/My POS Sales titles + cashier role map; permission-gated actions menu; modular sales components; expandable line-item rows (treasury pattern) + grid borders (REQ-008) + Cashier column (REQ-005); Day/Week/Month/Year + Custom date modes (REQ-002); tender-driven payment-method filter; detailed View Payments modal (edit/void/print/notify); draft payload fix; resume-sale from Drafts (REQ-003, same-order completion); projected stock preview (REQ-001); manager cost column (REQ-006); reason/on-account-aware returns UI + exchange picker with top-up payment |
| treasury-ui | `7b3617c`, `610f31e` | Invoice View Payments modal; RecordPaymentModal now submits method/reference/receipt/date; REQ-005 columns (Transactions Customer, Journals Recorded By); approval OTP step |
| notifications-api | `97f701f` | Mappings for `pos.payment.received_notification` (SMS receipt), `treasury.payment_received_notification` (email receipt), `treasury.approval_otp_requested` (OTP email to approver only) |

## REQ-005 audit findings (Customer / Cashier columns)

- **POS All Sales / POS Sales**: Customer + Contact already present; **Cashier column added** (order `user_id` → staff name).
- **Treasury Transactions** (payment intents): **Customer added** from the intent's metadata snapshot (present when the source recorded one). **Cashier: N/A** — payment intents do not store the till user; the cashier lives on the pos order (`user_id`) and on journals (`created_by`). Documented, not invented.
- **Treasury Journal Entries**: **Recorded By added** (`created_by`). **Customer: N/A** — journals reference source documents, not customers; the reference column links to the doc that owns the customer.

## Known limitations / decisions (approved)

- **Historical partial invoices**: `amount_paid` backfills `total_amount` only for already-`paid` invoices; historical "partial" invoices have no per-payment rows to reconstruct and stay at 0 (correct going forward). Statements fall back to invoice-derived lines for customers predating the AR ledger.
- **Payment edits never change amounts** — void + re-record (keeps GL/AR consistent). Gateway/on-account/loyalty payments cannot be voided at the till (refund/returns flows own them).
- **Exchange GL**: revenue/VAT nets via the replacement order's exchange-credit discount; returned-goods COGS reversal is only posted when a leftover refund goes to treasury (stock counts stay correct via `exchange.completed` restock; GL COGS on even swaps is a known small drift, documented in returns.go).
- **treasury.payment_received (automatic)** is deliberately NOT mapped to customer emails — customer comms remain the explicit "Send Payment Received Notification" action.

## Cross-repo follow-ups (flagged, not hacked in)

1. **CRM-backed customer filter (REQ-002)**: the All-Sales Customer filter matches order-stored name/phone. A CRM-driven picker needs a marketflow READ/search endpoint (current client is write-only `UpsertContactByPhone`).
2. **Customer email match (REQ-002)**: `POSOrder` stores no customer email — matching by email requires either adding the field at checkout capture or the CRM read above.
3. **Prod ops — RBAC re-seed**: the cashier role change (drop `pos.orders.view`, keep `view_own`) requires running the pos-api seeder in prod; the seeder now revokes dropped grants on GLOBAL system roles (tenant-scoped copies stay add-only).
4. **Prod ops — migrations**: three new migrations must apply on deploy: pos `20260705211512_add_posorder_paid_total` (with backfill), treasury `20260705221537_add_invoice_payments_amount_paid` (with backfill), `20260705225857_add_ar_transactions`, `20260705235324_add_approval_otps`.
5. **JetStream durables**: no filter-subject changes to existing durables; new events flow through the existing `pos.>` / `treasury.>` wildcard consumers.

## E2E verification checklist (codevertex-demo)

1. Draft: POS Add Sale → Save as Draft → 201; Drafts page → Resume Sale → prefilled → Complete Sale settles the SAME order.
2. 404s: All-Sales row from another outlet → Sell Details opens; Return by Invoice finds `POS-…` receipts across outlets.
3. Partial: Multiple-Pay 400 of 464 → badge Partial, Sell Due 64; Partial filter returns exactly the Partial-badged rows; Due filter excludes them.
4. Cashier: demo cashier sees "My POS Sales" scoped to own sales (+ open bills); manager sees all; direct API `GET /orders/{other-cashier-order}` → 404 for cashier.
5. Payments modal: edit reference/note on a cash payment; void → order reopens to pending_payment, treasury reversal posted; Send Payment Received Notification → SMS/email queued.
6. Credit-sale return: 2,000 on account → return 800 (`changed_mind`) → forced `offset_invoice` → CustomerBalance 1,200 + ARTransaction lines on the statement; `defective` reason hides/blocks store credit.
7. Exchange: dearer replacement → replacement order + top-up payment modal; cheaper → leftover refund; even → auto-completed replacement.
8. OTP: approve a payout/vendor-bill/expense without a code → 428; request code → email; wrong ×3 → locked; correct → approved.

## Live E2E results (codevertex-demo, 2026-07-06)

PASSED against production after CI/CD rollout (pos-api `85abef2`, treasury-api `edfb677`):
1. **DEF-001**: `POST /pos/orders` with `order_subtype:"draft"` → 201, status `draft`, subtype `retail` (was 500).
2. **404 fix**: GET order by id AND by-number with a mismatched `X-Outlet-ID` → 200.
3. **Partial semantics (pos)**: 200/371.20 cash payment → `paid_total=200`, order stays `draft` (the old double-count would have completed it at ≥185.60); `?payment_status=partial` contains it with badge `partial` (paid 200 / due 171.20); `due` filter excludes it; voiding the payment → `paid_total=0`, back in the `due` filter.
4. **Partial semantics (treasury)**: 1,000 invoice + 400 (mpesa/ref) → `partial`/`amount_paid=400`; +700 cash → `overpaid`/1,100, status `paid` (cumulative — the old per-call compare kept it partial); void 700 → `partial`/400, invoice reopened to `sent`; payment rows persisted with method+reference.
5. **Returns policy**: `defective` + `store_credit` → 422 rejected; `changed_mind` + `store_credit` → created (`on_account_sale=false` persisted); reject path OK; full initiate→approve→complete cycle settled a cash reversal in treasury (`treasury_refund_ref` recorded).
6. **Fixed during E2E**: SSO principals (demo admin) were 403'd by the new order-read gate — JWTs carry no `pos.*` codes and no assignment rows exist; the middleware now falls back to the /auth/me role-code mapping (pos-api `abaec0f`). Seeded tender type `manual` added to the voidable set (`85abef2`).

**E2E residue (demo tenant, books net zero):** pos order `POS-C4B537678A25` (fully returned/reversed, stock restored) + its payment/return/audit rows; treasury journal entries for the reversed payments and the deleted invoice `INV-260706-000014`'s two voided payment rows. Row-level deletion + the requested urban-loft transaction wipe need the psql-over-SSH admin path, which was blocked in this session — run per `postgres-topology-and-data-clearing` when authorized.

## Follow-up (2026-07-06 pm): cost/margin columns + non-billable items

- **Terminal cart** (pos-ui `872f06b`): explicit grid tracks (proper spacing), Cost column eye-masked by default + a separate Margin column for admin/manager (`pos.catalog.view_cost` / `pos.orders.manage`); margin follows the cost reveal state (margin% + price exposes cost arithmetically). Add Sale already had the masked cost column.
- **Non-billable items end-to-end**: inventory `Item.non_billable` (migration `20260706093044` + corrective `20260706111500` — the first backfill's `%ugali%` LIKE was over-broad, catching "Ugali Flour" INGREDIENT and potentially priced mains; corrected to exact accompaniment names on RECIPE/GOODS). `ListItems ?include_non_billable=1` lets supplies (tissue/packaging) through the type filter; pos-api forces price 0 + Free flag + clears price-band guardrails (`c0a84be`); order lines carrying the `non_billable` metadata marker are zeroed server-side (belt) — verified LIVE: a 150×2 flagged line produced a 0.00 order. pos-ui shows FREE chips (grid + cart) and pins free lines to 0 across tier switches; inventory-ui item form gained the Non-billable checkbox (`f483989`).
- **Demo seed** (`14140f7`): the deploy-time demo seeder prunes non-seeded SKUs (an API-created test item was wiped by the next deploy) — so Ugali [ACC] + Steamed Greens [ACC] now live in the seed under a new "Accompaniments" category (name matches the terminal's accompaniment-tab matcher), flagged via a `non_billable` tag.
- **urban-loft note**: its ugali accompaniment (if named exactly "Ugali"/"Ugali [ACC]") is flagged by the corrective migration; if the item doesn't exist there, create it in inventory-ui and tick "Non-billable".
