# PayHero Integration Reference

> **Source**: [PayHero API documentation](https://docs.payhero.africa) (API 2.0.0)
> **Owner**: treasury-api
> **Updated**: October 2026

PayHero Africa is treasury's gateway for M-Pesa collections into a tenant's own paybills, tills
and bank accounts, for mobile money in other countries (MTN, Airtel and other networks), for card
hosted checkout, bank deposits and the offline paybill, and for payouts from a tenant's PayHero
wallet. Only the 2.0.0 API is used.

See [Payment Workflow](payment-workflow.md) for the end-to-end flow every gateway shares (intent
creation, the shared pay page, `initiate_url`, callbacks). This page covers what is specific to
PayHero. For the tenant-facing setup steps, see the
[PayHero user guide](../user-guide/treasury/payhero.md).

## Hosts and authentication

| Host | Used for |
|---|---|
| `https://api.payhero.africa` | Payments, rail discovery, status, balance, beneficiaries, payment channels |
| `https://auth.payhero.africa` | Teams (accounts), invites, KYC |
| `https://connect.payhero.africa` | Identity verification checks (billed per check) |

All three use HTTP Basic auth with the API username and password. The platform's key is stored
encrypted in treasury's gateway configuration and is never exposed to tenants.

## Account modes

The platform owner configures PayHero once (Platform, Gateways). Each tenant then turns PayHero on
in one of three modes:

| Mode | Account used | Own wallet | Notes |
|---|---|---|---|
| `platform_team` (default) | The tenant's own **Team** inside the platform's PayHero organization | Yes, isolated per Team | Required for escrow and wallet collections |
| `platform_root` | The platform's root account; the tenant claims specific channels | No | Channel collections only |
| `own_account` | The tenant's own PayHero API key (stored encrypted) | Its own | The account is detected from the key's channels on the first sync |

A `platform_team` tenant without a Team has no account at all. It never falls back to the
platform's account, so its collections and payouts can never touch the platform's wallet.

Creating Teams requires a PayHero **enterprise** organization. On other plans PayHero refuses
Team creation; treasury explains the options: upgrade the organization with PayHero, use the
shared platform account mode, connect the tenant's own PayHero account, or link a Team created on
the PayHero dashboard.

PayHero has no API to create channels or wallets. A Team gets its wallet (and a service wallet
that pays PayHero's own costs) when it is created. Paybills, tills and bank accounts are added on
the PayHero dashboard by someone invited into the Team, then synced into treasury. A collection
straight to a channel needs credit in the service wallet (with an empty one PayHero refuses it);
wallet deposits and payouts take PayHero's charge from the money instead (see Fees and collection
routes).

### Who sets what

| Setting | Level | Where |
|---|---|---|
| API key, organization and root account | Platform | Platform, Gateways, PayHero (Detect fills the ids) |
| Gateway available to tenants, platform primary | Platform | Platform, Gateways |
| PayHero on, mode, country, offline paybill | Tenant | Settings, Payments, PayHero, Account |
| Team (create or link) | Tenant, or the platform owner on their behalf | Settings, Payments, PayHero, Account |
| Channels on or off, routing, payment links | Tenant | Settings, Payments, PayHero, Channels and routing |
| KYC checks and tier | Tenant | Settings, Payments, PayHero, Verification |
| Which gateways customers see, tenant primary | Tenant | Settings, Payments, Gateways |

## Channels and routing

Treasury syncs a tenant's channels on demand and every 15 minutes, and keeps an on/off switch per
channel. Each collection is routed to a channel in this order:

1. the outlet override,
2. the payment's reference type (for example `invoice` or `pos_order`),
3. the default channel (the first active channel when none is set).

The routing screen only lists payment types the tenant can actually receive: those of the
products it subscribes to, those it received in the last 180 days, and those already routed.

A Kenyan M-Pesa pay-in reaches the routed channel straight, or relayed through a payments wallet
(see Fees and collection routes). Escrow contributions and wallet top-ups carry no channel and
land in the Team wallet.

### Payments to the platform

Plan subscriptions, renewals, support-agreement charges, top-ups and card setup are charged on the
platform's own PayHero account and follow its routing, whatever gateway the paying tenant uses;
the pay page lists the platform's methods for them. A payment made from an invoice's Pay Now page
takes the invoice's own routing (a subscription invoice routes as a subscription, not as a manual
invoice).

### Personal channels (platform owner)

The platform owner can mark a channel as a personal account with a payee name. It never maps to a
company account, never takes a business route and is the only channel personal collections
(support agreements set to Personal) settle into, by M-Pesa only. Those invoices are kept off the
company's books entirely: no ledger entry, receivable, eTIMS submission or report figure.

### Plans

PayHero is gated on the plan's `mpesa_integration` feature (from the Growth tier, like direct
M-Pesa): without it the PayHero write routes answer 403, the pay page offers no PayHero method and
initiation refuses. Payments to the platform are not gated.

