# KRA eTIMS demo guide (OSCU integrator)

Read this before the KRA demonstration. It covers what the KRA team looks at, the order to show
things in, the code and architecture questions to expect, and what to do if the sandbox misbehaves.

It builds on these treasury-api documents and does not repeat them:

- `finance-service/treasury-api/docs/kra-etims-demo-runbook.md`: the click path for each flow.
- `finance-service/treasury-api/docs/architecture/tis-etims-technology-architecture.md`: the
  architecture document submitted to KRA (and its PDF in the same folder).
- `finance-service/treasury-api/docs/architecture/tis-etims-demo-presentation.md`: the slides.
- `finance-service/treasury-api/docs/kra-oscu-automated-testing-runbook.md`: the certification history
  and every KRA error we have hit, with its cause.

## 1. Where we stand

| Item | State |
|---|---|
| Certification | 23 of 23 passed on 2026-10-16, app `etims-oscu-cert-app-ts01`, device `CV-P052543168K-TS01`, branch 00 |
| Go-live copies | Invoice INV-261016-000102 (invcNo 209) and credit note CN-000030 (invcNo 210); download the PDFs from each document in treasury |
| Taxpayer | Codevertex Africa Limited, PIN P052543168K, branches 00 and 01 |
| Demo tenant | `codevertex-demo` on books.codevertexafrica.com (treasury) and pos.codevertexafrica.com (POS) |
| Test buyer | CRM contact "Test Customer", PIN P318295670X |
| Route | Real traffic goes straight to `etims-api-sbx.kra.go.ke/etims-api` with the device `tin`, `bhfId` and `cmcKey` headers. The certification wizard alone uses the GavaConnect proxy, because the portal only scores that route |
| Auto sync on codevertex-demo | Off. Every new document needs **Transmit to eTIMS** by hand |

## 2. Run sheet for today

**13:00, read-only checks.** Nothing here creates data at KRA.

1. Sign in to books.codevertexafrica.com as the demo user and open the codevertex-demo org.
2. Go to Tax & Compliance, then eTIMS Devices. The activation card must show all four steps green
   and the device as active on branch 00 and branch 01.
3. On Transmissions, invcNo 209 and 210 should show as transmitted, each with a CU number.
4. Open invoice INV-261016-000102. The KRA eTIMS panel shows the CU invoice number, the signature
   and the QR. Download the PDF once to make sure the docs engine answers.
5. In the certification wizard, run the **Select Invoice Details** lookup for 209. It is a read
   call and proves the sandbox answers.
6. Open pos.codevertexafrica.com on the demo outlet and check that the till loads its catalogue.

If step 5 times out, KRA's sandbox is slow. Try once more after five minutes. If it still fails,
plan to use the fallback in section 7.

**13:30, set up the screen.** Open these tabs, in this order:
1. Treasury eTIMS Devices.
2. eTIMS Items.
3. Invoices.
4. Transmissions.
5. eTIMS Sync.
6. The POS till.
7. The architecture PDF.
8. This guide.

Close everything else and turn off notifications.

**14:00, agenda (about 45 minutes).**
1. Two minutes on who we are and the product (one fiscalisation point for POS, invoicing and
   purchases).
2. Five minutes of architecture, using the PDF diagram.
3. Twenty minutes of live walkthrough (section 4).
4. Fifteen minutes of questions (section 5).
5. Close with the evidence list (section 6).

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
6. **Invoice number control.** invcNo is sequential per device branch and never reused. Ask
   yourself how we stop two servers taking the same number; the answer is in section 5.
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

1. **Activation (2 min).** Open eTIMS Devices and walk through the activation card (PIN, device,
   CMC key, entitlement). Point out that the CMC key is masked. Do not press Initialise again.
2. **Code lists (1 min).** On the same tab, press **View Code Lists** to show the lists pulled from
   KRA, then open the item class dropdown in the Register item form on eTIMS Items. (The screen
   does not show when the lists were last refreshed; **Refresh Code Lists** pulls them again.)
