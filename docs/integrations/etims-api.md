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
5. **Go live.** Pay a monthly plan (with a fair included-transaction quota and metered overage
   beyond it) for as long as you use the API.

## Pricing

| Plan | Monthly | Included transactions | Overage (per 100) |
|---|---|---|---|
| API Basic | KES 4,999 | 500 | KES 800 |
| API Growth | KES 12,999 | 2,000 | KES 600 |
| API Scale | KES 29,999 | 10,000 | KES 400 |

A one-time assisted-integration fee applies only if you choose to have our team do the setup for
you instead of your own developers.

## Full API reference

The complete endpoint reference (authentication, request/response shapes, error codes, rate
limits) lives with the treasury service itself:
[treasury-api's external eTIMS API reference](https://github.com/Bengo-Hub/treasury-api/blob/main/docs/integrations/external-etims-api.md).

## Related

- [Payment Workflow](payment-workflow.md) — if you're also integrating payment collection, not
  just fiscalization.
- [Finance Integration Map](finance-integration-map.md) — how treasury's ledger fits together, for
  context on where eTIMS sits in the bigger picture.