### Shared-account tenants

A tenant in `platform_root` mode collects into its own paybill or till added on the platform's
PayHero account. The platform owner assigns the channel to it
(`POST /platform/gateways/payhero/channels/{id}/assign`); tenants cannot claim channels. The
platform never lists, routes to or maps an assigned channel, and the tenant's collections are its
own (its intent, its ledger, never platform revenue or a payout owed). Its payments are always
relayed through the platform's wallet and paid on to its channel, so PayHero's charge comes out of
each payment and nothing is billed to the tenant later.

### Fees and collection routes

PayHero charges in two places:

- **Channel collections** (straight into a paybill, till or bank): a flat fee per amount band from
  PayHero's published tariff (`/api/transaction_fees`, mirrored daily into the platform fee rules
  for gateway `payhero`), taken from the account's service wallet.
- **Wallet deposits and payouts**: a charge kept out of the money itself; the service wallet is
  never used. PayHero does not publish these charges. It reports them on each line of the
  account's ledger (`GET /api/v2/transactions`, field `cost`).

Each tenant picks a **collection route** (`collection_route` on `PUT /{tenant}/gateways/payhero`):

| Route | Behaviour |
|---|---|
| `auto` (default) | The channel while the service wallet covers the band fee, unless a relay is measured to be cheaper at this amount; a relay when the service wallet is short. |
| `relay` | Always collect into a payments wallet and pay the channel on. |
| `channel` | Always straight to the channel; refused while the service wallet is empty. |

A shared-account tenant always relays. The relay is carried by the tenant's own wallet when
PayHero lets it prompt customers into it (own PayHero account, or a Team at KYC tier 3), otherwise
by the platform's root wallet (platform setting `payhero.relay_platform_carrier`, on by default),
which pays the tenant's channel straight on. Escrow, platform billing, personal and offline
payments are never relayed.

Relays are priced from a table of charges PayHero really made, read back from the carrier's
ledger after every relay (job "payhero relay costs", every 15 minutes) and stored once per fact:
a charge already stated by the table (the same amount, or an amount inside a range whose ends
already predict it) is not stored again. `auto` treats a relay as cheaper only when its charges
were measured near the amount.

Who pays: the tenant's `fee_bearer` (default `payer`). With `payer` the fee is added to the prompt
(quote: `GET /pay/{tenant}/fees/payhero`, which runs the same route choice) and booked as a
recovered charge (4600); on a relay the surcharge is the relay's, and the channel receives exactly
the price. With `merchant` the payer is prompted for the price; on a relay the channel receives
the price less PayHero's charge. A relay's charge is booked Dr 5100 M-Pesa Transaction Fees / Cr
the account the payment settled into, and corrected to PayHero's real charge once it is read when
the tenant's own wallet carried it. Nothing is billed to a tenant afterwards. Payments to the
platform, escrow and personal collections are never surcharged.

## What customers are offered

PayHero is its own gateway, separate from Daraja M-Pesa. `GET /api/v1/pay/{tenant}/gateways`
lists `payhero` only when the tenant's account can take a payment (it has a Team or its own
account), with its rails in `payhero_methods`:

```json
{"gateways":["paystack","payhero","cod"],"payhero_methods":["mpesa"],"providers":{}}
```

- The rails come from PayHero's discovery for the payment's country (M-Pesa, Airtel, MTN, other
  networks, card, bank). If discovery is unavailable, M-Pesa alone is offered.
- Only Kenyan M-Pesa is offered until the platform service config `payhero.global_rails_verified`
  is `true`. Every other rail runs on `POST /api/global/payments`, which has not been seen to settle:
  live discovery (2026-10-07) lists deposit networks only, no withdraw network in any country, and
  an empty `merchant_id` that its provider (bitpay) requires. Kenyan M-Pesa collections and M-Pesa,
  paybill and till payouts use the V1 endpoints and are proven live. Bank, Airtel and cross-border
  payouts are refused before PayHero is called.
- `mpesa` in `gateways` means Daraja only (the business's own paybill or till).
- The offline paybill (`payhero_offline`) is offered only when the business switched it on and the
  platform has confirmed it with a live payment (`payhero.offline_paybill_verified`).

The payment page shows one PayHero option that opens a checkout listing these rails. Each rail is
started with `gateway: "payhero"` on the initiate call, which pins PayHero: the payment never falls
back to the business's Daraja account. The POS shows one PayHero tender; STK Push and C2B (matching
a payment the customer already made to the till) are Daraja only.

## Collections

| Rail | Endpoint |
|---|---|
| Kenyan M-Pesa | `POST /api/v2/payments` with the routed channel (or the Team wallet) |
| Every other pay-in (other countries, Airtel, MTN, card, bank) | `POST /api/global/payments` |
| Offline paybill | V1 collection with `is_offline: true` |