3. **Register an item (3 min).**
   - Go to eTIMS Items and choose Register item.
   - Leave the code blank so the server mints it.
   - Pick a real class and band B.
   - Show the new row with its `itemCd` and the Registered badge.

   This step creates data at KRA, so agree it in advance.
4. **Sale with two items (5 min).**
   - Raise an invoice to the Test Customer with two registered items, one band B and, if possible,
     one band D.
   - Send it, then press **Transmit to eTIMS**.
   - Show the CU number, signature and QR on the invoice.
   - Download the PDF and show the SCU information block and the band table.
   - Scan the QR on a phone.
5. **POS sale (3 min).** Ring up two items on the till, take payment and show the printed receipt
   with the KRA block. The POS sale is fiscalised by treasury, the same single point.
6. **Credit note (3 min).**
   - From the invoice, choose Credit Note, then Pick items to credit, and credit one line.
   - Transmit it and show `rcptTyCd R` with the original invcNo.
   - Show that crediting more than the remainder is refused.
7. **Transmissions and audit trail (2 min).** On the Transmissions tab, open a row to show its
   status, eTIMS invoice number, KRA receipt number, CU number, signature, retry count and any
   error, plus the Retry and Requeue actions. KRA's full reply is shown on the invoice itself, in
   the window that opens after **Transmit to eTIMS**.
8. **Reconciliation (1 min).** Show eTIMS Sync comparing KRA's sales list with our records.

Purchases and stock are slower to show live. Describe them from the stock mapping table in the
demo runbook and show the ledger rows on eTIMS Sync instead.

## 5. Code and architecture questions

### Where the code lives

The KRA integration is in treasury-api, module `internal/modules/tax`.

| Concern | File |
|---|---|
| HTTP client, every OSCU call, payload shapes | `kra_client.go`, `kra_client_oscu_ext.go`, `kra_client_oscu_branch.go` |
| Direct host versus GavaConnect routing | `kra_routing.go` |
| Platform and tenant on/off switches | `etims_switch.go` |
| OAuth token handling for GavaConnect | `gavaconnect_client.go` |
| Device registration, initialisation, CMC key | `service.go`, `service_etims_device_init.go` |
| Code lists and item classes | `service_etims_codelists.go` |
| Item registration and `itemCd` | `service_etims_items.go`, `etims_item_classify.go` |
| Sales, invcNo allocation, duplicate handling | `service_etims_stock.go`, `invcno_order.go`, `invcno_duplicate.go`, `kra_sequence_reconcile.go` |
| Money rounding at the KRA boundary | `kra_money.go` |
| POS sales and refunds | `service_pos_etims.go`, `refund_split.go` |
| Stock IO and stock master | `service_etims_stock.go`, `stock_subscriber.go`, `service_etims_stock_reconcile.go` |
| Purchases | `purchase_match.go`, `purchase_adjustment.go`, `service_etims_expense.go` |
| Background transmission and retries | `worker.go` |
| Reconciliation with KRA | `service_etims_reconcile.go` |
| Certification runner | `certification_runner.go`, `service_certification.go` |
| VSCU (local signing unit) | `vscu.go`, `vscu_offline.go` |

The front end is treasury-ui, under `src/app/[orgSlug]/tax` (tabs) and `tax/etims-certification`
(the 23-step wizard).

### Likely questions and short answers

**How does a sale reach KRA?** Every source (an invoice, a POS sale, an online order) ends at one
function in treasury that builds the OSCU sales payload and sends it. POS and ordering never talk
to KRA themselves. A finished sale either goes straight away (Transmit, or POS checkout) or is
queued and picked up by the worker within about 30 seconds.

**What stops two servers from issuing the same invoice number?** The number is taken inside a
database transaction that locks the device rows for that PIN and branch (`SELECT ... FOR UPDATE`),
so sends for one branch go one at a time across all pods. The number is stored on the record
before the call, and a unique index stops a document being queued twice.

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
secret, never in code. API responses show it masked, and revealing it needs the treasury
configuration permission.

