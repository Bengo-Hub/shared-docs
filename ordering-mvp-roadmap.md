# BengoBox Platform — MVP Countdown Sprint Plan

**Date**: February 15, 2026
**MVP Deadline**: March 17, 2026 (30 days remaining)
**Developer**: Titus (single dev for all technical work)

---

## Context

The previous sprint (P1-P4, completed Feb 14-15) delivered:
- **P1** ✅ Auth-UI production readiness (forgot password, 2FA, org creation, sessions, API keys)
- **P2** ✅ Auth event publishing (NATS outbox for user/tenant lifecycle)
- **P3** ✅ Subscription lifecycle (state machine, endpoints, product model, 8 products, 3 bundles, 6 plans)
- **P4** ✅ Notifications (SendGrid, Twilio, worker retry with 3 NAck attempts)

This plan addresses what remains for March 17 MVP launch: **documentation updates, rider-app build-out (currently a skeleton), ordering-frontend completion, cross-service integration testing, and production deployment**.

---

## What Was Found (Verified via Codebase Exploration)

### Critical Gaps

| Area | Finding | Severity |
|:---|:---|:---|
| **Rider-App** | SKELETON: 7 source files total. Zero auth, zero real API calls, no TanStack Query, no Zustand, no shadcn/ui, no PWA service worker. `plan.md` is 0 bytes. | **BLOCKER** |
| **Rider-App K8s** | `devops-k8s/apps/rider-app/` directory does NOT exist (despite sprint-report claiming "Created") | **BLOCKER** |
| **Ordering-Frontend** | 70% complete. Missing: unit/E2E tests, outlet list API call, brand config API, analytics embed | MEDIUM |
| **Subscription Sprint Docs** | No `docs/sprints/` directory. Only 5 docs total | HIGH |
| **Notifications Sprint Docs** | No `docs/sprints/` directory | HIGH |
| **Architecture Docs** | `microservice-architecture.md`, `ARCHITECTURE-RECOMMENDATIONS.md`, `CROSS-SERVICE-DATA-OWNERSHIP.md`, `TRINITY-AUTHORIZATION-PATTERN.md` — all missing Feb 14 work (auth events, subscription lifecycle, notification retry) | HIGH |

### What's Production-Ready

| App | Routes | API | PWA | Auth | K8s | Status |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
| Auth-UI | 15 | ✅ | ✅ | ✅ Zustand | ✅ | 🟢 Ready |
| Ordering-Frontend | 14 | ✅ | ✅ | ✅ Zustand | ✅ | 🟡 Ready (no tests) |
| Cafe-Website | 20 | ⚠️ | ❌ | ✅ NextAuth | ✅ | 🟡 Marketing ready |
| Rider-App | 5 | ❌ | ❌ | ❌ | ❌ | 🔴 NOT READY |
| Subscriptions-UI | — | — | — | — | — | ⬜ Not MVP (skip) |
| Notifications-UI | — | — | — | — | — | ⬜ Not MVP (skip) |

---

## 30-Day Sprint Plan

### Week 1 (Feb 15-21): Rider-App Foundation + Docs

#### Task 1.1: Rider-App Dependencies + Auth (Day 1-2)

**Install dependencies** in `logistics-service/rider-app/`:
- `zustand`, `@tanstack/react-query`, `axios`, `zod`, `react-hook-form`, `@hookform/resolvers`
- shadcn/ui primitives: copy from `auth-service/auth-ui/src/components/ui/` (button, card, badge, input, label, dialog)
- `sonner` (toast), `lucide-react` (icons), `next-themes`

**Create auth integration** (follow auth-ui Zustand pattern):

| File to Create | Pattern Source |
|:---|:---|
| `rider-app/src/store/auth-store.ts` | `auth-ui/src/store/auth-store.ts` |
| `rider-app/src/hooks/useAuth.ts` | `auth-ui/src/hooks/useAuth.ts` |
| `rider-app/src/components/auth/ProtectedRoute.tsx` | `auth-ui/src/components/auth/ProtectedRoute.tsx` |
| `rider-app/src/lib/api-client.ts` | `auth-ui/src/lib/api-client.ts` (adapt for logistics API) |
| `rider-app/src/app/login/page.tsx` | New — email/password form for riders |

