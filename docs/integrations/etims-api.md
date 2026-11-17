# eTIMS API: External Integrator Quickstart

Codevertex's treasury platform is a certified KRA eTIMS OSCU integrator. If you run your own
software and want to fiscalize sales with KRA directly, without adopting the full Codevertex
POS/treasury suite, this API is for you.

## Who this is for

- **Self-serve.** You have your own developers. No integration fee. Sandbox test, pass the
  go-live certification checklist, move to production, and pay only for API usage.
- **Assisted.** You'd rather our team handle the setup. A one-time fee applies, from KES 35,000
  depending on how many branches and devices you have and which system we connect. See
  [assisted integration](#assisted-integration-one-time) below. Ongoing usage billing is the same
  either way.

## Request access

Apply at [accounts.codevertexafrica.com/developer/apply](https://accounts.codevertexafrica.com/developer/apply)
and pick **Treasury API** as the service. You can also fill out the form at
[codevertexafrica.com/integrations](https://codevertexafrica.com/integrations), or describe what
you want to Vera, the assistant embedded on that page, and it will collect the details and route
your request to our team. Our support team is notified immediately and follows up by email. A
self-serve request typically gets a sandbox credential provisioned automatically once approved.

## How it works

1. **Get your credentials.** Once your request is approved, we email your consumer key and a link
   to the developer console. Sign in (developer accounts use an authenticator app), open your
   sandbox app and generate a consumer secret. It is shown once. We never send secrets by email.
2. **Sandbox first.** Register a virtual device, register a couple of items, record a stock
   movement, and transmit a few test sales, all against KRA's own sandbox, at no risk. Sandbox
   calls are not charged.
3. **Check your certification status.** A single endpoint tells you exactly what's left before
   you can request production access.
4. **Request go-live.** Once your checklist is green, one call notifies our platform team for a
   final review. This mirrors the same two-layer gate KRA itself uses for certifying integrators:
   an automated check followed by a human reviewer.
5. **Go live.** You're on a prepaid token bucket. Call the API as long as you have a balance, and
   top up any time.

## Authentication

Exchange your consumer key and secret for an access token, then send the token on every call.

```bash
curl -s -X POST https://sso.codevertexafrica.com/api/v1/token \
  -u "$CONSUMER_KEY:$CONSUMER_SECRET" \
  -d grant_type=client_credentials
```

```json
{ "access_token": "eyJ...", "token_type": "Bearer", "expires_in": 900, "scope": "etims:read etims:write" }
```

```bash
curl -s https://booksapi.codevertexafrica.com/api/v1/external/etims/certification-status \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

- Tokens last 15 minutes. Request a new one when it expires; there is no refresh token.
- Add `scope=etims:read` to the token request for a read-only token.
- You can also send `client_id` and `client_secret` as form fields instead of HTTP Basic auth.
- Suspending or revoking the app makes its existing tokens stop working straight away.
- If you set an IP allowlist on the app (single addresses or ranges such as `41.90.12.0/24`),
  tokens are only issued to those addresses.
- The older `X-API-Key` header still works but is being retired. New integrations should use
  access tokens.

### Sandbox and live secrets

New consumer secrets show which environment they belong to, the way Stripe keys do: a sandbox
app's secret starts with `bng_cs_test_` and a production app's with `bng_cs_live_`. API keys
follow the same pattern (`bng_app_test_` and `bng_app_live_`). Secrets issued before this change
start with plain `bng_cs_` and keep working.

Promotion to production leaves your existing secret as it is, so nothing breaks on go-live day.
To get a `bng_cs_live_` secret, rotate it from the console after promotion, keeping the old one
for 24 hours while you switch over. We do not rotate automatically on promotion because the new
secret would then be shown to the reviewer who promotes the app rather than to you.

### Rotating your secret

Open your app in the developer console and choose **New secret**. You then pick one of two
options:

- **Keep the old secret working for 24 hours** (the default). Both secrets can get access
  tokens until the time shown in the console, so you can roll the new one out with no downtime.
  Tokens already issued are left to run out on their own within 15 minutes.
- **Stop it now.** Use this if the secret may have leaked. The old secret is refused straight
  away, and so is every access token already issued for the app.

Only one old secret is kept. Rotating again while an old secret is still in its grace period
ends that older secret at once. Rotating the API key offers the same two options.

Over the API, send `POST /api/v1/admin/apps/{id}/rotate-secret` (or `/rotate` for the API key)
with an optional body such as `{"grace_hours": 24}`. The default is 24 hours, the most is 168
hours (7 days), and `0` stops the old secret immediately. The response carries the new secret
once and `previous_client_secret_expires_at` (or `previous_key_expires_at`) with the time the
old one stops working.

## Pricing: prepaid tokens, not a flat monthly quota

Every call spends a small number of tokens, weighted by what it actually costs to serve. A cached
lookup costs far less than a call that reaches KRA's live signing infrastructure.

| Plan | Monthly | Included tokens/month | About this many sales | Top-up price |
|---|---|---|---|---|
| API Basic | KES 2,500 | 5,000 | 500 | KES 0.60/token |
| API Growth | KES 4,000 | 20,000 | 2,000 | KES 0.45/token |
| API Scale | KES 8,000 | 100,000 | 10,000 | KES 0.30/token |

A sale sent to KRA costs 10 tokens. Writes such as registering a device or an item cost 3, and a
lookup costs 1. So a sale works out to:

| Plan | Per sale within your plan | Per sale on a top-up |
|---|---|---|
| API Basic | KES 5.00 | KES 6.00 |
| API Growth | KES 2.00 | KES 4.50 |
| API Scale | KES 0.80 | KES 3.00 |

Top-up tokens cost more than the tokens your plan includes, so if you regularly top up, a bigger
plan is usually cheaper. Included tokens accumulate every renewal and never reset or expire. A
call that fails before doing real work, such as a malformed request or KRA itself rejecting or
timing out, is refunded automatically.

Not sure which plan fits? `POST /tokens/estimate` needs no API key. Give it your expected volume
and it returns your monthly token need, what each plan would cost you in total including
top-ups, and the cheapest plan for that volume. See the
[full API reference](#full-api-reference) for the endpoint.

Already a Codevertex customer whose main plan bundles eTIMS? You don't pay the standalone fee
twice. Ask support about the `ETIMS_API_BUNDLED` tier: the same token pricing as API Basic, with
no monthly base fee.

## Assisted integration (one-time)

If you'd like our team to do the setup instead of your own developers, a one-time fee applies. It
is invoiced once when we start and is separate from your token plan.

| Package | One-time fee | What's included |
|---|---|---|
| Standard | KES 35,000 | One KRA PIN, one branch, one device. Item and stock sync, sales and credit notes, sandbox testing and go-live support. |
| Multi-branch | KES 85,000 | Up to 5 branches or devices under one PIN. Mapping to your ERP or POS fields, purchases and imports, staff training. |
| Enterprise | KES 180,000 | Several PINs or companies, VSCU, SAP, Odoo, Sage or older in-house systems, custom middleware, on-site work. |
| Extra branch or device | KES 7,500 each | Beyond your package's allowance. KRA issues credentials per PIN, branch and device, so each one is set up separately. |
| Annual support (optional) | 15% of your setup fee a year | We handle KRA specification changes and device re-registration, with priority help. |

Not sure which package fits? Describe your setup in the request form and we'll confirm the
package and price before any work starts.

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
[Treasury Service API Docs](https://booksapi.codevertexafrica.com/v1/docs/). It's filtered to the
external eTIMS/Payments/Health surface for anonymous visitors, same as this reference. If you've
been given a Codevertex staff app secret, paste it into the bar at the top of that page to unlock
the full internal spec.

## Related

- [Payment Workflow](payment-workflow.md), if you're also integrating payment collection and not
  just fiscalization.
- [Finance Integration Map](finance-integration-map.md), for how treasury's ledger fits together
  and where eTIMS sits in the bigger picture.