**How is one taxpayer kept from another?** Each tenant's data carries its tenant id, and every
query filters on it. A device belongs to one tenant and one PIN. Users sign in through our identity
service with signed tokens (RS256), and permissions come from their role. Internal calls between
our services use a separate service key.

**Do you use the GavaConnect proxy or the eTIMS host?** Live traffic goes to the eTIMS host
directly with the device headers. The certification wizard uses GavaConnect with OAuth, because
that is the route the portal scores. Switching from sandbox to production is a configuration change
per device; the code does not change.

**How do you handle tax bands and rounding?** We follow KRA's band letters (A exempt, B 16, C zero,
D non-VAT, E 8). Unit prices are VAT inclusive, the taxable amount is the supply divided by one plus
the rate, and every amount is rounded to two decimals at the point where it leaves our system. Band
totals are summed from the rounded lines, so the header always matches.

**What if the taxpayer is not VAT registered?** The tenant's tax obligations decide. A non-VAT
tenant registers and sells everything as band D with no VAT, and VAT-only screens are hidden.

**How do returns from the till reach KRA?** A POS return sends the returned lines, outlet and the
original order to treasury. Treasury raises a credit note that refers to the original invcNo and
sends it as a refund, splitting each line by the band the item was registered under.

**How do you keep stock in step with KRA?** Every stock movement in inventory raises an event.
Treasury maps it to one KRA stock reason (sale out 11, purchase in 02, return in 03, adjustment in
06, adjustment out 16, return to supplier 12). It keeps a ledger keyed on the source movement, so
a movement is sent once. The stock master quantity follows the running stocked-in total.

**Can a user edit a fiscalised invoice?** No. Only a draft can be edited, and a draft is never
sent to KRA. Once an invoice is issued, corrections go through a credit note and a new invoice.

**What about offline tills?** POS keeps sales offline and syncs them when back online with an
idempotency key, so a resent sale is not created twice. Treasury fiscalises it once it arrives.

**Do you support VSCU?** Yes, as a second channel next to OSCU. A business picks the channel on its
tax profile: OSCU only, VSCU only, or automatic, which uses OSCU and moves a sale to the branch's
VSCU unit only when OSCU could not be reached at all. VSCU calls follow KRA's VSCU Specification
v2.0 path names. Both channels take invoice numbers from the
same branch counter under the same lock, so they never reuse a number, and a slow OSCU answer is
retried rather than signed again on VSCU. No customer runs a VSCU unit yet. If asked whether one
branch may run both an OSCU and a VSCU device, say we will follow KRA's ruling; we have asked.

**Which tech stack?**
- Go services with the Ent ORM and Atlas versioned migrations.
- PostgreSQL behind PgBouncer, Redis, and NATS JetStream for events.
- Next.js front ends.
- Kubernetes with ArgoCD, NGINX ingress, cert-manager, and Cloudflare at the edge.

Treasury runs at least two replicas with a disruption budget and autoscaling.

**How do you test?** Unit tests pin each payload rule (bands, rounding, refund dates, credit lines).
A scripted certification suite replays all 23 cases against the sandbox, and the wizard runs the
same cases from the UI. Every transmission keeps the request and KRA's response for audit.

**How do you deploy and roll back?** Each merge builds an image tagged with the commit. ArgoCD rolls
it out pod by pod, and rolling back means pointing at the previous tag. Database changes are
versioned migrations applied at start-up.

**What logs and monitoring are there?** Structured logs with a request id on every call, health
probes, and per-document status with KRA's result code. Failed and dead-lettered documents show on
the Transmissions screen.

**How do you onboard a new taxpayer?** Enter the PIN on the tax profile, register the device with
its serial and branch, initialise to get the CMC key, refresh code lists, then register items. The
activation card shows each step. Until all four are green, no document is sent to KRA.