**Wire auth into app:**
- Update `rider-app/src/app/layout.tsx` — add QueryClientProvider, ThemeProvider
- Update `rider-app/src/app/[orgSlug]/layout.tsx` — wrap with ProtectedRoute (role: rider)

#### Task 1.2: Rider-App Core Pages (Day 3-4)

| Page | File | API Endpoint | Description |
|:---|:---|:---|:---|
| Deliveries Queue | `[orgSlug]/deliveries/page.tsx` | `GET /api/v1/{tenant}/tasks?status=pending` | List pending tasks, accept/reject |
| Active Delivery | `[orgSlug]/active/page.tsx` | `GET /api/v1/{tenant}/tasks/{id}` | Current task details, status update buttons |
| Earnings | `[orgSlug]/earnings/page.tsx` | `GET /api/v1/{tenant}/fleet-members/{id}/earnings` | Daily/weekly summary |
| Settings | `[orgSlug]/settings/page.tsx` | `GET /api/v1/{tenant}/fleet-members/{id}` | Profile, vehicle, shift toggle |

**TanStack Query hooks to create** in `rider-app/src/hooks/`:
- `useDeliveries.ts`, `useActiveDelivery.ts`, `useEarnings.ts`, `useRiderProfile.ts`, `useTaskMutations.ts`

**Shared components** in `rider-app/src/components/delivery/`:
- `delivery-card.tsx` — task card with accept/reject (large touch targets, 48x48px min)
- `active-delivery.tsx` — status progression, "Open in Maps" button
- `status-badge.tsx` — color-coded delivery status

#### Task 1.3: Rider-App PWA + K8s (Day 5-6)

**PWA files:**
- `rider-app/public/manifest.json` — standalone, portrait, orange theme (per existing `PWA-REQUIREMENTS.md`)
- `rider-app/public/sw.js` — cache-first for static assets, network-first for task data
- `rider-app/src/components/pwa/pwa-install-prompt.tsx` — adapt from auth-ui
- Update `rider-app/next.config.ts` — add PWA config, ensure `output: "standalone"`

**K8s deployment (create new directory):**
- `devops-k8s/apps/rider-app/app.yaml` — ArgoCD Application (pattern: `devops-k8s/apps/ordering-frontend/app.yaml`)
- `devops-k8s/apps/rider-app/values.yaml` — Helm values:
  - Image: `docker.io/codevertex/rider-app`
  - Ingress: `riderapp.codevertexitsolutions.com`
  - Env: `NEXT_PUBLIC_LOGISTICS_API_URL`, `NEXT_PUBLIC_SSO_URL`, `NEXT_PUBLIC_TENANT_SLUG`
  - Health: `/` endpoint, 10s interval
  - Resources: 100m/256Mi → 500m/768Mi

#### Task 1.4: Documentation Sprint — Architecture Docs (Day 7)

**Update 4 existing docs:**

1. **`docs/microservice-architecture.md`** — Add sections:
   - "Transactional Outbox Pattern" under Communication Patterns (auth-service + subscription-service)
   - "Subscription Service Lifecycle" — state machine diagram, JWT enrichment
   - "Notification Worker Architecture" — retry pattern, provider abstraction

2. **`docs/ARCHITECTURE-RECOMMENDATIONS.md`** — Add sections:
   - "Event Publishing Standards" — outbox pattern, NATS subject naming (`{aggregate}.{event}`)
   - "Multi-Service Subscription Model" — products, bundles, plans, feature gating

3. **`docs/CROSS-SERVICE-DATA-OWNERSHIP.md`** — Add:
   - "Event Subscription Matrix" table mapping publishers → events → subscribers:
     - auth → user.created → subscription, notifications, ordering
     - auth → tenant.created → subscription (trial provisioning)
     - subscription → subscription.upgraded → auth (JWT refresh), notifications
     - ordering → order.created → logistics, notifications, treasury
     - logistics → task.completed → ordering, notifications

