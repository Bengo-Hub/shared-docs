# KRA eTIMS demo guide (OSCU integrator)

Read this before the KRA demonstration. It covers what the KRA team looks at, the order to show
things in, the code and architecture questions to expect, what to do if the sandbox misbehaves,
and how to make any eTIMS call by hand from Postman.

It builds on these treasury-api documents and does not repeat them:

- `finance-service/treasury-api/docs/kra-etims-demo-runbook.md`: the click path for each flow
  (written before the 2026-10-31 tax menu change; use the menu paths in this guide).
- `finance-service/treasury-api/docs/architecture/tis-etims-technology-architecture.md`: the
  architecture document submitted to KRA (and its PDF in the same folder).
- `finance-service/treasury-api/docs/architecture/tis-etims-demo-presentation.md`: the slides.
- `finance-service/treasury-api/docs/kra-oscu-automated-testing-runbook.md`: the certification history
  and every KRA error we have hit, with its cause.
- `finance-service/treasury-api/docs/kra-etims-postman-collection/Codevertex-Treasury-eTIMS.*.json`:
  the Postman collection and environment for every treasury-api eTIMS endpoint (section 10).

## 1. Where we stand

| Item | State |
|---|---|
| Certification | 23 of 23 passed on 2026-10-16, app `etims-oscu-cert-app-ts01`, device `CV-P052543168K-TS01`, branch 00 |
| Go-live copies | Invoice INV-261016-000102 (invcNo 209) and credit note CN-000030 (invcNo 210); download the PDFs from each document in treasury |
| Taxpayer | Codevertex Africa Limited, PIN P052543168K, branches 00 and 01 |
| Demo tenant | `codevertex-demo` on books.codevertexafrica.com (treasury) and pos.codevertexafrica.com (POS) |
| Test buyer | CRM contact "Test Customer", PIN P318295670X |
| Route | Real traffic goes straight to `etims-api-sbx.kra.go.ke/etims-api` with the device `tin`, `bhfId` and `cmcKey` headers. The certification wizard alone uses the GavaConnect proxy, because the portal only scores that route |
| Auto send on codevertex-demo | On as of 2026-11-12: sending an invoice or raising a credit note signed it with KRA at once in every run below. **Transmit to eTIMS** stays for a document that failed, and a POS sale still needs **Generate ETR receipt** (section 4, step 5) |
| Environment | Both demo devices on sandbox. Production go-live is a per-device switch that has not been used |
| Signing channel | OSCU only on codevertex-demo (checked 2026-11-11) |
| Live check 2026-11-11 | Branch 00 counter 220 equals KRA's latest sale; branch 01 at 86; 51 of 51 documents in 30 days signed. The 11 dead letters in full history date from 22 September to 10 October, the GavaConnect proxy outage before the direct route; say so if the Dead letter filter is opened, and do not requeue them |

## 1a. What changed after the 2026-11-11 review, and the proof

I fixed every point the KRA team raised on 2026-11-11 and deployed the fixes on 2026-11-12
(treasury, inventory, POS and SSO, back end and screens). The same evening I ran each review
scenario on codevertex-demo, branch 01 (sandbox), and read every document back from KRA's own
receipt page. Every total, every tax amount and every tax band matched to the cent.

| Scenario | Our document | KRA receipt | Result |
|---|---|---|---|
| Goods in all five bands, A to E | INV-261112-000121 | KRACU0400001232/95 | A, B, C, D and E all shown; 4,135.68, tax 199.68 |
| Services only, bands A to E | INV-261112-000122 | branch 01 | 2,620.00, tax 120.00 |
| Goods and services mixed, a 10% and a 7.5% line discount, flat line discounts, a 50.00 document discount | INV-261112-000123 | branch 01 | 3,356.52, tax 159.35 |
| Recipe items (no stock of their own) | INV-261112-000124 | branch 01 | 679.30, tax 93.70; no out of stock error |
| First partial credit note (1 of 2 on two lines) | CN-000046 | KRACU0400001232/99 | B and D, minus 611.20, tax minus 51.20, against receipt 95 |
| Second partial credit note on the same invoice | refused | | 409 with KRA's rule: one partial per invoice, then credit everything left |
| Credit for everything left, part quantities included | CN-000047 | branch 01 | A to E, 3,524.48, tax 148.48 |
| A further credit note once nothing is left | refused | | "nothing is left to credit" |
| Half paid invoice credited in full, the paid half refunded by M-Pesa | INV-261112-000126, CN-000049 | branch 01 | 1,972.00 both; 986.00 recorded as refunded by M-Pesa, with its own journal entry |
| Print copy | INV-261112-000121 PDF | | Original prints NS with no COPY mark; the Print copy button prints COPY and CS |

Points to say when showing these:
- KRA's receipt page prints bands C and D as "TAX C" and "TAX D", and A, B and E as "A-EX",
  "B-16%" and "E-8%". This is KRA's layout, not ours.
- A credit note's time on KRA's page reads twelve hours off (CN-000046 shows 10:39 for a note
  raised at 22:39 EAT). This is the sandbox refund time display we have already reported.
