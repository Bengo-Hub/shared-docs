# Client Deliverables

Client-facing sales/project documents and their build tooling. These live at the `shared-docs` repo root (not under `docs/`) because they include PDF-generation toolchains (`build/`, `node_modules/`) that don't belong in a static docs site build — this page is just a pointer.

| Deliverable | Location | Purpose |
|---|---|---|
| Codevertex Afya (hospital) quotation | `shared-docs/hospital-quotation/` | Client-facing sales quotation for the hospital management product, plus its markdown-to-PDF build pipeline. |
| Migori Library (MCCL) signoff docs | `shared-docs/library-service/mccl/` | Certificate of Practical Completion and UAT signoff PDFs for a completed library-service deployment. |
| Processa sourcing-traceability architecture | `shared-docs/processa-integration/architecture/` | Architecture and demo-presentation docs for a sourcing-traceability integration, plus its PDF build pipeline. |

Raw API references used to build the integration docs (not documentation themselves): `shared-docs/mpesa apis/Safaricom APIs.postman_collection.json`.
