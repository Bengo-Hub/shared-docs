# SRDD source documents

> **Confidential.** Keep this folder out of the public documentation site. It sits outside `docs/`, so `mkdocs build` never reads it, and it is listed in the repository `.dockerignore`.

These are the three documents the SRDD consolidates, kept exactly as supplied. `text/` holds plain-text extracts of each, so they can be searched and diffed. Regenerate the extracts with `python3 build/tools/extract-sources.py` (requires `pypdf`).

| File | Author and date | Pages | What the SRDD takes from it |
|---|---|---|---|
| `AELIA_Creator_Commerce_System_Requirements_MVP_Specification.pdf` | Erick Wanga for Aelia Holdings, v1.0, September 2026 | 6 | Platform model, users, objectives, the 18 functional modules, journeys, MVP and not-MVP scope, technical, data and trust requirements, ownership and access (§4.1), the API documentation standard (§4.2), pilot targets, Definition of Done, key decisions (§5.3), and the list of next technical documents (§5.4) |
| `AELIA-Creator-Commerce-Codevertex-Feasibility-Report.pdf` | Codevertex Africa, 21 September 2026 | 23 | Ecosystem reuse assessment, the reference-plus-cache pattern, integration architecture, the transaction swimlane, the 10-step campaign sequence, payout schedules, Campaign Composer lanes, KRA 5% withholding, the Data Protection Act, content disclosure, the phased roadmap and technical risks |
| `AELIA-Creator-Commerce-Project-Proposal-and-Cost-Valuation.pdf` | Codevertex Africa, 26 September 2026 | 22 | **Technical and delivery content only:** scope by release, team and RACI, agile method, sprint cycle, Definition of Done, change control, phases, gates, work breakdown (in days), delivery KPIs and the support model |

## Deliberately excluded from the SRDD

On AELIA's instruction, the SRDD contains no commercial terms. These are governed by a separate agreement:

- equity and revenue share
- cost valuation, payback and repayment terms
- pricing tiers and the ERP subscription cost

The Proposal and Feasibility Report still contain them, so treat both files as commercially confidential.