- A discount on the whole document reaches KRA shared across the lines, because KRA has no
  document discount field, only a discount per line. On INV-261112-000123 the 50.00 document
  discount puts 11.09 on the hair set (KRA shows 822.34), 7.70 on demo service 3 (492.30, still
  band C) and so on. Since 2026-11-13 our PDF and screens print each line the same way: the
  SUBTOTAL and AMOUNT columns take the line's share off, a grey note under the description names
  the share, and the lines add up to the grand total exactly as KRA's do.
- Check on 2026-11-13: of the 47 documents codevertex-demo signed in the 30 days before, 44 match
  KRA's receipt page line by line. The three that do not (INV-261111-000112, its credit note
  CN-000041, INV-261111-000118) were signed during the 11 November demo, before the discount fix,
  when a line discount went to KRA as a rounded whole percent. Signed records cannot be edited,
  so they stay as the record of the bug that was fixed.
- KRA's receipt page prints each line with its VAT included; the tax band table on our
  document shows the taxable value without VAT. They reconcile line by line: B 822.34 less VAT
  113.43 is the 708.91 in our B row, E 619.94 less 45.92 is 574.02.
- The DISC column shows "10%" for a percentage discount and the amount for a flat one; the
  rate and the amount it came to are in grey under the description.
- Every date we send KRA is now East Africa Time, whatever the server clock says.
- A discount KRA can't hold as a whole percent goes over as the net price, and where that price
  needs more than two decimals the line is split into two lines with the same item code, so the
  line totals agree with ours exactly.
- An item's band comes from the line's tax code. When it differs from the band the item was
  registered with, the item is re-registered with the new band before the sale goes over.
- One signing unit per branch: a branch with an OSCU device refuses a VSCU set-up, and the
  other way round.
- Customer copies say COPY only when printed with the Print copy button; a plain print or a
  download stays the original.
- Document lists show the SCU invoice number and filter by date and time, number, SCU number,
  customer and amount. Credit notes show the SCU numbers on top and the TIS numbers, with the
  original invoice's number, in the box at the bottom.
- Queued sales that miss a period go into the next period, inside KRA's six month window.

## 2. Run sheet for the day

The tax pages now sit in the treasury sidebar under **Tax**, in three groups: Compliance
(Overview, Rates and deadlines, Tax settings, Tax codes, KRA lookups), Returns (VAT return,
Withholding, ...) and eTIMS (Devices, Items, Sync with KRA, Transmissions, Branch tools,
Certification). The old "Tax & Compliance" tabs are gone; old `?tab=` links still redirect.

**One hour before, read-only checks.** Nothing here creates data at KRA. The Postman folder
**01 Demo readiness** runs the same checks (section 10).

1. Sign in to books.codevertexafrica.com as the demo admin and open the codevertex-demo org. In
   the top bar, set the outlet to **All outlets**. The Transmissions page follows the selected
   outlet, and with a branch 01 outlet selected the branch 00 go-live copies are hidden.
2. Tax, eTIMS, **Devices**. The activation card shows all four steps green and both devices
   active (branch 00 and branch 01). Both must say **Sandbox**. If one says Live or Mixed, stop
   and investigate before the demo: the invoice counter is kept per PIN, branch and environment.
3. Tax, **Tax settings**, eTIMS connection: eTIMS on, Auto send off, signing channel OSCU only,
   Mode Sandbox. Change nothing. OSCU only is deliberate for the demo: no VSCU unit is provisioned
   and KRA has not yet ruled on OSCU and VSCU sharing a branch (section 12).
4. Tax, eTIMS, **Transmissions**: invcNo 209 and 210 show as transmitted, each with a CU number.
5. Open invoice INV-261016-000102. The KRA eTIMS panel shows the CU invoice number, the signature
   and the QR. Download the PDF once to make sure the docs engine answers.
6. Tax, eTIMS, **Certification**, run the **Select Invoice Details** lookup for 209. It is a read
   call and proves the sandbox answers.
7. Open pos.codevertexafrica.com on the branch 01 outlet and check that the till loads its
   catalogue.
8. Check that the two items planned for the demo sale are registered (Tax, eTIMS, Items, badge
   Registered) and carry a tax code.
9. The dashboard shows KRA's current notices in a banner. Open one with **Read the full notice**;
   it lands on Tax, eTIMS, Branch tools with that notice highlighted. Notice 12 (the new
   `/initialize` path) is a good opening for the questions in section 12.

If step 6 times out, KRA's sandbox is slow. Try once more after five minutes. If it still fails,
plan to use the fallback in section 8.

**Thirty minutes before, set up the screen.** Open these tabs, in this order:
1. Tax, eTIMS, Devices.
2. Tax, eTIMS, Items.
3. Invoices.
4. Tax, eTIMS, Transmissions.
5. Tax, eTIMS, Sync with KRA.
6. Transactions (for Generate ETR receipt on the POS sale).
7. The POS till.
8. Tax, eTIMS, Certification (history card at the top).
9. The architecture PDF.
10. This guide, and Postman with the collection loaded if you plan to show the API.

Close everything else and turn off notifications.

**Agenda (about 45 minutes).**
1. Two minutes on who we are and the product (one fiscalisation point for POS, invoicing and
   purchases).
2. Five minutes of architecture, using the PDF diagram.
3. Twenty minutes of live walkthrough (section 4).
4. Fifteen minutes of questions (section 5).
5. Close with the evidence list (section 7).

## 3. What the KRA team looks at