**Country and currency.** The payment's currency picks the country's rails (KES on Kenya's, UGX on
Uganda's, and so on); the tenant's configured country is the fallback and also drives which
networks the pay page lists. Each rail charges in its own country's currency, so a payment in
another currency (say a USD invoice paid by M-Pesa) is converted at the stored exchange rate and
rounded up to whole units. The conversion is kept on the payment intent, settlement checks the
amount against it, and the ledger still posts the intent's own currency and amount. With no rate
available the payment is refused rather than charged in the wrong currency.

**Offline paybill.** For payers who cannot take a phone prompt. The pay page shows PayHero's
paybill and an account number; the payer pays from the M-Pesa menu and the payment settles like
any other when PayHero's callback arrives.

**Prompt guard.** Every gateway that sends a prompt to the payer's phone goes through one guard:
after repeated failed or cancelled prompts to the same phone (or many for the same tenant) in a
short window, further prompts pause and the payer is pointed to the offline paybill. A successful
payment clears the count for that phone.

## Where the money lands in the books

Each synced channel maps to one of the tenant's financial accounts (Banking, Accounts). On sync,
an unmapped channel is matched by account number, or to the only account at the bank named in the
channel; the tenant can change it by hand. The Team wallet maps to an account too. When a
collection settles, its ledger entry debits the mapped account, so each account's balance follows
the money.

Each payment is booked once: a gateway payment of an invoice posts one receipt per payment
intent (enforced in the database), the invoice's paid amount changes under a row lock once per
intent, and voiding a manual payment removes only that payment.

## Callbacks

`POST /api/v1/webhooks/payhero`. PayHero callbacks are not signed, so a callback is only treated
as a hint: treasury looks the payment up with PayHero's transaction status endpoint before settling
it through the single settlement path. Payout callbacks are confirmed the same way, and a payout
whose callback never arrives is looked up again after 15 minutes.

Payments made on a PayHero dashboard Payment Link have no treasury intent and cannot be attributed
to a tenant from the callback, so they are logged only. Tenants can still save their Payment Link
and Hosted Checkout URLs in treasury to share them.

## Payouts and wallet withdrawals

Kenyan phones, paybills and tills are paid out through V1 withdraw; everything else through the
global withdrawal endpoint. Payouts come from the tenant's own account and follow the tenant's
payout approval policy; the one exception is a relay the platform's wallet carried, which the
platform pays on to the tenant's channel (it shows in the tenant's withdrawal history).

A tenant moves money out of its Team wallet with `POST .../wallet/withdraw` to one of its own
channels or a phone. The disbursement approval policy applies (the request returns
`409 approval_required` until approved). When the payout succeeds, the amount moves between the
mapped accounts in the books. PayHero takes the withdrawal charge from the wallet itself.

## KYC

Collecting from the public into a Team wallet needs KYC tier 3 (national ID plus the company's KRA
PIN). Verification checks are billed by PayHero, so a check only runs when the request confirms
the charge (`confirm: true`; otherwise `428`). Treasury stores each check's lookup token, verified
name and status, never the numbers entered. Tiers are refreshed daily.

## API routes

Tenant routes live under `/{tenant}/gateways/payhero` (reads need `treasury.gateways.view`,
writes `treasury.gateways.manage`):

| Method | Path | Purpose |
|---|---|---|
| GET | `` | Status: mode, Team, KYC, channels, routing, links, verifications |
| PUT / DELETE | `` | Enable or change mode / disable |
| POST | `/team`, `/team/link`, `/team/invite` | Create the Team; link an existing Team; invite an admin |
| POST | `/channels/sync`, `/channels/{id}/claim` | Sync channels; claim a root-account channel (`platform_root`) |
| PATCH | `/channels/{id}` | Switch a channel on or off |
| PUT | `/channels/{id}/account`, `/wallet-account` | Map a channel or the wallet to a financial account |
| PUT | `/routing`, `/payment-links` | Channel routing; saved Payment Links |
| GET | `/routing/options` | Payment types this tenant can route |
| GET | `/balance`, `/discovery?country=` | Team wallet balance; rails for a country |
| POST / GET | `/wallet/withdraw`, `/wallet/withdrawals` | Withdraw from the Team wallet; recent withdrawals |
| GET / POST | `/kyc/pricing`, `/kyc/checks`, `/kyc/verify/{check}`, `/kyc`, `/kyc/refresh` | KYC and verification |

Platform routes: `GET/PUT /platform/gateways/payhero/settings`,
`POST /platform/gateways/payhero/settings/detect`, `GET /platform/gateways/payhero/teams`,
`POST /platform/gateways/payhero/teams/{tenantID}/link`.

## Background jobs

| Job | Every | Purpose |
|---|---|---|
| Channel sync | 15 minutes | Keep every tenant's channels current |
| KYC sync | 24 hours | Refresh Team KYC tiers |

Each runs once per period across all treasury replicas.
