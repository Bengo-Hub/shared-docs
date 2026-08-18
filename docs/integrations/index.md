# Integrations

Payment gateways and third-party/cross-service integration contracts.

| Doc | Covers |
|---|---|
| [Payment Workflow](payment-workflow.md) | The hub: invoice-first pattern, shared pay page, intent creation/initiation — read this first regardless of which gateway you're integrating. |
| [M-Pesa (Daraja) Reference](mpesa-integration-reference.md) | Safaricom Daraja API technical reference (STK push, B2C, config tiers). |
| [Paystack Reference](paystack-integration-reference.md) | Paystack API technical reference (transactions, transfers, settlements). |
| [Paystack Callback Page](paystack-callback-page.md) | The frontend contract for the public Paystack redirect-callback page. |
| [Notifications REST API](notifications-rest-api-integration.md) | How non-Go services (TruLoad/.NET, ERP/Python) send notifications without NATS. |
| [Finance Integration Map](finance-integration-map.md) | How each service's events post into treasury's general ledger. |
| [eTIMS API — External Integrator Quickstart](etims-api.md) | For companies integrating KRA eTIMS fiscalization directly against our API, outside the full Codevertex SaaS suite. |
| [Developer Portal — Current State & Roadmap](developer-portal.md) | What's ecosystem-wide vs. eTIMS-specific in the credential/environment/certification/rate-limit pattern, and what's still roadmapped. |
