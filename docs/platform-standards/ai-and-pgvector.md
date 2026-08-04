# AI Integrations & pgvector

## Status: infrastructure scaffolded fleet-wide, one production consumer today (marketflow-ai)

`shared/infrastructure/` has local-dev scaffolding for three AI-adjacent pieces:

- **`pgvector/`** — `docker-compose.yml` + `init-scripts/01-init-extensions.sql` enabling the pgvector Postgres extension, for services that need vector embeddings/similarity search.
- **`ollama/`** — a local LLM runner (`docker-compose.yml` + `start-ollama.ps1`) for local inference without hitting an external API.
- **`onnx/`** — `docker-compose.yml`, `config/`, `models/`, `triton-models/`, suggesting Triton Inference Server for ONNX models.

In prod, `marketflow-ai` is deployed as its own service (namespace `marketflow`, its own DB) — it's the platform's Vera AI assistant, doing KB enrichment and callable read-only tool use against other services' data (a `query_service_data.go`-style pattern: see the KRA/tax-compliance docs for one caller of this pattern). It runs against a two-tier LLM setup with a fallback chain (a fast/cheap model first, escalating to a stronger one on failure) — check `marketflow-ai`'s own service docs for the current model names, since LLM provider model IDs change faster than this doc will be updated.

## If you're building a new AI feature

1. Check whether `marketflow-ai` already exposes the capability you need as a callable tool before building a second AI integration point — it's the platform's designated AI service, not a per-service pattern.
2. If you need vector search, use the `shared/infrastructure/pgvector` extension against your service's own Postgres DB rather than standing up a separate vector database — pgvector as a Postgres extension keeps it inside the existing backup/PgBouncer/connection-pooling story (see [Connection Pooling & PgBouncer](connection-pooling-pgbouncer.md)) instead of adding a new kind of datastore to operate.
3. Don't synthesize a foreign-key-referenced ID (e.g. a deterministic UUID derived from a tenant slug) instead of resolving the real one — this exact mistake broke `marketflow-ai`'s session-to-tenant linkage for two weeks in production before being caught (every `chat_sessions` insert was failing its FK silently). Resolve real IDs from their owning service, never derive a plausible-looking one.

## Known gap

This page is a starting point, not a full architecture doc — a proper "AI integrations" architecture writeup (covering the KB embedding pipeline, tool-calling contract, and cross-service query pattern in detail) doesn't exist yet in shared-docs. If you're doing significant new AI work, consider writing that doc as part of the change rather than assuming this page covers it.
