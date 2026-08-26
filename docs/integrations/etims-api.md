# eTIMS API: External Integrator Quickstart

Codevertex's treasury platform is a certified KRA eTIMS OSCU integrator. If you run your own
software and want to fiscalize sales with KRA directly, without adopting the full Codevertex
POS/treasury suite, this API is for you.

## Who this is for

- **Self-serve.** You have your own developers. No integration fee. Sandbox test, pass the
  go-live certification checklist, move to production, and pay only for API usage.
- **Assisted.** You'd rather our team handle the setup. A one-time fee applies, scoped to your
  device/branch count and support needs. Ongoing usage billing is the same either way.

## Request access

Apply at [accounts.codevertexafrica.com/developer/apply](https://accounts.codevertexafrica.com/developer/apply)
and pick **Treasury API** as the service. You can also fill out the form at
[codevertexafrica.com/integrations](https://codevertexafrica.com/integrations), or describe what
you want to Vera, the assistant embedded on that page, and it will collect the details and route
your request to our team. Our support team is notified immediately and follows up by email. A
self-serve request typically gets a sandbox credential provisioned automatically once approved.

## How it works

1. **Get your API key.** Once your request is approved, you receive an `X-API-Key` credential
   scoped to `etims:read`/`etims:write`.
2. **Sandbox first.** Register a virtual device, register a couple of items, record a stock
   movement, and transmit a few test sales, all against KRA's own sandbox, at no risk.
3. **Check your certification status.** A single endpoint tells you exactly what's left before
   you can request production access.
4. **Request go-live.** Once your checklist is green, one call notifies our platform team for a
   final review. This mirrors the same two-layer gate KRA itself uses for certifying integrators:
   an automated check followed by a human reviewer.
5. **Go live.** You're on a prepaid token bucket. Call the API as long as you have a balance, and
   top up any time.

## Pricing: prepaid tokens, not a flat monthly quota

Every call spends a small number of tokens, weighted by what it actually costs to serve. A cached
lookup costs far less than a call that reaches KRA's live signing infrastructure.

| Plan | Monthly | Included tokens/month | Roughly this many sales transmissions | Top-up price |
|---|---|---|---|---|
| API Basic | KES 1,500 | 5,000 | ~500 | KES 0.80/token |
| API Growth | KES 4,000 | 20,000 | ~2,000 | KES 0.60/token |
| API Scale | KES 8,000 | 100,000 | ~10,000 | KES 0.40/token |

Included tokens accumulate every renewal and never reset or expire. A call that fails before
doing real work, such as a malformed request or KRA itself rejecting or timing out, is refunded
automatically. Not sure which plan fits? `POST /tokens/estimate` needs no API key and turns your
expected call volume into an exact monthly token figure and a plan recommendation. See the
[full API reference](#full-api-reference) for the endpoint.

Already a Codevertex customer whose main plan bundles eTIMS? You don't pay the standalone fee
twice. Ask support about the `ETIMS_API_BUNDLED` tier: the same token pricing as API Basic, with
no monthly base fee.

A one-time assisted-integration fee applies only if you choose to have our team do the setup for
you instead of your own developers.

## What's KRA's requirement vs. our own go-live gate

Under KRA's own OSCU specification, device credentials (`cmcKey`, `sdcId`, `mrcNo`, `dvcId`) are
issued per taxpayer PIN, branch, and device serial. They can't be pooled at an aggregator level.
When you register a device through this API, we register a real device with KRA under your TIN
and hold the resulting credentials on your behalf. The transmission is legally yours, fiscalized
through our platform, not "as us." Our sandbox simulation layer and the certification checklist
above are our own design, modeled on but not identical to KRA's own certification, meant to let
you build and test before you have real KRA sandbox credentials.

One open question we're confirming directly with KRA rather than assuming: whether a certified
integrator can drive your initial KRA taxpayer-portal signup on your behalf, or whether you need
to complete that handshake yourself at least once. Ask support if this affects your onboarding
timeline.

## Full API reference

The complete endpoint reference, covering authentication, request and response shapes, error
codes, and rate limits, is published as a live Swagger/OpenAPI doc on the treasury service:
[Treasury Service API Docs](https://booksapi.codevertexafrica.com/v1/docs). It's filtered to the
external eTIMS/Payments/Health surface for anonymous visitors, same as this reference. If you've
been given a Codevertex staff app secret, paste it into the bar at the top of that page to unlock
the full internal spec.

## Related

- [Payment Workflow](payment-workflow.md), if you're also integrating payment collection and not
  just fiscalization.
- [Finance Integration Map](finance-integration-map.md), for how treasury's ledger fits together
  and where eTIMS sits in the bigger picture.
