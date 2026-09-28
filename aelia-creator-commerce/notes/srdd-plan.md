# Plan: AELIA Creator Commerce — System Requirements & Design Document (SRDD)

## Context
Aelia Holdings has three input documents:
- **System Requirements & MVP Specification** v1.0 (Erick Wanga, 6 pp). §5.4 lists 8 "next technical documents": Technical Architecture, API, Database/Data Model, UI/UX, Security & Data Protection, Payment Integration, Test & UAT Plan, Deployment & Support Runbook.
- **Codevertex Feasibility Report** (21 Sep 2026, 23 pp). It covers corrections, competitors, reuse of services, architecture, the swimlane, the Composer lanes, KRA 5% withholding, legal, and a 6-month roadmap.
- **Project Proposal & Cost Valuation** (26 Sep 2026, 22 pp). It covers scope, team, RACI, sprints and gates, WBS, costs, the 30% net-revenue share, and KPIs.

The user wants these combined into **one professional SRDD**. It must include the 8 next documents as parts, plus methodology, architecture, technical specs, flow diagrams, illustrations and charts. It must adapt the Codevertex ecosystem as documented in this repo.

A key new requirement is that every ecosystem dependency be **pluggable and configurable from the AELIA platform**. That covers SSO, notifications, subscriptions/billing, finance/treasury, and also AI, social and AI-video. Codevertex services are loaded as the seeded default configuration. AELIA admins can register an alternative provider through a programming interface (a Go port/adapter SDK) or an API interface (a declarative REST connector), with webhooks and callback URLs.

