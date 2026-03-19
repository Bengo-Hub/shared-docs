# Go Backends: Ent Schema & Atlas Versioned Migrations

**Reference implementation:** `mosuon/game-stats/game-stats-api` and `logistics-service/logistics-api`.

This doc describes how to keep Ent schemas and migrations consistent across Go backends: **always generate Ent and Atlas migrations after schema changes**, never add migration files manually, and follow the same pattern as game-stats-api and logistics-api.

---

## 1. After Updating Schemas

1. **Regenerate Ent code**  
   From the backend root (e.g. `ordering-service/ordering-backend`, `inventory-service/inventory-api`):
   ```bash
   go generate ./internal/ent
   ```
   For game-stats-api (ent at repo root):
   ```bash
   go generate ./ent
   ```
   This regenerates all ent-generated code from `internal/ent/schema/*.go` (or `ent/schema/*.go`).

2. **Generate a new Atlas migration** (versioned SQL)  
   Do **not** add or edit `*.sql` migration files by hand. Use the migration diff command:
   - **game-stats-api:** `go run -mod=mod ent/migrate/main.go <migration_name>` (requires DB URL in the script; uses `migrate.NamedDiff`).
   - **logistics-api / ordering-backend:** Use `cmd/migrate/main.go` or a similar `ent/migrate/main.go` that calls `migrate.NamedDiff(ctx, databaseURL, migrationName, opts...)` with `schema.WithDir(dir)` and `schema.WithMigrationMode(schema.ModeReplay)`.

   This writes new `YYYYMMDDHHMMSS_migration_name.sql` (and updates `atlas.sum`) in the migrations directory.

3. **Run migrations at startup**  
   Use **versioned** migrations in the app so that the same SQL files are applied in every environment. In app bootstrap (e.g. `internal/app/app.go` or `internal/infrastructure/database/postgres.go`):
   ```go
   import (
       "entgo.io/ent/dialect/sql/schema"
       "yourmodule/internal/ent/migrate"
   )
   // ...
   if err := entClient.Schema.Create(ctx, schema.WithDir(migrate.Dir)); err != nil {
       return nil, fmt.Errorf("migrations: %w", err)
   }
   ```
   **Do not** use only `Schema.Create(ctx)` with no `WithDir`; that is auto-migrate (no versioned history). Prefer `Schema.Create(ctx, schema.WithDir(migrate.Dir))` so the app applies the same versioned migrations as in CI/local.

---

## 2. Reference Pattern (game-stats-api)

| Piece | Location | Purpose |
|-------|----------|---------|
| **Migration dir** | `ent/migrate/migrations/` (or `internal/ent/migrate/migrations/`) | Holds `*.sql` and `atlas.sum`. Committed to git. |
| **migrations.go** | `ent/migrate/migrations.go` | `//go:embed migrations/*.sql migrations/atlas.sum`; `init()` sets `Dir, _ = atlasmigrate.NewLocalDir("ent/migrate/migrations")`. |
| **migrate/main.go** | `ent/migrate/main.go` (build ignore) | Runs `migrate.NamedDiff(ctx, dbURL, os.Args[1], schema.WithDir(dir), schema.WithMigrationMode(schema.ModeReplay), ...)` to generate a new migration file. |
| **DB connect** | `internal/infrastructure/database/postgres.go` | `NewClient` calls `client.Schema.Create(ctx, schema.WithDir(migrate.Dir))` so startup applies versioned migrations. |

---

## 3. Checklist for Each Go Backend Using Ent

- [ ] After any change to `internal/ent/schema/*.go`: run `go generate ./internal/ent`.
- [ ] To add a new migration: run the project’s migrate diff command (e.g. `go run ent/migrate/main.go <name>` or `cmd/migrate` with NamedDiff); do **not** create or edit `*.sql` by hand.
- [ ] At app startup: use `Schema.Create(ctx, schema.WithDir(migrate.Dir))` (or equivalent) so versioned migrations are applied.
- [ ] Seed data: run idempotent seed (e.g. `go run cmd/seed/main.go`) after migrations; optionally run seed from the same process after `Schema.Create` for “migrate + seed on pod startup”.

---

## 4. Codebase Scan & Docs

- **Before adding logic:** Search the codebase for existing implementations (same or similar). Prefer refactor/reuse; keep architecture uniform. See `.cursor/rules/codebase-scan-and-docs.mdc`.
- **After changes:** Update the relevant docs: `plan.md`, `erd.md`, `integrations.md`, `architecture.md`, and sprint/plan docs so that design and progress stay accurate.

---

## 5. Services to Align

| Service | Current | Target |
|---------|---------|--------|
| **game-stats-api** | Versioned migrations + `WithDir(migrate.Dir)` in DB connect | Reference (no change) |
| **logistics-api** | Versioned migrations + `WithDir(migrate.Dir)` in app startup | Reference (no change) |
| **ordering-backend** | `Schema.Create(ctx)` only (auto-migrate) | Add `schema.WithDir(migrate.Dir)` at startup; use migrate diff to generate SQL. |
| **inventory-api** | Check app startup | Use versioned migrations + WithDir if not already. |
| **pos-api** | Check app startup | Use versioned migrations + WithDir if not already. |
| **auth-api, treasury-api, notifications-api, etc.** | Per-repo | Prefer versioned migrations + WithDir; run ent generate after schema edits; never add migration SQL by hand. |

---

**Summary:** (1) Always run `go generate` for Ent after schema changes. (2) Use Atlas versioned migrations (SQL in a dir + `atlas.sum`); generate new migrations via the project’s diff command; never add migration files manually. (3) At startup, apply migrations with `Schema.Create(ctx, schema.WithDir(migrate.Dir))`. (4) Scan the codebase before adding logic and update the relevant .md docs after changes.