4. **`docs/TRINITY-AUTHORIZATION-PATTERN.md`** — Add:
   - "Product-Level Entitlements" — layer between RBAC and Feature Licensing
   - Products (ordering, logistics, treasury, pos...) with bundle-based activation

**Create 4 new docs:**

5. **`logistics-service/rider-app/docs/plan.md`** — Full implementation plan (currently 0 bytes)
6. **`logistics-service/rider-app/docs/sprints/sprint-1-mvp.md`** — Auth, pages, PWA, K8s
7. **`subscriptions-service/subscriptions-api/docs/sprints/sprint-1-foundation.md`** — Schemas, products, seed
8. **`subscriptions-service/subscriptions-api/docs/sprints/sprint-2-lifecycle.md`** — State machine, endpoints, NATS

**Create 2 more docs:**

9. **`notifications-service/notifications-api/docs/sprints/sprint-1-foundation.md`** — SendGrid, Twilio, retry
10. **`docs/mvp-countdown-tracker.md`** — Master sprint tracking with weekly checkpoints

---

### Week 2 (Feb 22-28): Rider-App Polish + Ordering-Frontend Completion

#### Task 2.1: Rider-App Live API Integration (Day 8-9)

- Wire all pages to real logistics-api endpoints (replace any static data)
- GPS location tracking hook: `rider-app/src/hooks/useLocationTracking.ts`
  - `navigator.geolocation.watchPosition` → `POST /api/v1/{tenant}/fleet-members/{id}/location`
- Offline queue for status updates when network unavailable
- Build verification: `pnpm run build` must pass

#### Task 2.2: Ordering-Frontend Remaining Features (Day 10-11)

1. **Outlet list API** — replace hardcoded list in `site-header.tsx` with `GET /api/v1/{tenant}/outlets`
2. **Brand config API** — create `src/hooks/use-brand.ts`, fetch tenant look-and-feel settings
3. **Create sprint doc**: `ordering-frontend/docs/sprints/sprint-5-production-readiness.md`

#### Task 2.3: Backend Sprint Docs + Test Scaffolding (Day 12-13)

- Create `subscriptions-api/docs/sprints/` directory + sprint-1 and sprint-2 docs
- Create `notifications-api/docs/sprints/` directory + sprint-1 doc
- Ordering-frontend test scaffolding (vitest config exists, create 3 critical tests):
  - `src/__tests__/store/auth.test.ts`
  - `src/__tests__/hooks/use-menu.test.ts`
  - `src/__tests__/components/cart-drawer.test.tsx`

#### Task 2.4: Full Build Verification (Day 14)

```
All frontends: pnpm run build (0 errors)
  - logistics-service/rider-app
  - ordering-service/ordering-frontend
  - auth-service/auth-ui
  - Cafe/cafe-website

All backends: go build ./... (0 errors)
  - auth-service/auth-api
  - ordering-service/ordering-backend
  - logistics-service/logistics-api
  - subscriptions-service/subscriptions-api
  - notifications-service/notifications-api
  - finance-service/treasury-api
```

---

### Week 3 (Mar 1-7): Integration Testing + Polish

#### Task 3.1: Cross-Service E2E Testing (Day 15-17)

**Flow 1 — Customer Order:**
Login (auth-ui) → Browse menu (ordering-frontend) → Cart → Checkout → Payment → Order created → NATS event → Logistics task → Notification sent

**Flow 2 — Rider Delivery:**
Login (rider-app) → View queue → Accept task → Pick up → In transit → Delivered → Ordering status updates

**Flow 3 — Payment:**
Checkout → Treasury payment intent → M-Pesa STK (sandbox) or COD → Payment confirmed → Order confirmed

#### Task 3.2: Cafe Website Content + Polish (Day 18-19)

- Replace dummy data with real Urban Loft Cafe content
- Verify all 20 pages render correctly on mobile/desktop
- Staff portal pages wired to ordering-backend APIs
- PWA status: document limitation if workbox incompatible with Next.js 16