**Constraints**
- The local `D:\Projects\Codevertex\` repos and previous-session memory are not reachable from this cloud container. `/root/.claude` has no memory files.
- The ecosystem facts will come from this repo's docs:
  - `docs/architecture/*`
  - `docs/integrations/*`
  - `internal/*`
  - `processa-integration/architecture/processa-integration-architecture.md`

**Scope rules for the document (from user review)**
- **Pure SRDD.** Leave out all commercial content: equity, revenue share, cost valuation, payback, pricing tiers, ERP pricing and contract negotiation. An official agreement is being prepared separately. The input documents are used only for requirements, architecture, methodology, timeline and technical facts.
- **Stack is decided by Codevertex, not a proposal.** It is:
  - Go (chi, Ent, Atlas) backend
  - Next.js PWA
  - PostgreSQL through PgBouncer
  - Redis cache
  - NATS JetStream for queues and events
  - the shared libs toolkit (`shared-auth-client`, `shared-service-client`, `shared-events`, `httpware`, `cache`, `shared-ratelimit`, `pagination`, `@bengo-hub/shared-ui-lib`)
  - the shared-docs NATS subject, envelope and outbox standards
- **Full platform coverage.** The functional requirements describe the fully developed platform, including native apps, advanced AI, affiliate commerce and regional expansion. Every feature is tagged **MVP (month 3) / v1 (month 6) / Later (enhancement)**. Only MVP and v1 go into the 3–6 month delivery plan; Later items sit in a separate enhancements backlog.
- **Decisions are recorded as resolved, not open.** Among them: AELIA consumes the **Treasury service only**, not the full ERP suite. This is modelled as a treasury-only entitlement in the subscriptions service, with no pricing figures.

## Deliverables (new folder, mirroring `processa-integration/architecture/`)
`aelia-creator-commerce/`
- `AELIA-Creator-Commerce-System-Requirements-and-Design.md`: the single source document.
- `README.md`: purpose, the source documents it combines, and how to regenerate.
- `media/codevertex-logo.svg`: copied from processa.
- `build/`
  - `package.json`: copied from `processa-integration/architecture/build/` (`markdown-it`, `mermaid@9.4.3`, `puppeteer-core`).
  - `shared.cjs`: add `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` and a glob fallback to `findChrome()`.
  - `build-pdf.cjs`: adapted from processa. Cover: "AELIA Creator Commerce · System Requirements & Design Specification", v1.0, 28 Sep 2026, "Prepared by Codevertex Africa (Titus Owuor, Technical Lead) for Aelia Holdings (Erick Wanga)", classification Confidential. Badges: MVP month 3 · v1 month 6 · Go/Next.js.
  - Keep the plum/cream house palette and the TOC, header and footer.
  - Add CSS for `.chart` inline SVG, `.kpi` stat tiles, and `div.pb` page breaks.
- `.gitignore`: `node_modules/` and `output.html`.
- `AELIA-Creator-Commerce-System-Requirements-and-Design.pdf`: generated and committed, because it is the deliverable (unlike processa's ignored PDFs). It is also sent to the user via SendUserFile.

**Diagrams and charts**
- Mermaid 9.4.3 fences: `flowchart`, `sequenceDiagram`, `stateDiagram-v2`, `erDiagram`, `gantt`, `pie`. Follow the processa README rules: no `;` in sequence messages, no dashes in node labels, `<br/>` for line breaks.
- Hand-built inline SVG charts, all technical:
  - the payout and withholding waterfall
  - team loading per phase
  - the scope distribution (MVP / v1 / Later feature counts per module)
  - an NFR target dashboard of KPI tiles
  - the integration capability matrix

## Document outline (≈45–60 pages)
**Front matter**
- Document Control
- Source-document traceability table, mapping each input section to the SRDD section
- Glossary
- Resolved technical decisions register: the technical and SRDD-relevant items from §5.3, recorded as resolved. Payment architecture, withholding logic, shared services reused (treasury-only), data controller/processor roles, and ownership and access. Commercial and legal-entity items are marked "governed by separate agreement" with no detail.

**Part A: Product & Requirements**
1. Executive summary; platform model (Influence and Content marketplaces); Aelia Brand House context.
2. Stakeholders and actors: Brand, Creator, AELIA Admin, Finance/Admin, Super Admin, and system actors. Includes a use-case diagram.
3. Business objectives and the product differentiators they imply (KES-native contracts, automatic withholding, cross-platform matching, a reconcilable audit trail). Only a short product-context note; no market or commercial analysis.
4. Functional requirements for the **full platform**. The 18 modules, each with numbered `FR-xxx` IDs, a release tag (MVP / v1 / Later) and acceptance criteria.
   - Also covers AELIA Match ("recommend, brand decides"), the Campaign Composer's three lanes, and content-safety/disclosure.
   - Later-phase modules are specified at requirement level: native Android and iOS, predictive AI matching, affiliate and promo-code commerce, regional multi-country and multi-currency, advanced automation, and more AI video vendors.
5. User journeys: Brand 16 steps and Creator 16 steps (flowcharts), and the 10-step campaign sequence.
6. Non-functional requirements (`NFR-xxx`), drawing on the Proposal KPIs:
   - 99.5% uptime; p95 < 500 ms; RTO 4h / RPO 24h; 70% test coverage on money code
   - PWA; accessibility; localisation; multi-currency and country as a per-account setting
7. Release scope matrix (MVP / v1 / Later), the scope-distribution chart, pilot validation targets, and a separate "Future Enhancements Backlog" that is not scheduled in the 6 months.

**Part B: Methodology & Delivery**

8. Delivery methodology: 13 two-week sprints, the sprint cycle diagram, Definition of Done (merging the spec's and the proposal's versions), and the change-control flow.
9. Governance and RACI; the three meeting levels.
10. Roadmap: phases D and P0–P5 as a Mermaid gantt with gates G1–G5, covering MVP and v1 only. The WBS lists work packages and days only, with no KES figures. Includes the team loading chart.

**Part C: Technical Architecture** (next document #1)

11. Architecture principles:
    - AELIA owns its data
    - reference plus cached display name
    - link, don't rebuild
    - event-driven via outbox
    - ports and adapters
12. Context diagram (C4 level 1) and container diagram (level 2):
    - `aelia-api` (Go 1.26, chi, Ent, Atlas)
    - `aelia-worker` (outbox and consumers)
    - `aelia-ui` (Next.js 16 PWA)
    - Postgres through PgBouncer, Redis, MinIO for content assets, NATS JetStream
13. Internal module decomposition (bounded contexts): identity-link, passport, discovery/match, campaign, workspace/messaging, content, contracts/rights, payments/ledger, tax, reputation, reporting, admin, and the integrations hub.
14. Ecosystem integration map. For each service (auth-api, notifications, subscriptions, treasury, marketflow/Vera, shared libs), what AELIA reuses and how: REUSE / EXTEND / PATTERN, citing real endpoints, headers and events from the repo docs.
    - AELIA is a treasury-only consumer: it takes the treasury entitlement through subscriptions and does not use the full ERP.
    - Treasury extensions: a `creator` payee type, a three-way split, and a configurable withholding engine.

**Part D: Pluggable Integration Framework** (the core new design)

15. Integrations Hub design.
    - **Ports** (Go interfaces), each with a default Codevertex adapter and generic alternatives:
      - `IdentityProvider`: codevertex-sso default; generic OIDC (Keycloak, Auth0, Azure AD, Google)
      - `NotificationProvider`: codevertex-notifications; generic SMTP, Africa's Talking, Twilio, Meta WhatsApp, webhook
      - `BillingProvider`: codevertex-subscriptions; built-in plans; Stripe-like REST
      - `PaymentProvider` / `PayoutProvider`: codevertex-treasury; direct Paystack, Flutterwave, generic REST
      - `TaxEngine`
      - `AIMatchProvider`: Vera; rules engine
      - `SocialPlatformConnector`
      - `AIVideoVendor`: HeyGen, Creatify
    - **Configuration model**
      - Tables: `integration_providers`, `integration_bindings` (capability → provider, by platform or tenant scope), `integration_credentials` (encrypted, fingerprint only), `webhook_endpoints`, `webhook_deliveries`
      - Precedence: environment defaults → seeded Codevertex profile → tenant override
      - Features: health checks, a circuit breaker, and a "test connection" action
    - **Declarative REST connector.** An API-interface option that needs no code: base URL, auth scheme (API key header, OAuth2 client-credentials, HMAC), endpoint mapping, and JSONPath request/response templates.
    - **Inbound webhooks**
      - URL: `/api/v1/integrations/{providerId}/webhooks/{event}`
      - Per-provider signature verification (HMAC-SHA256/512, JWT, shared secret)
      - Replay window and idempotency
    - **Outbound callbacks and webhooks to third parties.** HMAC-SHA256 signing (`X-Aelia-Signature` plus a timestamp), retry with backoff, a dead-letter queue, and a delivery log.
    - **Event mapping:** from provider events to canonical `aelia.*` events.
    - **Conformance test suite** that every adapter must pass.
    - **Admin UI:** Integrations Hub screens, and the sequence diagrams for "Swap SSO provider" and "Add payment provider".
    - Default Codevertex configuration table, with the values that are seeded.

**Part E: API Specification** (next document #2)

16. API conventions:
    - REST under `/api/v1/{tenant}/aelia/...`
    - JWT or `X-API-Key` with `X-Tenant-ID`
    - pagination, error envelope, `Idempotency-Key`, rate limits, versioning
    - sandbox vs production environments, and Swagger at `/v1/docs`
17. Endpoint catalogue by module (tables), plus the full API-documentation template from spec §4.2 applied to each external/shared service.
18. Event catalogue: published `aelia.*` subjects (envelope per `shared-events`) and consumed subjects (`auth.*`, `treasury.payment.*`, `treasury.payout.completed`, `subscription.*`).

**Part F: Data Model** (next document #3)

19. ER diagrams by bounded context. Entity dictionary covering users/orgs link, brand, creator, passport, social accounts, campaign, deliverable, application, agreement, rights, submission/revision, message, transaction/ledger, payout, tax withholding, review, dispute, audit, and integration tables.
20. Data ownership matrix versus the Codevertex services, plus retention rules.

**Part G: Workflows & State**

21. The campaign state machine (the 17-state machine from the brief, compressed), the three-lane swimlane, and the content approval states.
22. Payment sequences:
    - funding via Paystack split, M-Pesa, or bank transfer with proof upload
    - the three payout schedules
    - the payout-with-withholding sequence, and the corrected KES 20,000 → 17,400 waterfall chart
    - the commission ledger (double-entry)
    - reconciliation

**Part H: UI/UX Specification** (next document #4)

23. Information architecture and sitemap for Brand, Creator, Admin and Finance. Key screen inventory, wireframe-style illustrations, the design system, and PWA behaviour.

**Part I: Security & Data Protection** (next document #5)

24. Authentication and authorization:
    - trinity RBAC and permission codes `aelia.{module}.{action}`
    - 2FA for admins
    - encryption, secrets, audit log
    - OWASP controls, WAF, rate limits
25. Kenya Data Protection Act 2019 and ODPC: controller vs processor, consent log, DSR flow, retention and deletion, breach response.

**Part J: Payment Integration Specification** (next document #6)

26. Licensed-rail principle (no escrow, CBK PSP licensing), Paystack split-payment, the creator payee type, the three-way split, the configurable tax engine, eTIMS, and withholding certificates.

**Part K: Test & UAT Plan** (next document #7)

27. Test strategy pyramid, conformance tests for integration adapters, UAT scripts per journey, pilot acceptance criteria, and the traceability matrix from FR to tests.

**Part L: Deployment & Support Runbook** (next document #8)

28. Environments:
    - k3s, ArgoCD `apps/aelia-*`, the Helm chart, CI/CD
    - AELIA-owned domain and accounts (spec §4.1 ownership table)
    - monitoring, backups and restore drill, incident severities
    - support SLA (2h critical), handover
29. Technical risks register; assumptions, dependencies and exclusions. Technical items only, such as provider approvals, social API permissions and AI vendor API changes.
30. Appendices:
    - requirements traceability matrix
    - platform agreements the system must support (as data and workflow only: brand/creator terms acceptance, content-rights records)
    - source-document references
    - sign-off block

## Execution steps
1. Scaffold the folder and copy the builder. Generalise the builder's `MD`/`OUT` and cover metadata into a constant block at the top of `build-pdf.cjs`.
2. Write the markdown section by section, drawing facts from the extracted PDF text in the scratchpad and the repo docs listed above.
3. Build:
   ```
   cd aelia-creator-commerce/build && npm install
   PUPPETEER_EXECUTABLE_PATH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome node build-pdf.cjs
   ```
4. Commit with a clear message and push to `claude/keen-lovelace-4zpscj`. Add a CHANGELOG entry only if the repo convention requires it for non-docs folders (processa did not); otherwise skip it. Do not open a PR unless asked.

## Verification
- The build log's "mermaid rendered N" count equals the number of mermaid fences, and the rendered HTML has no Mermaid syntax errors (grep `output.html` for `Syntax error`).
- Screenshot a sample of pages with puppeteer: the cover, the TOC, one diagram page, one chart page, and one table page. Inspect them visually for overflow, clipped diagrams, and working dark-on-cream contrast.
- Check the TOC covers all Parts A–L and that every one of the 8 "next documents" appears.
- Cross-check facts against the sources: dates, KPIs, phase days and withholding maths.
- grep the markdown for `revenue share|equity|30%|1,477|2,223|8,288|payback` and confirm there are no commercial leftovers.
- Send the PDF to the user with SendUserFile.