KRA does not publish a demo checklist. Their public pages list only what goes in the application:
- the company documents;
- proof of three qualified technical staff;
- the bio-data form;
- the architecture document;
- the software on read-only media.

The list below comes from our two certification rounds, the go-live rejection of 2026-09-27 and
the OSCU specification. Expect them to check each point.

1. **Device setup.** The device is bound to the right PIN and branch, and initialisation returns a
   CMC key. A second initialisation gives 902 ("already installed"), which is normal.
2. **Code lists and item classes.** They are pulled from KRA, not typed in. Forms use KRA's codes
   for class, package unit, quantity unit and tax type.
3. **Item registration.** `itemCd` follows KRA's format (origin, type, package unit, quantity unit,
   sequence). The item type matches the product: 1 raw material, 2 finished good, 3 service.
4. **The receipt itself.** This is where the 2026-09-27 rejection came from. A fiscal invoice must
   show:
   - the CU invoice number (SCU ID / invcNo);
   - the receipt signature and internal data;
   - the QR code, which must resolve on KRA's side;
   - the date and time KRA signed it;
   - a tax band table;
   - the buyer PIN;
   - at least two items.

   A proforma must be clearly marked as not fiscal.
5. **Credit notes.** A refund (`rcptTyCd R`) refers to the original invcNo, carries a reason code
   and the buyer PIN, and cannot credit more than was sold.
6. **Invoice number control.** invcNo is sequential per device branch and never reused. Expect a
   question on how two servers are kept from taking the same number; the answer is in section 5.
7. **Stock.** Each stock movement maps to one KRA stock reason, and the stock master matches
   what the system holds.
8. **Purchases.** Supplier sales are pulled from KRA and confirmed against bills, and purchases
   are sent with the right receipt type.
9. **Failure handling.** What the cashier sees when KRA is down, how the sale is kept and sent
   later, and how an operator finds and fixes a stuck document.
10. **Tax bands.** A is exempt, B is VAT 16, C is zero rated, D is non-VAT and E is VAT 8.
    Totals per band must add up to the header.
11. **Segregation.** One taxpayer can never see or sign with another taxpayer's device.

## 4. Live walkthrough script

Use the Test Customer for every buyer. Never type a free-text customer name: KRA rejected those
copies before. Use branch 01 for live sales so branch 00 keeps the clean go-live sequence.

**Branch 01 needs an outlet.** A treasury invoice signs on the device of its own outlet, and an
invoice with no outlet signs on the main device, which is branch 00. Before raising the demo
invoice, pick the outlet mapped to branch 01 in the top bar and check that the new invoice shows
that outlet. Then switch the top bar back to All outlets when showing Transmissions.

1. **Activation (2 min).** Open Tax, eTIMS, Devices and walk through the activation card (PIN,
   device, CMC key, entitlement). Point out that the CMC key is masked. Do not press Initialise
   again, and do not touch **Go live** on either device (section 9).
2. **Code lists (1 min).** Tax, eTIMS, Sync with KRA shows the lists pulled from KRA. Then open
   the item class dropdown in the Register item form on Tax, eTIMS, Items.
3. **Register an item (3 min).**
   - Go to Tax, eTIMS, Items and choose Register item.
   - Leave the code blank so the server mints it.
   - Pick a real class and band B. The class can come from the item's category; the table shows
     where each class came from.
   - Show the new row with its `itemCd` and the Registered badge.

   This step creates data at KRA, so agree it in advance.
4. **Sale with two items (5 min).**
   - Raise an invoice to the Test Customer with two registered items, one band B and, if possible,
     one band D, on the branch 01 outlet.
   - Send it, then press **Transmit to eTIMS**.
   - Show the CU number, signature and QR on the invoice.
   - Download the PDF and show the SCU information block and the band table.
   - Scan the QR on a phone.
   - Optional: the VAT on the invoice, in the books and in what KRA received now come from one
     shared calculator, so they agree to the cent. Tax, VAT return shows books, ledger and eTIMS
     side by side.
   - Discounts: a line can take a percentage or a flat amount, and the document a global discount.
     The PDF shows each discount as given (a flat amount, or "10% (40.00)"), with SUBTOTAL and VAT
     columns, and KRA's receipt page shows the same line totals as ours (since 2026-11-12, runbook
     section 3.39). I run one discounted sale on branch 01 on the morning of the demo and compare it
     with KRA's QR page before showing one.
5. **POS sale (3 min).** Ring up two items on the branch 01 till and take payment. Because auto
   send is off on this tenant, the receipt prints **unsigned** at the till; this is by design and
   the sale is queued, not lost. Then in treasury open **Transactions**, find the sale, open it
   and press **Generate ETR receipt**. Reprint the receipt from the POS order history to show the
   KRA block. Say on screen that a tenant with auto send on gets the signed receipt at checkout.
6. **Credit note (3 min).**
   - From the invoice, choose Credit Note, then Pick items to credit, and credit one line.
   - Transmit it and show `rcptTyCd R` with the original invcNo.
   - Show that crediting more than the remainder is refused.
7. **Transmissions and audit trail (2 min).** On Tax, eTIMS, Transmissions (top bar on All
   outlets), open a row to show its status, eTIMS invoice number, KRA receipt number, CU number,
   signature, retry count, signing channel, the sale's outlet and the signing device's outlet,
   plus the Retry and Requeue actions. KRA's full reply is shown on the invoice itself, in the
   window that opens after **Transmit to eTIMS**.
