# BengoBox MVP Countdown Tracker

**MVP Target**: March 17, 2026
**Last Updated**: March 2026. E2E status and domain reference: see e2e-gap-analysis.md (updated with canonical production domains and E2E doc refs). Blocker: DNS for auth subdomains per bengobox-mvp-production-test-report.md.
**Active Outlet**: Busia (ONLY -- Kiambu is post-MVP)

---

> **March 6 corrections**: Previous versions incorrectly stated subscriptions-ui and pos-ui
> could be skipped for MVP -- they CANNOT. All four admin UIs (logistics-ui, inventory-ui,
> subscriptions-ui, pos-ui) are MVP blockers. The only active outlet for launch is **Busia**
> (not Kiambu). See [mvp-critical-path.md](./mvp-critical-path.md) for the consolidated plan.

---

## Service Status Dashboard

| Service | Backend | Frontend | K8s | Auth | PWA | Status |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
| Auth | 0 errors | 15 routes, 0 errors | Deployed | Zustand+JWT | Workbox | READY |
| Ordering | 0 errors, 37 tests | 19 routes, 0 errors | Deployed | Zustand+JWT | Workbox | READY (67 tests) |
| Logistics | 0 errors, 35 tests | rider-app: 7 routes; **logistics-ui: SCAFFOLDED (code complete)** | Configured | SSO/PKCE | PWA | rider-app READY; logistics-ui needs API wiring |
| Inventory | 0 errors, 14 tests | 8 API endpoints; **inventory-ui: SCAFFOLDED (code complete)** | Configured | SSO/PKCE | PWA | API ready; inventory-ui needs API wiring |
| Cafe Website | N/A | 22 routes, 0 errors | Deployed | NextAuth | No | READY (needs real API integration) |
| POS | 0 errors | **pos-ui: SCAFFOLDED (code complete)** | Deployed (API) | SSO/PKCE | PWA | Needs API wiring |
| Subscription | 0 errors | **subscriptions-ui: SCAFFOLDED (code complete)** | Deployed | SSO/PKCE | PWA | Needs API wiring |
| Treasury | 0 errors | **treasury-ui: SCAFFOLDED (code complete)** | Deployed | SSO/PKCE | PWA | Needs API wiring |
| Notifications | 0 errors | Minimal admin UI | Deployed | N/A | N/A | Backend ready |
| Treasury | 0 errors | N/A | Deployed | N/A | N/A | Backend ready |

---

## Weekly Checkpoints

### Week 1 (Feb 15-21) — Blockers + MVP Features
- [x] Rider-app auth (Zustand + ProtectedRoute)
- [x] Rider-app login + 5 core pages
- [x] Rider-app PWA manifest + service worker
- [x] K8s values.yaml updated with SSO URL
- [x] 4 architecture docs updated
- [x] Rider-app plan.md populated
- [x] `pnpm run build` passes (7 routes, 0 errors)
- [x] Inventory service MVP (5 Ent schemas, 8 endpoints, 39 seed items)
- [x] Cart persistence (Zustand persist middleware)
- [x] Event wiring fix (ordering.order.ready subject)
- [x] Treasury webhook config (M-Pesa callback URL)
- [x] Order history pages (list + detail)
- [x] Loyalty dashboard page
- [x] Email verification page
- [x] Proof of delivery UI (rider-app)
- [x] Shared library alignment (httpware v0.2.0, shared-events v0.2.0)

### Week 2 (Feb 22-28) — Testing, Integration & Polish
- [x] Frontend test infrastructure (MSW + Vitest wrapper)
- [x] Ordering-frontend unit tests (stores, hooks, components) — 67 tests across 10 files
- [x] Rider-app test scaffolding + core tests — 10 tests across 2 files
- [x] Inventory service integration tests — 14 handler tests
- [x] Logistics task service unit tests — 16 tests (including state machine)
- [x] Responsive design audit + CSS fixes
- [x] ALL frontends build clean (ordering 19 routes + rider-app 7 routes)
- [x] ALL backends build clean + tests pass (logistics 35, inventory 14, ordering 37)