#### Task 3.3: M-Pesa + Documentation Wrap-up (Day 20-21)

- If till number obtained → configure live M-Pesa in treasury-api
- If blocked → document COD-only MVP, M-Pesa as fast-follow
- Update `docs/roadmap.md` with March progress
- Create `docs/project-status-report-2026-03-07.md`

---

### Week 4 (Mar 8-17): UAT + Production Launch

#### Task 4.1: K8s Deployment + UAT (Day 22-24)

- Deploy all services to K8s cluster
- Client (Antony) UAT with test credentials:
  - Auth: `accounts.codevertexitsolutions.com`
  - Ordering: `ordersapp.codevertexitsolutions.com/urban-loft/menu`
  - Rider: `riderapp.codevertexitsolutions.com/urban-loft`
  - Cafe: `theurbanloftcafe.com`
- Collect and triage feedback

#### Task 4.2: Bug Fixes + Hardening (Day 25-27)

- Fix UAT feedback
- Security: CORS origins, auth on all endpoints
- Performance: health checks, resource limits, connection pooling

#### Task 4.3: Go/No-Go + Launch (Day 28-30)

- Mar 14: Final build + test pass + client sign-off
- Mar 15: Tag `v1.0.0-mvp`, push images, ArgoCD sync
- Mar 16: Smoke test production
- Mar 17: **MVP Launch**

---

## MVP Scope Boundaries

### IN Scope
- Rider-app: Auth, delivery queue, accept/complete, earnings, PWA
- Ordering-frontend: Menu, cart, checkout, tracking, profile (all working)
- Cafe-website: All public pages, staff order management
- Auth-UI: All features (login, signup, 2FA, sessions, API keys)
- All K8s deployments
- COD payment (M-Pesa if till available)

### OUT of Scope (Post-MVP)
- Subscriptions-UI (admin CLI scripts suffice)
- Notifications-UI (admin CLI scripts suffice)
- Rider GPS background tracking (nice-to-have)
- Push notifications (depends on VAPID setup)
- Superset analytics embed
- Group ordering
- Full test coverage (critical path only)

---

## Verification Checklist

### Week 1 (Feb 21)
- [ ] Rider-app has auth (Zustand + ProtectedRoute)
- [ ] Rider-app has login + 4 core pages
- [ ] Rider-app has PWA manifest + service worker
- [ ] `devops-k8s/apps/rider-app/` has app.yaml + values.yaml
- [ ] 4 architecture docs updated
- [ ] Rider-app plan.md populated
- [ ] `pnpm run build` passes for rider-app

### Week 2 (Feb 28)
- [ ] Rider-app has live logistics-api integration
- [ ] Ordering-frontend has outlet list + brand config
- [ ] 3+ test files in ordering-frontend
- [ ] Subscription + notification sprint docs created
- [ ] ALL frontends build clean
- [ ] ALL backends build clean
- [ ] MVP countdown tracker doc exists

### Week 3 (Mar 7)
- [ ] E2E customer order flow verified
- [ ] E2E rider delivery flow verified
- [ ] Cafe website content finalized
- [ ] M-Pesa status determined
- [ ] All services deployed to K8s

### Week 4 (Mar 14)
- [ ] Client UAT completed
- [ ] UAT bugs fixed
- [ ] Go/No-Go decision made
- [ ] All repos tagged for release

---

## Risk Register

| Risk | Impact | Mitigation |
|:---|:---|:---|
| M-Pesa till not received | Payment blocked | COD only for MVP; M-Pesa as fast-follow |
| PWA workbox + Next.js 16 | Cafe PWA broken | Rider-app uses standalone setup; cafe documents limitation |
| Single dev bandwidth | Cannot complete all | Prioritize rider-app auth + pages over polish; skip subscriptions-ui/notifications-ui |
| Rider-app scope creep (GPS/push) | Delayed | GPS/push are post-MVP; delivery list/accept/complete is the MVP bar |