8. **Reconciliation (1 min).** Show Tax, eTIMS, Sync with KRA comparing KRA's sales list with our
   records.

Purchases and stock are slower to show live, and KRA's sandbox has been failing `insertStockIO`
for our own PIN with an OutOfMemoryError (section 12). Describe them from the stock mapping table
in the demo runbook and show the ledger rows on Sync with KRA instead.

## 5. Code and architecture questions

### Where the code lives

The KRA integration is in treasury-api, module `internal/modules/tax`.

| Concern | File |
|---|---|
| HTTP client, every OSCU call, payload shapes | `kra_client.go`, `kra_client_oscu_ext.go`, `kra_client_oscu_branch.go` |
| Direct host versus GavaConnect routing | `kra_routing.go` |
| Platform and tenant on/off switches | `etims_switch.go` |
| Signing channel (Automatic, OSCU, VSCU) | `etims_channel.go`, `vscu_routing.go` |
| OAuth token handling for GavaConnect | `gavaconnect_client.go` |
| Device registration, initialisation, CMC key | `service.go`, `service_etims_device_init.go` |
| Sandbox to production per device | `device_environment.go` |
| Code lists and item classes | `service_etims_codelists.go` |
| Item registration and `itemCd` | `service_etims_items.go`, `etims_item_classify.go`, `item_seq_lock.go` |
| Sales, invcNo allocation, duplicate handling | `service_etims_stock.go`, `invcno_order.go`, `invcno_duplicate.go`, `kra_sequence_reconcile.go` |
| Money rounding at the KRA boundary | `kra_money.go`, `pos_line_figures.go` |
| POS sales and refunds | `service_pos_etims.go`, `refund_split.go` |
| Stock IO and stock master | `service_etims_stock.go`, `stock_subscriber.go`, `stock_ledger_claim.go`, `service_etims_stock_reconcile.go` |
| Purchases | `purchase_match.go`, `purchase_adjustment.go`, `service_etims_expense.go` |
| Background transmission and retries | `worker.go` |
| Reconciliation with KRA | `service_etims_reconcile.go`, `vat_return_etims.go` |
| Certification runner | `certification_runner.go`, `service_certification.go` |
| VSCU (local signing unit) | `vscu.go`, `vscu_offline.go` |

The VAT formula itself lives in the shared Go module `httpware/tax` (and its twin in
shared-ui-lib), so invoices, POS, ordering and eTIMS compute the same figures.

The front end is treasury-ui, under `src/app/[orgSlug]/tax/etims/*` (devices, items, sync,
transmissions, branch tools) and `tax/etims-certification` (the 23-step wizard).

### Likely questions and short answers

**How does a sale reach KRA?** Every source (an invoice, a POS sale, an online order) ends at one
function in treasury that builds the OSCU sales payload and sends it. POS and ordering never talk
to KRA themselves. A finished sale either goes straight away (Transmit, or POS checkout) or is
queued and picked up by the worker within about 30 seconds.

**What stops two servers from issuing the same invoice number?** The number is taken inside a
database transaction that locks the device rows for that PIN, branch and environment (`SELECT ...
FOR UPDATE`), so sends for one branch go one at a time across all pods. The number is stored on
the record before the call, and a unique index stops a document being queued twice.

**What if KRA times out after it actually accepted the sale?** On retry, KRA answers that the
invoice number already exists. We then read KRA's own copy of that sale, compare it with ours, and
if it is the same sale we record KRA's receipt rather than sending again. If it is a different
sale, we move to the next free number. The counter also follows KRA's latest signing time, so it
heals after any gap.

**What happens when KRA is down?** The sale completes and the customer gets a receipt marked
pending. The document stays queued and the worker tries it three times, waiting 2 and then 4
minutes between attempts. After that it goes to a dead-letter list where an operator can requeue
it from the Transmissions screen, inside KRA's 48-hour offline window. Nothing is lost, and a
resend that KRA already holds is matched to KRA's copy rather than signed twice.

**How do you store the CMC key?** It is encrypted with AES-256-GCM using a key held in a Kubernetes
secret, never in code. API responses show it masked, and revealing it needs a manage permission.

**How is one taxpayer kept from another?** Each tenant's data carries its tenant id, and every
query filters on it. A device belongs to one tenant and one PIN, and a device can only be
registered for the PIN on the tenant's own tax profile. Users sign in through our identity
service with signed tokens (RS256), and permissions come from their role. Internal calls between
our services use a separate service key.

**Do you use the GavaConnect proxy or the eTIMS host?** Live traffic goes to the eTIMS host
directly with the device headers. The certification wizard uses GavaConnect with OAuth, because
that is the route the portal scores.

**How does a taxpayer go live?** Following KRA's OSCU/VSCU step-by-step guide: the taxpayer files
a service request on the production portal (PIN, branch, serial), then each device is switched in
place with **Go live**. That takes the approved serial, initialises on the production host to get
the production CMC key, restarts the invoice counter at the number KRA confirms, and keeps sandbox
records apart (they are never resent). Code lists and items are then registered again in
production. KRA's production approval is a manual step on their side.

