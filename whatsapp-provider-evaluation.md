# WhatsApp Provider Evaluation — ISP Billing Phase 4 Delivery Consolidation

**Date:** June 2026
**Context:** Phase 4 moves notification DELIVERY from isp-billing-backend onto the central
notifications-api. As part of this we evaluated whether to keep APIWap (the current isp-billing
WhatsApp provider) or adopt a cheaper / more reliable provider for the Kenya/Africa market.

## Candidates

| Provider | Type | Cost model | Reliability | Notes |
|----------|------|-----------|-------------|-------|
| **APIWap** (current) | Unofficial reseller / instance gateway | Flat monthly per instance, opaque per-msg | Medium — non-official, depends on a single reseller instance staying connected; risk of bans/disconnects | Already integrated in both services; kept as fallback. |
| **Meta WhatsApp Cloud API** (direct) | Official Meta first-party | Per-message, by category + country; **no BSP markup**. Utility/Auth messages (the ISP billing use case: receipts, expiry reminders, OTP) are the cheapest categories (~$0.008–0.012 utility, lower for Africa) | Highest — official Meta infrastructure, hosted by Meta (no instance to keep alive) | Free dev tier; requires a registered WhatsApp Business phone-number-id + permanent access token. Templates must be pre-approved by Meta. |
| Twilio WhatsApp | BSP | Meta base fee **+ $0.005/msg** Twilio markup | High | More expensive than Meta direct for our volume. |
| Wati | BSP | Meta base fee **+ 20%** per message + monthly platform fee | High | Most expensive per message; UI-centric, not needed (we send programmatically). |
| Celcom Africa (local KE) | Local BSP | From ~KES 0.25/msg + KES 15k setup + KES 15k/mo | Medium | Cheap per-message but high fixed monthly + setup; local-only. |

## Decision: **Meta WhatsApp Cloud API (direct)** — registered as `meta_cloud`

**Why:**
1. **Cheapest sustainable cost.** Direct Meta pricing has no BSP per-message markup (Twilio +$0.005,
   Wati +20%). Our traffic is almost entirely Utility/Authentication category (payment receipts,
   subscription-expiry reminders, OTP), which is Meta's cheapest tier, and Rest-of-Africa rates are low.
2. **Reliability.** First-party, Meta-hosted — no reseller "instance" to keep connected (APIWap's main
   failure mode). No extra platform monthly fee like Wati/Celcom.
3. **Official + future-proof.** Template approval and webhooks are first-class; aligns with how the rest
   of the platform integrates messaging.

**APIWap is retained as a fallback** (not deleted) so existing tenants keep working while `meta_cloud`
is rolled out per-tenant via ProviderSetting.

## Integration

- New provider: `notifications-api/internal/providers/whatsapp/metacloud.go` implementing the existing
  `WhatsAppProvider` interface (same shape as `apiwap.go`).
- Registered in `internal/providers/manager.go` `GetWhatsAppProvider`. Selection order is
  `[meta_cloud, apiwap]` (meta_cloud preferred, apiwap fallback); a tenant/platform `_preferred` row or
  a `metadata.provider` override still wins.
- Credentials via the existing `ProviderSetting` mechanism (channel=`whatsapp`, provider=`meta_cloud`),
  keys: `access_token`, `phone_number_id`, optional `api_version`, `template_mode`. **No secrets in code**
  — values come from ProviderSetting rows / env placeholders.

## Sources
- [WhatsApp Business API Costs 2026 — Chatarmin](https://chatarmin.com/en/blog/whatsapp-business-api-costs)
- [WhatsApp Business API Pricing 2026 — Blueticks](https://blueticks.co/blog/whatsapp-business-api-pricing-2026)
- [Meta WhatsApp Pricing 2026 — go4whatsup](https://www.go4whatsup.com/guides/meta-whatsapp-pricing/)
- [Twilio WhatsApp Messaging Pricing](https://www.twilio.com/en-us/whatsapp/pricing)
- [WhatsApp API Provider Cost Comparison 2026 — EZContact](https://ezcontact.ai/en/blog/whatsapp-api-pricing-comparison-meta-twilio-360dialog-ezcontact/)
- [WhatsApp Business API Africa 2026 — AfroTools](https://afrotools.com/blog/whatsapp-business-api-africa-2026/)
- [Bulk WhatsApp Business API (Kenya) — Celcom Africa](https://celcomafrica.com/blog/how-to-integrate-bulk-whatsapp-business-api/)