### Week 3 Sprint (Feb 23–Mar 1) — Critical Fixes ✅
- [x] K8s health probes fixed: /healthz route for ordering-frontend + rider-app (was returning 3xx)
- [x] Stuck K8s Jobs force-deleted (ordering-migrate 30d, isp-migrate 13d Terminating)
- [x] Helm Hook Jobs disabled: entrypoint.sh now runs migrate+seed on every pod startup (idempotent)
- [x] logistics-api self-contained: entrypoint.sh + logistics-seed binary in Dockerfile
- [x] OIDC path fixed on ALL frontends: /api/v1/authorize (was /api/v1/auth/oidc/authorize → 404)
- [x] SSO client_id defaults set (ordering-ui, rider-app)
- [x] auth-api seed: upsert OAuth clients; correct redirect_uris for all 4 frontends
- [x] Rider invitation landing page (/join) with SSO redirect + tenant context
- [x] Post-approval redirect: pending → /[orgSlug]/profile (not root)
- [x] Order rating: backend (1-5 stars, Ent schema, API endpoint) + frontend dialog
- [x] POD photo: base64 compress + encode on client (no MinIO required for MVP)
- [x] build.sh standardized for all services (SHA tags, centralized devops scripts)

### Week 4 (Mar 1-7) — Integration + Deployment
- [ ] E2E customer order flow verified (browser)
- [ ] E2E rider delivery flow verified (browser)
- [ ] E2E rider invitation flow verified
- [ ] Cafe website SSO fix: refresh token URL use `/api/v1/token`; AUTH_CLIENT_ID=cafe-website (see e2e-gap-analysis.md)
- [ ] Cafe website + ordering-frontend: use seeded backend data (no mock); set production API URLs and NEXT_PUBLIC_USE_DUMMY_DATA=false
- [ ] Cafe website content finalized
- [ ] M-Pesa status determined
- [ ] All services deployed to K8s staging
- [ ] Security hardening review
- [ ] Performance verification

### Week 4 (Mar 8-17) — UAT + Launch
- [ ] Client UAT completed
- [ ] UAT bugs fixed
- [ ] Go/No-Go decision made
- [ ] All repos tagged v1.0.0-mvp

---

## Progress Summary

| Phase | Feb 14 | Feb 16 | Feb 24 | Mar 6 | Target |
|:---|:---:|:---:|:---:|:---:|:---:|
| Overall Completion | 73% | 87% | 93% | **85%** | 100% |
| Backend Services | 90% | 96% | 98% | **95%** | 100% |
| Frontend Applications | 80% | 90% | 95% | **82%** (5 UIs scaffolded; API wiring pending) | 100% |
| Infrastructure & DevOps | 95% | 98% | 100% | **100%** | 100% |
| Testing | 60% | 75% | 75% | **75%** | 80%+ |
| Website Content & Polish | 40% | 40% | 40% | **45%** | 90% |

> Note (Mar 6): logistics-ui, inventory-ui, subscriptions-ui, pos-ui, treasury-ui are all scaffolded
> with full Next.js apps (SSO, platform admin, PWA). Menu-inventory SKU linkage done. SSO/API base
> URL fixes and devops config updates applied. Atlas migrations skipped for MVP.

---

## Risk Register

| Risk | Impact | Mitigation | Status |
|:---|:---|:---|:---|
| M-Pesa till not received | Payment blocked | COD only for MVP | Monitoring |
| PWA + Next.js 16 Turbopack | Build fails | Use --webpack flag | Resolved |
| Single dev bandwidth | Cannot complete all | **subscriptions-ui, logistics-ui, inventory-ui, pos-ui are all REQUIRED for MVP**; notifications-ui minimal admin is sufficient; defer P2 features | Active |
| Rider-app scope creep (GPS/push) | Delayed | GPS/push are post-MVP | Accepted |
| Inventory service (was blocker) | Ordering can't validate stock | MVP implemented with 8 endpoints | **Resolved** |
| Event wiring mismatch | Orders not forwarded | Subject corrected | **Resolved** |
| Cart data loss on refresh | Poor UX | Zustand persist middleware | **Resolved** |
| OIDC 404 on all frontends | Users can't log in | Fixed path /api/v1/authorize in all frontends | **Resolved** |
| K8s probes failing (3xx on /) | Pods unhealthy | /healthz route added, probes updated | **Resolved** |
| :latest image tags | No rollback, ImagePullBackOff risk | All build.sh use commit SHA | **Resolved** |
| POD photo storage (no MinIO) | Photo lost on session end | Base64 encode to task metadata | **Resolved for MVP** |
| Busia-only outlet not enforced | Multi-outlet UI confuses staff | Busia-only enforced in frontends and inventory seed | **Resolved** |
| 5 MVP UIs need API wiring | logistics-ui, inventory-ui, subscriptions-ui, pos-ui, treasury-ui scaffolded | Wire each UI to its backend API; deploy via devops-k8s | **OPEN** |
| Menu-inventory SKU linkage missing | Orders cannot deduct stock | 39 menu items seeded with SKUs; inventory client wired | **Resolved** |