**How do you handle tax bands and rounding?** We follow KRA's band letters (A exempt, B 16, C zero,
D non-VAT, E 8). Unit prices are VAT inclusive, the taxable amount is the supply divided by one plus
the rate, and every amount is rounded to two decimals at the point where it leaves our system. Band
totals are summed from the rounded lines, so the header always matches. A document discount is
shared across the lines before VAT, the same way in the books and in eTIMS.

**What if the taxpayer is not VAT registered?** The tenant's tax obligations decide. A non-VAT
tenant registers and sells everything as band D with no VAT, and VAT-only screens are hidden.

**How do returns from the till reach KRA?** A POS return sends the returned lines, outlet and the
original order to treasury. Treasury raises a credit note that refers to the original invcNo and
sends it as a refund, splitting each line by the band the item was registered under. An exchange
is a credit note plus a new sale at full price, so KRA never sees the returned value taken off
twice.

**How do you keep stock in step with KRA?** Every stock movement in inventory raises an event.
Treasury maps it to one KRA stock reason (sale out 11, purchase in 02, return in 03, adjustment in
06, adjustment out 16, return to supplier 12). It claims a ledger row keyed on the source movement
before calling KRA, so a movement is sent once even if two pods receive it. The stock master
quantity follows the running stocked-in total.

**Can a user edit a fiscalised invoice?** No. Only a draft can be edited, and a draft is never
sent to KRA. Once an invoice is issued, corrections go through a credit note and a new invoice.

**What about offline tills?** POS keeps sales offline and syncs them when back online with an
idempotency key, so a resent sale is not created twice. Treasury fiscalises it once it arrives.

**Do you support VSCU?** Yes, as a second channel next to OSCU. A business picks the channel in
Tax settings: OSCU only, VSCU only, or automatic, which uses OSCU and moves a sale to the branch's
VSCU unit only when OSCU could not be reached at all. VSCU calls follow KRA's VSCU Specification
v2.0 path names. Both channels take invoice numbers from the same branch counter under the same
lock, so they never reuse a number, and a slow OSCU answer is retried rather than signed again on
VSCU. No customer runs a VSCU unit yet. If asked whether one branch may run both an OSCU and a
VSCU device, say we will follow KRA's ruling; we have asked.

**Which tech stack?**
- Go services with the Ent ORM and Atlas versioned migrations.
- PostgreSQL behind PgBouncer, Redis, and NATS JetStream for events.
- Next.js front ends.
- Kubernetes with ArgoCD, NGINX ingress, cert-manager, and Cloudflare at the edge.

Treasury runs at least two replicas with a disruption budget and autoscaling.

**How do you test?** Unit tests pin each payload rule (bands, rounding, refund dates, credit lines),
and the VAT calculator has shared test vectors run in both Go and TypeScript. A scripted
certification suite replays all 23 cases against the sandbox, and the wizard runs the same cases
from the UI. Every transmission keeps the request and KRA's response for audit.

**How do you deploy and roll back?** Each merge builds an image tagged with the commit. ArgoCD rolls
it out pod by pod, and rolling back means pointing at the previous tag. Database changes are
versioned migrations applied at start-up.

**What logs and monitoring are there?** Structured logs with a request id on every call, health
probes, and per-document status with KRA's result code. Failed and dead-lettered documents show on
the Transmissions screen.

**How do you onboard a new taxpayer?** Enter the PIN in Tax settings, register the device with
its serial and branch, initialise to get the CMC key, refresh code lists, then register items. The
activation card shows each step. Until all four are green, no document is sent to KRA.

**Can third parties use your integration?** Yes. An external eTIMS API takes an API key scoped to
eTIMS, with per-plan rate limits and usage billing. It goes through the same fiscalisation code.

**What are the known limits?** Answer these honestly if asked:
- VSCU is built but not provisioned for any customer.
- The debit note path (`rcptTyCd D`) has not been run live.
- Tenant isolation is enforced in the application layer, not with database row-level security.
- Production item codes follow KRA's per-PIN sequence; the self-correction is proven in the
  sandbox only.

### Before the demo, know these points about your own system

- Auto send is off on codevertex-demo, so you press Transmit (invoices) or Generate ETR receipt
  (POS). Say so on screen instead of waiting for the worker. Turning auto send on just for the
  demo is not recommended: the worker would then send every record still queued on the tenant.
- KRA's GavaConnect proxy timed out (504 after 20 seconds) from 2026-09-24. That is why live
  traffic goes direct. If they ask about the earlier rejection, the cause was that our attached
  invoice never fiscalised while the proxy was failing. It has been fixed since 2026-10-13.
- Set the tax code on band D items before selling them in the demo.

## 6. Evidence to have ready

- The certification history on the demo tenant: Tax, eTIMS, **Certification**, the
  **Certification history** card at the top of that page. Click a run to open its 23 cases.
  The 2026-10-16 run shows 23 of 23, run by admin@codevertexafrica.com, with each step's result.
  The two earlier runs on 2026-09-22 (1 and 12 of 23) are older attempts.
- The go-live invoice and credit note: open INV-261016-000102 and CN-000030 in treasury and
  download the PDFs. `d:\tmp\etims-go-live` holds the later mixed band copies (INV-261016-000103 and
  000105, CN-000031 and 000033), not 209 and 210.
