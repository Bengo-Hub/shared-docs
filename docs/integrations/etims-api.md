# eTIMS API — External Integrator Quickstart

Codevertex's treasury platform is a certified KRA eTIMS OSCU integrator. If you run your own
software and want to fiscalize sales with KRA directly — rather than adopting the full Codevertex
POS/treasury suite — this is the API for you.

## Who this is for

- **Self-serve** — you have your own developers. No integration fee. You sandbox-test, pass a
  go-live certification checklist, then move to production and pay only for API usage.
- **Assisted** — you'd rather our team handle the setup. A one-time fee applies (scoped to your
  device/branch count and support needs); ongoing usage billing is identical either way.

## Request access

Apply at [accounts.codevertexafrica.com/developer/apply](https://accounts.codevertexafrica.com/developer/apply) —
pick **Treasury API** as the service. You can also fill out the form at
[codevertexafrica.com/integrations](https://codevertexafrica.com/integrations), or just describe
what you want to Vera, the assistant embedded on that page, and it will collect the details and
route your request to our team. Either way, our support team is notified immediately and follows
up by email, and a self-serve request typically gets a sandbox credential provisioned
automatically once approved.

## How it works

1. **Get your API key.** Once your request is approved, you receive an `X-API-Key` credential
   scoped to `etims:read`/`etims:write`.
2. **Sandbox first.** Register a virtual device, register a couple of items, record a stock
   movement, and transmit a few test sales — all against KRA's own sandbox, at no risk.
3. **Check your certification status.** A single endpoint tells you exactly what's left before
   you can request production access.
4. **Request go-live.** Once your checklist is green, one call notifies our platform team for a
   final review — the same two-layer gate (automated check + human reviewer) KRA itself uses for
   certifying integrators.
5. **Go live.** You're on a prepaid token bucket — call the API as long as you have a balance, top
   up any time.

## Pricing — prepaid tokens, not a flat monthly quota

Every call spends a small number of tokens, weighted by what it actually costs to serve (a cached
lookup costs far less than a call that reaches KRA's live signing infrastructure):

| Plan | Monthly | Included tokens/month | ≈ sales-transmission equivalent | Top-up price |
|---|---|---|---|---|
| API Basic | KES 4,999 | 5,000 | ~500 | KES 0.80/token |
| API Growth | KES 12,999 | 20,000 | ~2,000 | KES 0.60/token |
| API Scale | KES 29,999 | 100,000 | ~10,000 | KES 0.40/token |

Included tokens **accumulate** every renewal (never reset or expire), and a call that fails
before doing real work (a malformed request, or KRA itself rejecting/timing out) is automatically
refunded. Not sure which plan fits? `POST /tokens/estimate` (no API key needed) turns your
expected call volume into an exact monthly token figure and a plan recommendation — see the [full
API reference](#full-api-reference) for the endpoint.

Already a Codevertex customer whose main plan bundles eTIMS? You don't pay the standalone fee
twice — ask support about the `ETIMS_API_BUNDLED` tier (same token economics as API Basic, KES
0/month base fee).

A one-time assisted-integration fee applies only if you choose to have our team do the setup for
you instead of your own developers.

## What's KRA's requirement vs. our own go-live gate

Per KRA's own OSCU specification, device credentials (`cmcKey`/`sdcId`/`mrcNo`/`dvcId`) are issued
**per taxpayer PIN + branch + device serial — never poolable at an aggregator level**. When you
register a device through this API, we register a real device with KRA under *your* TIN and hold
the resulting credentials on your behalf — the transmission is legally yours, fiscalized through
our platform, not "as us." Our sandbox-simulation layer and the certification checklist above are
our own design (modeled on, but not identical to, KRA's own certification), meant to let you build
and test before you have real KRA sandbox credentials. One open question we're confirming directly
with KRA rather than assuming: whether a certified integrator can drive your initial KRA
taxpayer-portal signup on your behalf, or whether you need to complete that handshake yourself at
least once — ask support if this affects your onboarding timeline.

## Full API reference

The complete endpoint reference (authentication, request/response shapes, error codes, rate
limits) is published as a live Swagger/OpenAPI doc on the treasury service itself:
[Treasury Service API Docs](https://booksapi.codevertexafrica.com/v1/docs) — filtered to the
external eTIMS/Payments/Health surface for anonymous visitors, exactly like this reference. If
you've been given a Codevertex-staff app secret, pasting it into the bar at the top of that page
unlocks the full internal spec instead.

## Related

- [Payment Workflow](payment-workflow.md) — if you're also integrating payment collection, not
  just fiscalization.
- [Finance Integration Map](finance-integration-map.md) — how treasury's ledger fits together, for
  context on where eTIMS sits in the bigger picture.
