# Sourcing & Traceability Platform — Technology Architecture (Processa Integration)

Canonical architecture documentation for integrating Processa's agro-processing farm-to-shelf
domain (grower sourcing, intake grading, lot traceability, quality assurance, processing,
packaging, distribution) into the Codevertex micro-service ecosystem, without duplicating any
existing system of record.

| Artifact | Path |
|---|---|
| Source (Markdown, portrait report) | [`processa-integration-architecture.md`](processa-integration-architecture.md) |
| Source (Markdown, landscape flow deck) | [`processa-integration-demo-presentation.md`](processa-integration-demo-presentation.md) |
| Rendered PDF (portrait) | `Codevertex-Sourcing-Traceability-Architecture.pdf` |
| Rendered PDF (landscape) | `Codevertex-Sourcing-Traceability-Flows.pdf` |
| Logo | `media/codevertex-logo.svg` |
| Build pipeline | `build/` |

## Regenerate the PDFs

```bash
cd build
npm install               # first time only (markdown-it, mermaid, puppeteer-core)
node build-pdf.cjs        # -> ../Codevertex-Sourcing-Traceability-Architecture.pdf (portrait report)
node build-presentation.cjs  # -> ../Codevertex-Sourcing-Traceability-Flows.pdf (landscape flow deck)
```

The build renders each Markdown source to a branded HTML shell (plum cover with the Codevertex
logo, TOC or slide numbering, mermaid diagrams) and prints it to A4 via the locally-installed
**Chrome** (`puppeteer-core`; no Chromium download). Set `PUPPETEER_EXECUTABLE_PATH` to override
the browser.

This toolchain is a direct copy of `finance-service/treasury-api/docs/architecture/build/`
(the fleet's only PDF-doc pipeline — see `[[reference: treasury-api docs/architecture]]`),
adapted to a single brand logo (no second-party logo) and rebranded content.

## Editing the document

- **Portrait report** (`processa-integration-architecture.md`): each top-level `## ` heading is one
  numbered TOC entry / report section.
- **Landscape flow deck** (`processa-integration-demo-presentation.md`): each top-level `## `
  heading becomes **one landscape slide** — keep each section short enough to fit one A4-landscape
  page (the renderer clips overflow, it does not paginate a section across slides).
- Diagrams are authored as ```mermaid fenced blocks (`flowchart LR/TB` with `subgraph` clusters,
  `sequenceDiagram`). Mermaid is pinned to **9.4.3** — avoid `;` inside sequence messages and
  em/en-dashes (`—` `–`) inside flowchart node labels (use `<br/>` for line breaks, `<i>` for
  italics).
- Re-run the relevant build script after any edit.