**Can third parties use your integration?** Yes. An external eTIMS API takes an API key scoped to
eTIMS, with per-plan rate limits and usage billing. It goes through the same fiscalisation code.

**What are the known limits?** Answer these honestly if asked:
- VSCU is built but not provisioned for any customer.
- The debit note path (`rcptTyCd D`) has not been run live.
- Tenant isolation is enforced in the application layer, not with database row-level security.

### Before the demo, know these points about your own system

- Auto sync is off on codevertex-demo, so you must press Transmit. Say so on screen instead of
  waiting for the worker.
- KRA's GavaConnect proxy timed out (504 after 20 seconds) from 2026-09-24. That is why live
  traffic goes direct. If they ask about the earlier rejection, the cause was that our attached
  invoice never fiscalised while the proxy was failing. It has been fixed since 2026-10-13.
- A line with no tax code takes the catalogue VAT even when the item is registered as band D. Set
  the tax code on band D items before selling them in the demo.

## 6. Evidence to have ready

- The certification history on the demo tenant: Tax & Compliance, eTIMS Devices tab, the
  **Certification Wizard** button, then the **Certification history** card at the top of that page.
  Click a run to open its 23 cases.
  The 2026-10-16 run shows 23 of 23, run by admin@codevertexafrica.com, with each step's result.
  That session was driven by scripts against KRA rather than through the wizard, so its results
  were entered into the history afterwards from the session record (the run's notes say so). Say so
  if asked. The two earlier runs on 2026-09-22 (1 and 12 of 23) are older attempts.
- The go-live invoice and credit note: open INV-261016-000102 and CN-000030 in treasury and
  download the PDFs. `d:\tmp\etims-go-live` holds the later mixed band copies (INV-261016-000103 and
  000105, CN-000031 and 000033), not 209 and 210.
- The architecture PDF, `Codevertex-TIS-eTIMS-Technology-Architecture.pdf`.
- The submission pack in `finance-service/treasury-api/docs/kra-submission` (registration, CR12,
  TCC, staff, declaration of solvency, bio-data form).

## 7. If something goes wrong

| Symptom | What to do |
|---|---|
| A KRA call hangs for 20 seconds then fails | Sandbox is slow. Say so, show the queued document on Transmissions, and move on to the next flow. Come back to Retry later |
| "Invalid invcNo" or "already exists" | Expected after a gap. Press Retry once; the counter heals itself. Explain the duplicate handling from section 5 |
| 902 on initialise | Normal, the device is already installed. Do not repeat |
| Receipt has no KRA block | The send has not finished. Wait for the page to refresh, or open the invoice from Transmissions |
| The sandbox is down entirely | Show the 23/23 certification history, open the go-live invoice and credit note, scan their QR, and open their rows on Transmissions to show the CU number, signature and receipt KRA returned |

## 8. State of production on demo day

Live since 12:20 on 2026-10-27:
- treasury-api `6f2bc953`: VSCU address checks, CMC key no longer stored twice, KRA replies cut in
  errors, and revealing a CMC key needs config manage.
- treasury-ui `e20ec43`: the certification history on the wizard page (Tax & Compliance,
  eTIMS Devices, Certification Wizard).

Live since 2026-10-28 (after the demo): treasury-api `83158a68` and treasury-ui `86f867ee`. The
signing channel is on the Tax Profile tab (automatic by default), each device has a Channel action
on the eTIMS Devices tab, and Transmissions shows "Signed via". The full list of fixes is in the
treasury-api runbook, section 3.38.

## 9. Do not do during the demo

- Do not initialise the device again or change the invoice counter.
- Do not switch the platform or tenant eTIMS switch off.
- Do not use branch 00 for test sales (keeps the go-live sequence clean).
- Do not open server logs, the database, or anything showing keys or tokens on the shared screen.
- Do not promise dates for VSCU or production go-live. Say they follow KRA approval.
