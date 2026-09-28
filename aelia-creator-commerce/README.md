# AELIA Creator Commerce: System Requirements & Design Document (SRDD)

The single consolidated system requirements and design specification for the **AELIA Creator Commerce Platform**, a brand and creator marketplace built on the Codevertex ecosystem. It combines three sources into one development baseline:

- the AELIA System Requirements & MVP Specification (v1.0, September 2026)
- the Codevertex Technical Partnership & Feasibility Report (21 September 2026)
- the technical and delivery content of the Codevertex Project Proposal (26 September 2026)

It also includes the eight "next technical documents" from the requirements specification (§5.4) as Parts C–L.

Commercial terms between the parties are out of scope. They are governed by a separate agreement.

> **Confidential and not published.** This folder is outside `docs/`, so the public MkDocs site and GitHub Pages never include it. It is also excluded from the shared-docs Docker build context (`.dockerignore`).

| Artifact | Path |
|---|---|
| SRDD source (Markdown) | [`AELIA-Creator-Commerce-System-Requirements-and-Design.md`](AELIA-Creator-Commerce-System-Requirements-and-Design.md) |
| Rendered PDF (A4, about 88 pages) | `AELIA-Creator-Commerce-System-Requirements-and-Design.pdf` |
| Source documents consolidated, with text extracts | [`sources/`](sources/README.md) |
| Chart generator and generated SVGs | `charts/build_charts.py`, `charts/*.svg` |
| Planning notes and review decisions | [`notes/srdd-plan.md`](notes/srdd-plan.md) |
| Facts to confirm against the local Codevertex repos | [`notes/fact-check-checklist.md`](notes/fact-check-checklist.md) |
| PDF build pipeline and QA tools | `build/` (`build-pdf.cjs`, `shared.cjs`, `tools/`) |
| Logo | `media/codevertex-logo.svg` |

## Document map

| Part | Content |
|---|---|
| Front matter | Document control, source traceability, resolved decisions, glossary |
| A · Product & Requirements | Platform model, actors, objectives, 129 functional requirements tagged MVP / v1 / Later, journeys, NFRs, release scope, future enhancements backlog |
| B · Methodology & Delivery | Agile sprint method, Definition of Done, change control, governance and RACI, phases D and P0–P5, gates G1–G5, work breakdown |
| C · Technical Architecture | Principles, context and containers (Go, Next.js PWA, PostgreSQL, Redis, NATS JetStream), modules, Codevertex integration map, event standards |
| D · Pluggable Integration Framework | Ports and adapters, the Codevertex default profile, declarative REST connector, configuration model, inbound and outbound webhooks, callback URLs, provider swap scenarios |
| E · API Specification | Conventions, endpoint catalogue, event catalogue, shared-service API documentation register |
| F · Data Model | Data architecture, ER diagrams, entity dictionary, ownership, retention |
| G · Workflows | Transaction swimlane, campaign and participant state machines, content and dispute flows |
| H · UI/UX | UX principles, sitemap, wireframe illustrations, screen inventory, design system and PWA behaviour |
| I · Security & Data Protection | Threat model, auth and RBAC, controls, ownership and access, Kenya DPA 2019 compliance, breach response |
| J · Payment Integration | Licensed-rail principle, funding and payout flows, Treasury extensions, double-entry ledger, tax engine, reconciliation |
| K · Test & UAT Plan | Test levels, critical money scenarios, adapter conformance suite, UAT scripts, gate acceptance |
| L · Deployment & Support Runbook | Pipeline, environments, Kubernetes, release, monitoring, backup, support SLAs, runbooks, technical risks, traceability, sign-off |

## Local review workflow

```bash
git pull origin claude/keen-lovelace-4zpscj
cd aelia-creator-commerce/build
npm install                        # first time only: markdown-it, mermaid 9.4.3, puppeteer-core, pdfjs-dist

# 1. check facts against the local service repos: work through ../notes/fact-check-checklist.md
# 2. edit ../AELIA-Creator-Commerce-System-Requirements-and-Design.md
npm run charts                     # regenerate ../charts/*.svg; prints requirement counts for §7.2
npm run build                      # -> ../AELIA-Creator-Commerce-System-Requirements-and-Design.pdf
npm run preview -- '#sec-22'       # screenshot a section to build/shots/ (visual QA)
npm run audit -- 700               # list near-empty pages (layout QA)
npm run sources                    # optional: re-extract ../sources/text/*.txt (needs pip install pypdf)
```

On Windows, the build finds Chrome or Edge in the standard install paths. Set `PUPPETEER_EXECUTABLE_PATH` to use another browser. In Linux containers, it also finds the Playwright Chromium under `/opt/pw-browsers`.

### How the build works

The build renders the Markdown into the Codevertex house-style HTML shell:
- a cream and plum cover
- a TOC grouped by Part
- Mermaid diagrams, SVG charts and HTML illustrations

The shell is then printed to A4 with Chrome. The build prints twice: after the first pass, `pdfjs-dist` reads back the real page of every section, and the second pass writes exact TOC page numbers. It reports any Mermaid diagram that fails to render, and scales diagrams taller than a page to fit. The pipeline is adapted from `processa-integration/architecture/build/`.

## Editing conventions

- **Headings:**
  - `## Part X · Title` opens a new Part. It starts a new page, uses the gradient banner, and becomes a TOC group.
  - `## N. Title` is a numbered section.
  - `### N.M` is a subsection.
- **Release tags:** write `[MVP]`, `[v1]` or `[Later]` anywhere to get the coloured release pill.
- **Diagrams:** use ```` ```mermaid ```` fences. Mermaid is pinned to 9.4.3, so:
  - avoid `;` in sequence messages
  - avoid em and en dashes in node labels
  - use `<br/>` for line breaks
  - diagrams taller than a page are scaled to fit automatically
- **Figure captions:** `<p class="fig">Figure N. …</p>`, with `<code>` for code inside.
- **Charts:** a `<!-- chart:NAME -->` marker inside `<div class="chart">…</div>` is replaced at build time by `charts/NAME.svg`. Change chart data in `charts/build_charts.py`. The scope chart counts `[MVP]`/`[v1]`/`[Later]` tags in the requirement tables automatically.
- **Other HTML blocks:** stat tiles (`.kpis` / `.kpi`), illustrations (`.mocks`, `.swim`, `.layers`, `.uc`, `.stflow`), and `<div class="tight">` for dense tables. See the CSS in `build/build-pdf.cjs`.
- **Keep it SRDD-only.** Commercial terms belong in the separate agreement.
