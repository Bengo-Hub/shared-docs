# devops-k8s: Ingress CORS configuration for SSO-integrated services

**Purpose:** Ensure all services that integrate with SSO have correct CORS at the ingress layer in **devops-k8s** so browser requests from frontend origins are allowed. Apply these in `apps/<app-name>/values.yaml` (or equivalent Ingress/Helm templates) in the **Bengo-Hub/devops-k8s** repo.

**Reference values:** This repo includes `devops-k8s/apps/<app_name>/values.yaml` with ingress CORS annotations; copy or merge into your actual devops-k8s repo.

**Note:** Backend services (auth-api, ordering-backend, etc.) already send CORS headers from application code. Ingress-level CORS can **supplement** or **ensure** headers are present when the app is behind a proxy. Prefer keeping app-level CORS as source of truth; use these annotations to align ingress with the same policy or to add CORS when the app does not.

---

## 1. Allowed origins (canonical list)

Use this list for both **backend env** (`HTTP_ALLOWED_ORIGINS` / app CORS) and **ingress annotations** where applicable:

**Canonical list (matches devops-k8s/apps/*/values.yaml ingress hosts only; no alternate domains):**

| Origin | Service type |
|--------|----------------|
| `https://ordersapp.codevertexitsolutions.com` | Ordering frontend |
| `https://theurbanloftcafe.com` | Cafe website |
| `https://accounts.codevertexitsolutions.com` | Auth UI |
| `https://sso.codevertexitsolutions.com` | Auth API (SSO) |
| `https://notifications.codevertexitsolutions.com` | Notifications UI |
| `https://riderapp.codevertexitsolutions.com` | Rider app |
| `https://pricing.codevertexitsolutions.com` | Subscriptions UI |
| `https://books.codevertexitsolutions.com` | Treasury UI |
| `https://pos.codevertexitsolutions.com` | POS UI |
| `https://logistics.codevertexitsolutions.com` | Logistics UI |
| `https://inventory.codevertexitsolutions.com` | Inventory UI |
| `https://ticketing.codevertexitsolutions.com` | Ticketing UI |
| `https://projects.codevertexitsolutions.com` | Projects UI |
| `http://localhost:3000` | Local dev (cafe, auth-ui, etc.) |
| `http://localhost:3001` | Local dev (ordering-frontend) |
| `http://localhost:3002` | Local dev (rider-app) |
| `http://127.0.0.1:3000` | Local dev |
| `http://127.0.0.1:3001` | Local dev |

For **dynamic** allow (any `https://*.codevertexitsolutions.com`), use the regex or multi-origin form shown below.

---

## 2. NGINX Ingress CORS annotations

If your Ingress uses **NGINX Ingress Controller**, add these annotations to the **backend API** Ingress resources (so that browser requests from the frontend origins above are allowed). Frontend apps (Next.js) are same-origin to their own host and do not need ingress CORS for their own domain; they need the **backend** ingress to allow the frontend origin.

### 2.1 auth-api (SSO)

**Host:** `sso.codevertexitsolutions.com`  
**Path in devops-k8s:** `apps/auth-api/` (or equivalent)

```yaml
metadata:
  annotations:
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://ordersapp.codevertexitsolutions.com, https://theurbanloftcafe.com, https://accounts.codevertexitsolutions.com, https://sso.codevertexitsolutions.com, https://notifications.codevertexitsolutions.com, https://riderapp.codevertexitsolutions.com, https://pricing.codevertexitsolutions.com, https://books.codevertexitsolutions.com, https://pos.codevertexitsolutions.com, https://logistics.codevertexitsolutions.com, https://inventory.codevertexitsolutions.com, https://ticketing.codevertexitsolutions.com, https://projects.codevertexitsolutions.com, http://localhost:3000, http://localhost:3001, http://localhost:3002, http://127.0.0.1:3000, http://127.0.0.1:3001"
    nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    nginx.ingress.kubernetes.io/cors-allow-headers: "Accept, Authorization, Content-Type, X-Request-ID, X-Requested-With, X-API-Key, X-Tenant-Slug, X-Tenant-ID"
    nginx.ingress.kubernetes.io/cors-allow-credentials: "true"
    nginx.ingress.kubernetes.io/cors-max-age: "300"
```

**Important:** auth-api must allow `X-Tenant-ID` so frontends that send the tenant UUID from GET `/api/v1/auth/me` (e.g. cafe-website, notifications-ui) do not hit CORS preflight failures. Application CORS in `auth-api/internal/httpapi/router.go` and ingress must both include `X-Tenant-ID`.

### 2.2 ordering-backend

**Host:** `orderingapi.codevertexitsolutions.com` (or `orderingapi.codevertexitsolutions.com`)  
**Path in devops-k8s:** `apps/ordering-backend/` (or `apps/ordering-backend/values.yaml` under ingress)

```yaml
metadata:
  annotations:
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://ordersapp.codevertexitsolutions.com, https://theurbanloftcafe.com, https://pos.codevertexitsolutions.com, https://accounts.codevertexitsolutions.com, https://sso.codevertexitsolutions.com, https://notifications.codevertexitsolutions.com, https://pricing.codevertexitsolutions.com, https://books.codevertexitsolutions.com, https://logistics.codevertexitsolutions.com, http://localhost:3001, http://127.0.0.1:3001"
    nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    nginx.ingress.kubernetes.io/cors-allow-headers: "Accept, Authorization, Content-Type, X-Request-ID, X-Tenant-ID, X-Tenant-Slug, X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset"
    nginx.ingress.kubernetes.io/cors-allow-credentials: "true"
    nginx.ingress.kubernetes.io/cors-max-age: "300"
```

### 2.3 notifications-api

**Host:** `notificationsapi.codevertexitsolutions.com`  
**Path in devops-k8s:** `apps/notifications-api/`

```yaml
metadata:
  annotations:
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://notifications.codevertexitsolutions.com, https://ordersapp.codevertexitsolutions.com, https://accounts.codevertexitsolutions.com, https://sso.codevertexitsolutions.com, https://pricing.codevertexitsolutions.com, https://books.codevertexitsolutions.com, http://localhost:3000, http://localhost:3001"
    nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    nginx.ingress.kubernetes.io/cors-allow-headers: "Accept, Authorization, Content-Type, X-Tenant-Slug, X-Tenant-ID"
    nginx.ingress.kubernetes.io/cors-allow-credentials: "true"
    nginx.ingress.kubernetes.io/cors-max-age: "300"
```

### 2.4 logistics-api

**Host:** `logisticsapi.codevertexitsolutions.com`  
**Path in devops-k8s:** `apps/logistics-api/`

```yaml
metadata:
  annotations:
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://logistics.codevertexitsolutions.com, https://riderapp.codevertexitsolutions.com, https://ordersapp.codevertexitsolutions.com, https://accounts.codevertexitsolutions.com, https://sso.codevertexitsolutions.com, http://localhost:3002, http://localhost:3001"
    nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    nginx.ingress.kubernetes.io/cors-allow-headers: "Accept, Authorization, Content-Type, X-Tenant-Slug, X-Tenant-ID"
    nginx.ingress.kubernetes.io/cors-allow-credentials: "true"
    nginx.ingress.kubernetes.io/cors-max-age: "300"
```

### 2.5 treasury-api

**Host:** `booksapi.codevertexitsolutions.com` (Treasury UI is at `books.codevertexitsolutions.com`)  
**Path in devops-k8s:** `apps/treasury-api/`

```yaml
metadata:
  annotations:
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://books.codevertexitsolutions.com, https://ordersapp.codevertexitsolutions.com, https://theurbanloftcafe.com, https://pos.codevertexitsolutions.com, https://accounts.codevertexitsolutions.com, https://sso.codevertexitsolutions.com, http://localhost:3011, http://localhost:3001, http://localhost:4201"
    nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    nginx.ingress.kubernetes.io/cors-allow-headers: "Accept, Authorization, Content-Type, X-Tenant-Slug, X-Tenant-ID"
    nginx.ingress.kubernetes.io/cors-allow-credentials: "true"
    nginx.ingress.kubernetes.io/cors-max-age: "300"
```

### 2.6 inventory-api

**Host:** `inventoryapi.codevertexitsolutions.com`  
**Path in devops-k8s:** `apps/inventory-api/`

```yaml
metadata:
  annotations:
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://ordersapp.codevertexitsolutions.com, https://theurbanloftcafe.com, https://pos.codevertexitsolutions.com, https://inventory.codevertexitsolutions.com, http://localhost:3001"
    nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    nginx.ingress.kubernetes.io/cors-allow-headers: "Accept, Authorization, Content-Type, X-Tenant-Slug, X-Tenant-ID"
    nginx.ingress.kubernetes.io/cors-allow-credentials: "true"
    nginx.ingress.kubernetes.io/cors-max-age: "300"
```

### 2.7 pos-api

**Host:** `posapi.codevertexitsolutions.com`  
**Path in devops-k8s:** `apps/pos-api/`

```yaml
metadata:
  annotations:
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://pos.codevertexitsolutions.com, https://ordersapp.codevertexitsolutions.com, https://theurbanloftcafe.com, http://localhost:3001"
    nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    nginx.ingress.kubernetes.io/cors-allow-headers: "Accept, Authorization, Content-Type, X-Tenant-Slug, X-Tenant-ID"
    nginx.ingress.kubernetes.io/cors-allow-credentials: "true"
    nginx.ingress.kubernetes.io/cors-max-age: "300"
```

### 2.8 subscriptions-api

**Host:** `pricingapi.codevertexitsolutions.com`  
**Path in devops-k8s:** `apps/subscriptions-api/`

```yaml
metadata:
  annotations:
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://pricing.codevertexitsolutions.com, https://ordersapp.codevertexitsolutions.com, https://accounts.codevertexitsolutions.com, https://sso.codevertexitsolutions.com, https://books.codevertexitsolutions.com, http://localhost:3010, http://localhost:3001"
    nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    nginx.ingress.kubernetes.io/cors-allow-headers: "Accept, Authorization, Content-Type, X-Tenant-Slug, X-Tenant-ID"
    nginx.ingress.kubernetes.io/cors-allow-credentials: "true"
    nginx.ingress.kubernetes.io/cors-max-age: "300"
```

---

## 3. values.yaml: Backend env (HTTP_ALLOWED_ORIGINS)

For backends that read CORS from env (e.g. ordering-backend `HTTP_ALLOWED_ORIGINS`), set in **values.yaml** under the app's env or `extraEnv`:

| App | Env var | Example value |
|-----|---------|----------------|
| ordering-backend | `HTTP_ALLOWED_ORIGINS` | `https://ordersapp.codevertexitsolutions.com,https://theurbanloftcafe.com,https://pos.codevertexitsolutions.com,https://notifications.codevertexitsolutions.com,https://pricing.codevertexitsolutions.com,https://books.codevertexitsolutions.com,https://logistics.codevertexitsolutions.com,https://accounts.codevertexitsolutions.com,https://sso.codevertexitsolutions.com,http://localhost:3001,http://127.0.0.1:3001` |
| auth-api | (CORS via ingress only) | See ?2.1; origins = configured frontend hosts from values.yaml |
| notifications-api | (if supported) | Same pattern: frontend origins only |
| logistics-api | (if supported) | Same pattern |
| treasury-api | (if supported) | Same pattern |
| inventory-api | (if supported) | Same pattern |
| pos-api | (if supported) | Same pattern |
| subscriptions-api | (if supported) | Same pattern |

---

## 4. Frontend apps (no ingress CORS needed for same-origin)

Frontend apps (ordering-frontend, cafe-website, notifications-ui, auth-ui, rider-app, logistics-ui, treasury-ui at books, pos-ui, subscriptions-ui at pricing, inventory-ui, ticketing-ui, projects-ui) are **origins** that call backends. Their Ingress resources do **not** need CORS annotations for their own domain; CORS is required on the **backend** ingress (and app) so that these origins are allowed when the browser sends requests to the API.

Ensure each frontend's **build** receives the correct production API/SSO URLs (see `shared-docs/mvp-critical-path.md` ?9.2).

---

## 5. Checklist (devops-k8s repo)

- [ ] **auth-api** ingress: CORS annotations per ?2.1
- [ ] **ordering-backend** ingress: CORS annotations per ?2.2; `HTTP_ALLOWED_ORIGINS` in values.yaml per ?3
- [ ] **notifications-api** ingress: CORS annotations per ?2.3
- [ ] **logistics-api** ingress: CORS annotations per ?2.4
- [ ] **treasury-api** ingress: CORS annotations per ?2.5
- [ ] **inventory-api** ingress: CORS annotations per ?2.6
- [ ] **pos-api** ingress: CORS annotations per ?2.7
- [ ] **subscriptions-api** ingress: CORS annotations per ?2.8
- [ ] All backend values.yaml: env for CORS/allowed-origins where the app supports it

---

## 6. Reference

- NGINX Ingress CORS: https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/#enable-cors
- Application-level CORS: `mvp-critical-path.md` ?9 (CORS and production domains)