- The architecture PDF, `Codevertex-TIS-eTIMS-Technology-Architecture.pdf`.
- The submission pack in `finance-service/treasury-api/docs/kra-submission` (registration, CR12,
  TCC, staff, declaration of solvency, bio-data form).

## 7. Closing evidence list

Certification 23/23 with per-case history, the go-live invoice and credit note with working QR,
the live sale and credit note from today, and the Transmissions audit trail.

## 8. If something goes wrong

| Symptom | What to do |
|---|---|
| A KRA call hangs for 20 seconds then fails | Sandbox is slow. Say so, show the queued document on Transmissions, and move on to the next flow. Come back to Retry later |
| "Invalid invcNo" or "already exists" | Expected after a gap. Press Retry once; the counter heals itself. Explain the duplicate handling from section 5 |
| 902 on initialise | Normal, the device is already installed. Do not repeat |
| POS receipt has no KRA block | Auto send is off. Generate ETR receipt from Transactions, then reprint |
| Invoice receipt has no KRA block | The send has not finished. Wait for the page to refresh, or open the invoice from Transmissions |
| "the invoice has no outlet, so its KRA branch can't be resolved" | Raise the invoice with the branch 01 outlet selected |
| Transmissions looks empty | The top bar outlet filters it. Switch to All outlets |
| A KRA notice link opens a 404 page | KRA's own notice pages (`etims-sbx.kra.go.ke/.../indexEbmNotice`) answer 404 on KRA's side (checked 2026-11-11). The dashboard banner now opens the full notice in Tax, eTIMS, Branch tools instead |
| The sandbox is down entirely | Show the 23/23 certification history, open the go-live invoice and credit note, scan their QR, and open their rows on Transmissions to show the CU number, signature and receipt KRA returned |

## 9. Do not do during the demo

- Do not initialise a device again or change its invoice counter.
- Do not press **Go live** or **Back to sandbox** on a device. It drops the CMC key, restarts the
  counter and holds every unsent record as a dead letter.
- Do not change Mode in Tax settings, or the GavaConnect Sandbox/Production switch on the
  platform page.
- Do not switch the platform or tenant eTIMS switch off, and do not turn auto send on.
- Do not use branch 00 for test sales (keeps the go-live sequence clean).
- Do not open server logs, the database, Postman environment values, or anything showing keys or
  tokens on the shared screen.
- Do not promise dates for VSCU or production go-live. Say they follow KRA approval.

## 10. Postman collection

Two files in `finance-service/treasury-api/docs/kra-etims-postman-collection/`:

- `Codevertex-Treasury-eTIMS.postman_collection.json`: 121 requests covering every eTIMS endpoint
  treasury-api exposes.
- `Codevertex-Treasury-eTIMS.postman_environment.json`: the variables, all empty except safe
  defaults. Real values go in the **current value** column only, which Postman keeps on this
  machine; never in the initial value, and never committed.

KRA's own collections in the same folder call KRA directly with a CMC key. This one calls
treasury-api, so every request runs through the same code, locks, counters and audit trail as
the UI. That is why it is the safer choice for manual calls.

**Setup.** Import both files and pick the environment. Fill `token`: copy the access token from a
signed-in treasury tab (paste it, never retype a token), or run **00 Sign in, Login**, which saves
it. Run **01 Demo readiness, List devices**; it saves the first device id in `device_id` and
prints each device's branch, environment, last invcNo and last sarNo in the Postman console.

**Folders.**

| Folder | What it is for |
|---|---|
| 00 Sign in | Login that stores the token |
| 01 Demo readiness | The read-only checks of section 2 |
| 02 Certification | The 23 OSCU functions in the wizard's order, plus the automated run (start, list, poll), the same engine as `run_certification.py` |
| 03 Devices and setup | Register, initialise, outlet, integration, counter sync, catalogue sync |
| 04 Items and code lists | Register items, bulk, stock master, cached code lists |
| 05 Sales, credit notes and receipts | Transmit a document, Generate ETR receipt, fiscal evidence, raw credit note |
| 06 Stock | Raw stock IO, stock move list |
| 07 Transmissions and retries | List and retry |
| 08 Purchases and imports | Supplier sales, transmit a bill, imported items |
| 09 Branch data and lookups | Branch customer, user, insurance, composition, customer PIN |
| 10 Reconciliation | Books against KRA (Smart Tax plan feature) |
| 11 Platform owner | KRA config status and reload, GavaConnect app tests |
| 12 External eTIMS API | The API-key surface for third-party integrators, including the sandbox simulator |
| 13 Service to service | What pos-api calls (internal key) |

**Naming.** `[KRA WRITE]` requests create data at KRA and use up sequence numbers. `[DANGER]`
requests change numbering or credentials and are never for a demo.

**Three rules that trip people up.**
1. The branch comes from `outlet_id` (sent as the `X-Outlet-ID` header). Empty means the main
   device, branch 00. Put the branch 01 outlet's id there for test traffic.
2. The certification folder sends `X-Etims-Certification: 1` so calls go through GavaConnect, the
   route KRA's portal scores. treasury-api honours that header only for a platform-owner token.
   Set `cert_route` to 0 to send the same calls direct.
3. A platform-owner token reaches another tenant only when `tenant` holds that tenant's UUID. With
   a slug it silently falls back to the token's own tenant.

**Permissions.** Reads need treasury ledger or config view. Writes need change or manage. Device
setup and certification runs need config manage or ledger manage (the tenant admin role has
ledger manage).

## 11. Field reference for manual calls

Most fields are filled by the server when a call goes through treasury-api. The ones below are
the ones a person has to supply or understand when calling by hand.

### Dates

| Field | Format | Where it comes from |
|---|---|---|
| `last_req_dt` (query) | `yyyyMMddHHmmss`, 14 digits | A cursor for KRA's list calls: KRA returns only records changed after it. `20240101000000` returns everything. KRA answers resultCd 001 ("no data") when nothing changed, which is not an error. Any other length is refused with 400 |
| `ocrnDt` (stock IO) | `yyyyMMdd` | The date the stock actually moved. Usually today |
| `salesDt` | `yyyyMMdd` | Set by the server from the invoice date. Kept from the first attempt on every retry, so a retry on a later day does not look like a new sale |
| `cfmDt`, `stockRlsDt` | `yyyyMMddHHmmss` | Set by the server at send time |
| `lastReqDt` (query, Reconciliation only) | `yyyyMMddHHmmss` | Same meaning as `last_req_dt`; that one endpoint spells it in camel case |

### Sequence numbers

| Field | Scope | How to derive it |
|---|---|---|
| `invcNo` | One counter per PIN, branch and environment | Never typed by hand. treasury-api takes the next one under a row lock when a document is transmitted. If KRA disagrees, treasury reads KRA's copy and heals. To see the current value, look at `last_invoice_no` in List devices; to pull it forward from KRA, run **Sync invoice counter from KRA** |
| `orgInvcNo` / `org_invc_no` | The sale being credited | The `invcNo` of the original sale, from its Transmissions row or its fiscal evidence. 209 is the go-live invoice |
| `sarNo` | One counter per PIN in treasury-api. KRA has not confirmed whether its scope is the PIN or the branch (section 12) | Required on the raw stock IO call, which does not allocate it. Take the highest `last_sar_no` across the devices in List devices and add 1. If it is wrong, KRA answers `Invalid sarNo: Expected: N`; send again with N. A raw stock call does not move treasury's own counter, so the next automatic stock send gets the same correction from KRA and heals itself with one extra round trip |
| `orgSarNo` | The stock movement being corrected | 0 for a new movement. For an adjustment of an earlier movement, that movement's sarNo |
| `itemSeq` | Line number inside one request | 1, 2, 3 in order |

### Codes

Every code below is in the cached code lists: **04 Items and code lists, Cached code lists** with
`type` set to the name in brackets. Item classes are a separate list (**KRA: item class list**).

| Field | Values | Notes |
|---|---|---|
| `taxTyCd` / `tax_ty_cd` (TAX_TY) | A exempt, B VAT 16, C zero rated, D non-VAT, E VAT 8 | Must match the band the item was registered with |
| `itemTyCd` / `item_ty_cd` (ITEM_TY) | 1 raw material, 2 finished good, 3 service | |
| `pkgUnitCd` (PKG_UNIT) | e.g. NT, CT, BX | Two characters |
| `qtyUnitCd` (QTY_UNIT) | e.g. NO (number), KG | Two characters; it is part of the itemCd. KRA's list also has 1-character codes such as U (pieces) that the item code cannot carry; since 2026-11-11 the pickers hide them and treasury sends NO instead |
| `itemClsCd` | 10 digits from the item class list | treasury uses the item's own class, else its category's, else the nearest parent category's. `1000000000` is the general fallback; avoid it for real items |
| `sarTyCd` (SAR_TY) | 02 purchase in, 03 return in, 06 adjustment in, 11 sale out, 12 return to supplier, 16 adjustment out | One reason per movement |
| `regTyCd` | M manual, A automatic | M for a call typed by hand |
| `rfdRsnCd` / `rfd_rsn_cd` (RFD_RSN) | KRA's refund reasons | 06 ("other") is the default when none is given |
| `rcptTyCd` (RCPT_TY) | S sale, R refund (credit note), D debit note | Set by the server from the document type |
| `pmtTyCd` (PMNT_TY) | 01 cash, and others for credit, card, mobile money | Set by the server from the tenders |

### The item code

`itemCd` is the 2-letter origin country, the item type, the package unit, the quantity unit,
then an 8-digit sequence that is the next number for the PIN. Example: `KE2NTNO00000012` is a
Kenyan finished good, packaging NT, unit NO, item number 12. Leave `item_cd` empty when
registering and treasury mints it under a per-PIN lock. KRA rejects a code that was already
sent, so never re-send an existing one to change an item.

### Amounts on a line

Prices are VAT inclusive. For one band B line of quantity 1 at 1,160:

- `prc` 1160 and `splyAmt` = `prc` x `qty` = 1160.
- `taxblAmt` = 1160 / 1.16 = 1000.00 (rounded to 2 decimals).
- `taxAmt` = `splyAmt` - `taxblAmt` = 160.00.
- `totAmt` = 1160.
- Bands A, C and D have `taxAmt` 0 and `taxblAmt` equal to the line total. Band E uses 1.08.
- A line discount goes in `dcRt` (percent) and `dcAmt`, and is taken off before the split.
- The header totals (`totTaxblAmt`, `totTaxAmt`, `totAmt`) are the sums of the rounded lines.

These hand figures matter only for the raw stock IO and raw credit note calls. For invoices and
POS sales, treasury computes them from the document.

### Fields the server always fills

`tin`, `bhfId`, the CMC key header, `regrId`/`regrNm`/`modrId`/`modrNm` (the eTIMS user),
`totItemCnt`, `invcNo`, `salesDt`, `cfmDt` and the customer block of a treasury document. Values
typed for these on a treasury-api call are replaced.

## 12. Questions and facts to confirm with KRA

Collected from the earlier demo, certification and tax plans and the project memory. Raise them
at the end of the demo or in the follow-up email. Each line says what we do until KRA answers.

### Sandbox problems to report

1. **`insertStockIO` fails for our own PIN.** Every stock movement for P052543168K, on both
   branches, returns `Handler dispatch failed: java.lang.OutOfMemoryError: Java heap space`
   after 15 to 20 seconds, whatever the payload. Still true on the 2026-10-16 run; the
   certification passed stock, composition, sale and purchase only through the session's
   Application Test Pin. Request IDs are in the testing runbook, section 3.30.2. Ask them to fix
   it, or to confirm it is a sandbox fault that production does not share.
2. **GavaConnect proxy timeouts.** From 2026-09-24 the proxy returned 504 after about 20 seconds
   while the direct eTIMS host answered. Live traffic now goes direct, but the portal still scores
   certification only through the proxy. Ask them to raise the proxy timeout, or to accept
   direct-route evidence for scoring.

2a. **Notice 12, "OSCU Initialization path suffix: /initialize"** (posted 2026-11-05, with a sample
   body `tin`, `bhfId`, `dvcSrlNo`). On 2026-11-11 I probed both direct hosts: `/initialize`
   answers 404 on `etims-api-sbx` and `etims-api`, while `selectInitOsdcInfo` still answers. Ask
   which route the new path belongs to (the GavaConnect proxy, or a coming release of the direct
   host), when `selectInitOsdcInfo` stops working, and whether the response changes. Until then
   device initialisation keeps `selectInitOsdcInfo` (`kra_client.go`, `SelectInitOsdcInfo`).
2b. **Notice detail links.** Every `dtlUrl` in the notice list answers 404 (a page titled "MyRRA").
   Ask them to fix the links. We show the full notice text in our own Branch tools page.

### Rules we have assumed and want confirmed

3. **One branch running OSCU and VSCU together.** Our Automatic channel needs an OSCU and a VSCU
   device on the same branch. Ask whether that is allowed, and whether a VSCU unit accepts an
   invoice number that OSCU did not issue (both share one branch counter in our design). Until
   then, Automatic with two devices is documented as needing KRA's approval.
4. **Scope of `sarNo`.** `invcNo` was confirmed per PIN and branch on 2026-09-24. KRA has never
   told us the scope of the stock `sarNo`, because the OutOfMemoryError comes back before any
   "Expected N" hint. We keep one counter per PIN and will switch to per branch if KRA says so.
5. **Deactivating an item.** `saveItem` validates every call as a new insert, so re-sending an
   item code with `useYn=N` is rejected with "Invalid itemCd Sequence". Ask for the supported
   way to retire an item. Until then we retire items locally only.
6. **Item codes in production.** Production codes follow KRA's per-PIN sequence. Our automatic
   correction to KRA's "expected sequence" is proven in the sandbox only. Ask whether production
   behaves the same, and whether items registered in the sandbox carry over (we assume they do
   not and register them again).
7. **Offline window.** We tell operators to requeue a dead-lettered sale within 48 hours. Confirm
   the limit, and what KRA expects for a sale signed later than that.
8. **Tourism levy on eTIMS receipts.** We keep the 2% tourism levy outside the VAT bands A to E
   and never put it on the receipt (absorbed mode). Ask whether a levy charged on the bill should
   appear on the eTIMS receipt and, if so, in which field.

### Go-live steps and approvals

9. **Production service request and approval.** Confirm the steps after certification: the
   production portal service request (PIN, branch, serial), who approves it and how long it takes,
   and whether the go-live invoice and credit note (INV-261016-000102, invcNo 209 and CN-000030,
   invcNo 210) complete the resubmission.
10. **Device serial format.** Confirm the serials to use in production. The portal cut the serial
    off at `CV-P05254316` in one session, which sent a wrong serial (TS03 instead of TS01) to init.
11. **Retired device TS02.** KRA's side showed TS02 as invalid and we removed it. Confirm it is
    gone on their side too before we register another device on that branch.
12. **The sandbox CMC key in our history.** An old sandbox CMC key sits in our git history (commit
    `50023c78`). Ask how to have it reissued so the old one stops working.
13. **Official KRA logo.** We print no KRA logo on fiscal documents. Ask for the approved asset
    and the rules for using it, if any.

### GavaConnect products (not eTIMS, but the same team may answer)

14. **PIN Checker by ID.** Our PINID app is subscribed to PIN Checker by PIN only. Confirm we can
    add the PIN Checker by ID product to it on developer.go.ke.
15. **Withholding PRN nature codes.** Income-tax withholding PRNs send `WHT_3000`, resident, KE.
    Confirm the nature code for each withholding type. Rental withholding PRNs stay on the manual
    form because KRA needs property details.
