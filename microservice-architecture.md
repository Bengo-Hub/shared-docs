# BengoBox Microservices Architecture

**Date**: December 2025  
**Version**: 1.0  
**Purpose**: Define a hybrid microservices architecture with seamless service-to-service communication, scalability, performance, and security for all BengoBox services.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [Production Infrastructure (devops-k8s)](#production-infrastructure-devops-k8s)
4. [Communication Patterns](#communication-patterns)
5. [Service Discovery](#service-discovery)
6. [Service-to-Service Technology Stack](#service-to-service-technology-stack)
7. [Data Sharing & Ownership](#data-sharing--ownership)
8. [Security & Authentication](#security--authentication)
9. [Reliability & Resilience](#reliability--resilience)
10. [Observability](#observability)
11. [Shared Libraries & Abstractions](#shared-libraries--abstractions)
12. [Architecture Diagram](#architecture-diagram)
13. [Implementation Status](#implementation-status)
14. [Migration Roadmap](#migration-roadmap)

---

## Overview

BengoBox uses a **hybrid microservices architecture** that combines multiple communication patterns to optimize for different use cases:

- **Event-Driven Architecture (EDA)** via NATS JetStream for asynchronous, decoupled communication
- **REST APIs** for synchronous, request-response operations
- **gRPC/ConnectRPC** for high-throughput internal service communication
- **Webhooks** for callback-based integrations (external and internal)
- **WebSockets** for real-time bidirectional communication
- **GraphQL** for flexible frontend data fetching (future)

This architecture ensures:
- ✅ Zero logic/entity duplication across services
- ✅ Scalable, high-performance communication
- ✅ Secure service-to-service interactions
- ✅ Parallel processing where applicable
- ✅ Fault tolerance and resilience
- ✅ Real-time capabilities where needed

---

## Architecture Principles

### 1. **Single Source of Truth**
Each service owns its domain data. Other services reference via IDs only.

### 2. **Reference Only, No Duplication**
Services store reference IDs (UUIDs), never duplicate entity data.

### 3. **Event-Driven First**
Prefer asynchronous events (NATS) for non-blocking operations.

### 4. **Synchronous When Necessary**
Use REST/gRPC for operations requiring immediate feedback.

### 5. **Fail Fast, Recover Gracefully**
Circuit breakers, retries, and graceful degradation.

### 6. **Secure by Default**
All service-to-service communication authenticated and authorized.

### 7. **Observable Everywhere**
Distributed tracing, metrics, and structured logging.

---

## Production Infrastructure (devops-k8s)

**Status**: ✅ **FULLY OPERATIONAL**

BengoBox uses a **centralized DevOps repository** (`devops-k8s`) that provides shared infrastructure, deployment pipelines, and standardized configurations for all microservices.

### Infrastructure Services

#### 1. **Message Brokers** (Namespace: `messaging`)

**NATS JetStream** (Primary - All Go services):
- Service: `nats.messaging.svc.cluster.local:4222`
- **Env var (standard):** `EVENTS_NATS_URL` — all Go backends use this single key for the NATS connection URL.
- Clustering: 2 replicas with JetStream enabled
- Storage: 10Gi PVC for persistence
- Usage: Primary async communication for Go services
- Streams: `{service}.{domain}` (e.g., `subscription.billing`, `logistics.tasks`)

**RabbitMQ** (Legacy - Python/Django services):
- Service: `rabbitmq.messaging.svc.cluster.local:5672`
- Usage: Celery broker for ERP service (Django)
- Virtual hosts: Per-service isolation

**Why NATS for Go, RabbitMQ for Python?**
- **NATS**: Native Go client, lightweight, perfect for Go services
- **RabbitMQ**: Celery (Python) has mature RabbitMQ support, Django ecosystem standard

#### 2. **Caching & Session Storage** (Namespace: `infra`)

**Redis**:
- Service: `redis-master.infra.svc.cluster.local:6379`
- Usage: 
  - Session storage (JWT refresh tokens)
  - Query result caching (5-60 min TTL)
  - Rate limiting counters
  - Idempotency keys
  - Real-time pub/sub (for WebSockets)
- Storage: 8Gi with persistence
- Priority: `db-critical` (high priority)

#### 3. **Databases** (Per-Service)

**PostgreSQL**:
- Each service has dedicated PostgreSQL database
- Connection strings stored in Kubernetes secrets
- Example: `{service-name}-secrets` → `postgresUrl` key

**Services with Databases**:
- `auth-service` → PostgreSQL in `auth` namespace
- `treasury-service` → PostgreSQL in `treasury` namespace
- `subscription-service` → PostgreSQL (database: `pricing`)
- `logistics-service` → PostgreSQL (PostGIS for geo-queries)
- `ordering-service` → PostgreSQL
- `notifications-service` → PostgreSQL
- `inventory-service` → PostgreSQL
- `pos-service` → PostgreSQL
- `erp-service` → PostgreSQL (Django)

#### 4. **Object Storage** (Namespace: `storage`)

**MinIO** (S3-compatible):
- Service: `minio.storage.svc.cluster.local:9000`
- Usage: Treasury service for settlement artifacts, receipts
- Bucket: `treasury-artifacts`

#### 5. **Observability** (Namespace: `infra`)

**OpenTelemetry Collector**:
- Service: `otel-collector.infra.svc.cluster.local:4317`
- Usage: Centralized trace/metric collection
- Export: All services export traces/metrics to collector

**Prometheus**:
- Scrapes metrics from all services via ServiceMonitors
- ServiceMonitors configured per service
- Namespace: `infra`

**Grafana**:
- Dashboard visualization for metrics
- External URL: `grafana.masterspace.co.ke`

### API Gateway & Ingress

**NGINX Ingress Controller**:
- Entry point for all external traffic
- TLS termination via cert-manager (Let's Encrypt)
- Domain-based routing to services
- Load balancing across service replicas

**TLS Certificates**:
- Managed by cert-manager
- ClusterIssuer: `letsencrypt-prod`
- Automatic renewal
- Per-service TLS secrets

**External Domains**:
- Auth API: `sso.codevertexitsolutions.com`
- Auth UI: `accounts.codevertexitsolutions.com`
- Treasury API: `booksapi.codevertexitsolutions.com`
- Treasury UI: `books.codevertexitsolutions.com`
- Notifications: `notifications.codevertexitsolutions.com`
- Ordering API: `orderingapi.codevertexitsolutions.com`
- Ordering UI: `ordersapp.codevertexitsolutions.com`
- Cafe Website: `theurbanloftcafe.com`
- POS API: `posapi.codevertexitsolutions.com`
- POS UI: `pos.codevertexitsolutions.com`
- Subscription API: `pricingapi.codevertexitsolutions.com`
- Projects API: `projectsapi.codevertexitsolutions.com`
- Projects UI: `projects.codevertexitsolutions.com`
- IoT: `iot.codevertexitsolutions.com`
- ISP Billing API: `ispbillingapi.codevertexitsolutions.com`
- ISP Billing UI: `ispbilling.codevertexitsolutions.com`
- Ticketing API: `ticketingapi.codevertexitsolutions.com`
- Ticketing UI: `ticketing.codevertexitsolutions.com`
- ERP: `erpapi.masterspace.co.ke` (legacy)

### GitOps & Deployment

**ArgoCD**:
- GitOps deployment orchestrator
- Monitors `devops-k8s` repository
- Root application syncs all child applications
- External URL: `argocd.masterspace.co.ke`

**Helm Charts**:
- Generic reusable chart in `charts/app/`
- Standardized deployment templates
- Service-specific values in `apps/{service}/values.yaml`

**GitHub Actions**:
- CI/CD pipelines for each service
- Reusable workflows from `devops-k8s`
- Automated builds and deployments

### Autoscaling & Resource Management

**Horizontal Pod Autoscaler (HPA)**:
- All services configured with HPA
- CPU/Memory-based scaling
- Min/Max replicas per service

**Vertical Pod Autoscaler (VPA)**:
- Enabled for critical services (ERP, Treasury)
- Automatic resource recommendations
- Update mode: `Recreate`

**KEDA** (Future):
- Queue-driven autoscaling
- NATS/RabbitMQ queue depth scaling

### Deployment Pattern

**Standard Service Structure**:
```
apps/
  {service-name}/
    app.yaml          # ArgoCD Application manifest
    values.yaml       # Helm values
    README.md         # Service-specific docs
```

**Reusable Helm Chart** (`charts/app/`):
- Generic deployment templates
- Supports: HTTP services, Celery workers, migrations, seeding
- Standardized health checks, monitoring, ingress

---

## Communication Patterns

### Pattern Selection Matrix

| Use Case | Pattern | Technology | When to Use |
|----------|---------|------------|-------------|
| **Async notifications** | Event-Driven | NATS JetStream | User/tenant sync, status updates, audit logs |
| **Real-time queries** | REST API | HTTP/REST | Data retrieval, immediate operations |
| **High-throughput internal** | gRPC | ConnectRPC | Bulk operations, streaming, service-to-service |
| **External callbacks** | Webhooks | HTTP POST | Payment providers, third-party integrations |
| **Internal callbacks** | Webhooks | HTTP POST | Service-to-service callbacks (payment confirmations) |
| **Live updates** | WebSockets | WS/WSS | Real-time tracking, live notifications |
| **Complex queries** | GraphQL | GraphQL | Frontend data fetching (future) |

---

## 1. Event-Driven Architecture (NATS JetStream)

**Status**: ✅ **IMPLEMENTED** (Primary async communication)

**Technology**: NATS JetStream

**Use For**:
- User/tenant synchronization
- Status updates
- Notifications
- Audit logging
- Non-blocking operations
- Event sourcing

### Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Service   │────────▶│ NATS         │────────▶│   Service   │
│     A       │ Publish │ JetStream    │ Consume │     B       │
└─────────────┘         └──────────────┘         └─────────────┘
                             │
                             ▼
                    ┌──────────────┐
                    │  Outbox      │
                    │  Pattern     │
                    └──────────────┘
```

### Implementation

**Stream Naming**: `{service_name}.{domain}` (e.g., `subscription.billing`, `logistics.tasks`)

**Subject Naming**: `{service_name}.{entity}.{action}` (e.g., `auth.user.created`, `treasury.payment.success`)

**Outbox Pattern** (Recommended for reliability):
1. Store event in database (same transaction as domain operation)
2. Background worker publishes from outbox table to NATS
3. Ensures guaranteed delivery even if NATS is temporarily unavailable

**Direct Publish** (For non-critical events):
- Direct NATS publish without persistence
- Suitable for non-critical status updates

### Services Using NATS

| Service | Stream Name | Subjects | Outbox Pattern |
|---------|-------------|----------|----------------|
| **auth-service** | `auth.events` | `auth.user.*`, `auth.tenant.*` | ⚠️ Partial |
| **subscription-service** | `subscription` | `subscription.*` | ✅ Implemented |
| **notifications-service** | `notifications` | `notifications.*` | ✅ Implemented |
| **logistics-service** | `logistics` | `logistics.*` | ✅ Implemented |
| **ordering-service** | `ordering` | `ordering.*` | ❌ Direct publish |
| **treasury-service** | `treasury` | `treasury.*` | ⚠️ Partial |
| **projects-service** | `projects` | `projects.*` | ✅ Implemented |
| **iot-service** | `iot` | `iot.*` | ✅ Implemented |

### Gaps

- ⚠️ Outbox pattern partially implemented (subscription, notifications, logistics, projects, IoT ✅; ordering, treasury, auth ⚠️)
- ❌ No event schema registry
- ❌ No event versioning strategy
- ⚠️ Dead-letter queue handling (implemented in shared-events library, needs configuration per service)

### Recommendations

1. **Standardize Outbox Pattern**: All services should implement outbox for critical events
2. **Event Schema Registry**: Use JSON Schema or Protobuf for event contracts
3. **Event Versioning**: Support event versioning (e.g., `auth.user.created.v1`, `auth.user.created.v2`)
4. **Dead Letter Queue**: Configure DLQ for failed event processing

---

## 2. REST API (Synchronous)

**Status**: ✅ **IMPLEMENTED** (Standard HTTP calls)

**Technology**: HTTP/REST with Chi Router (Go) or Gin (Go)

**Use For**:
- Real-time data retrieval
- Immediate operations requiring response
- Query operations
- CRUD operations

### Current Implementation

**Service URLs** (Hardcoded via environment variables):
```go
// Each service configures other service URLs
type Config struct {
    AuthServiceURL      string `envconfig:"AUTH_SERVICE_URL"`
    TreasuryServiceURL  string `envconfig:"TREASURY_SERVICE_URL"`
    NotificationsURL    string `envconfig:"NOTIFICATIONS_SERVICE_URL"`
}
```

**Direct HTTP Calls** (No abstraction):
```go
resp, err := http.Get(fmt.Sprintf("%s/api/v1/users/%s", cfg.AuthServiceURL, userID))
```

### Current Implementation

**Service URLs** (Kubernetes DNS for internal, HTTPS for external):
- Internal: `http://{service}.{namespace}.svc.cluster.local:{port}`
- External: `https://{domain}.codevertexitsolutions.com`

**Shared HTTP Client** (`shared-service-client`):
- ✅ Circuit breaker (gobreaker) - Opens after 5 consecutive failures
- ✅ Retry with exponential backoff - 100ms to 5s, max 30s
- ✅ Distributed tracing (OpenTelemetry)
- ✅ Structured logging (Zap)
- ✅ Configurable timeouts (default 10s)

**Usage**:
```go
client := serviceclient.New(serviceclient.DefaultConfig(
    "http://auth-api.auth.svc.cluster.local:4101",
    "auth-service",
    logger,
))
resp, err := client.Get(ctx, "/api/v1/users/"+userID, nil)
```

### Gaps

- ✅ All services migrated to use shared HTTP client (logistics, subscription completed)
- ✅ Service discovery using Kubernetes DNS (fully operational)

---

## 3. gRPC/ConnectRPC (High-Throughput)

**Status**: ⚠️ **PLANNED** (Not yet implemented)

**Technology**: ConnectRPC (modern gRPC alternative)

**Use For**:
- High-throughput internal service communication
- Bulk operations
- Streaming data
- Service-to-service RPCs

### Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Service   │────────▶│  ConnectRPC  │────────▶│   Service   │
│     A       │  gRPC   │   Gateway    │  gRPC   │     B       │
└─────────────┘         └──────────────┘         └─────────────┘
```

### Implementation Plan

**Implementation Plan**:
- Use Protocol Buffers (`.proto`) for service definitions
- ConnectRPC for gRPC implementation
- Start with subscription-service for feature checks
- Implement in treasury-service for bulk payments

### Services to Implement gRPC

1. **subscription-service** → Feature checks, usage reporting
2. **treasury-service** → Payment processing, bulk operations
3. **notifications-service** → Bulk notifications
4. **logistics-service** → Task assignments, streaming updates

### Timeline

- **Phase 1** (Q1 2026): Implement gRPC in subscription-service
- **Phase 2** (Q2 2026): Implement gRPC in treasury-service
- **Phase 3** (Q3 2026): Implement gRPC in notifications-service and logistics-service

---

## 4. Webhooks (Callbacks)

**Status**: ⚠️ **PARTIALLY IMPLEMENTED**

**Technology**: HTTP POST with HMAC signature verification

**Use For**:
- External service callbacks (payment providers, SendGrid, Twilio)
- Internal service-to-service callbacks (payment confirmations, delivery updates)

### Current Implementation

**External Webhooks** (Implemented):
- ✅ Treasury service: M-Pesa callbacks, Stripe webhooks
- ✅ Notifications service: SendGrid, Twilio delivery callbacks (planned)

**Internal Webhooks** (Partial):
- ✅ Auth-service: Tenant/user discovery webhooks (to be implemented)
- ❌ Other services: No standardized internal webhook infrastructure

**External Webhooks** (Implemented):
- HMAC signature verification for security
- M-Pesa and Stripe callback handlers in treasury-service
- Webhook event processing with retry logic

**Internal Webhooks** (Planned):
- Webhook registration API for service-to-service callbacks
- Event-driven webhook delivery with HMAC signing
- Retry mechanism with exponential backoff for failed deliveries
- Webhook management API (register/unregister/list)

### Gaps

- ❌ No internal webhook registration infrastructure
- ❌ No webhook retry mechanism (for internal)
- ❌ No webhook delivery status tracking
- ❌ No webhook management UI/API

---

## 5. WebSockets (Real-Time)

**Status**: ⚠️ **PLANNED** (Not yet implemented)

**Technology**: WebSocket (WS/WSS) with gorilla/websocket or nhooyr.io/websocket

**Use For**:
- Real-time order tracking
- Live driver/rider location updates
- Live notifications
- Collaborative features

### Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Client    │◀───────▶│  WebSocket   │◀───────▶│   Service   │
│  (Browser)  │   WS    │   Gateway    │   WS    │  (Backend)  │
└─────────────┘         └──────────────┘         └─────────────┘
                             │
                             ▼
                    ┌──────────────┐
                    │  Redis       │
                    │  Pub/Sub     │
                    └──────────────┘
```

### Implementation Plan

**Implementation Plan**:
- WebSocket handler upgrades HTTP connections
- Redis pub/sub for broadcasting updates to connected clients
- Real-time location and status updates for delivery tracking

### Services to Implement WebSockets

1. **logistics-service** → Real-time task tracking, rider location
2. **ordering-service** → Live order status updates
3. **notifications-service** → Live notification delivery (optional)

### Timeline

- **Phase 1** (Q2 2026): Implement WebSockets in logistics-service for task tracking
- **Phase 2** (Q3 2026): Implement WebSockets in ordering-service for order tracking

---

## 6. GraphQL (Flexible Queries)

**Status**: ⚠️ **FUTURE** (Not yet planned)

**Technology**: GraphQL with gqlgen or graphql-go

**Use For**:
- Frontend data fetching
- Complex nested queries
- Mobile app APIs

### Use Cases

- Cafe website: Complex menu queries with filters
- Admin dashboards: Aggregated data from multiple services
- Mobile apps: Flexible data fetching

### Implementation (Future)

**Future Implementation**:
- GraphQL schema for flexible frontend queries
- Resolvers aggregate data from multiple services
- Complex nested queries with filters

---

## Service Discovery

**Status**: ✅ **IMPLEMENTED** (Kubernetes DNS-based)

### Production Implementation

**Kubernetes DNS-Based Discovery** (Currently in use):

All services communicate via Kubernetes DNS service names following the pattern:
```
{service-name}.{namespace}.svc.cluster.local:{port}
```

**Internal Service Communication** (Backend-to-Backend):
- Auth Service: `auth-api.auth.svc.cluster.local:4101`
- Treasury Service: `treasury-api.treasury.svc.cluster.local:4000`
- Notifications Service: `notifications-service.notifications.svc.cluster.local:4000`
- Subscription Service: `subscription-service.subscription.svc.cluster.local:4005`
- Logistics Service: `logistics-api.logistics.svc.cluster.local:4000`
- Ordering Service: `ordering-backend.ordering.svc.cluster.local:4000`
- POS Service: `pos-api.pos.svc.cluster.local:4000`
- Inventory Service: `inventory-api.inventory.svc.cluster.local:4000`

**Infrastructure Services** (Shared resources):
- Redis: `redis-master.infra.svc.cluster.local:6379`
- NATS: `nats.messaging.svc.cluster.local:4222`
- RabbitMQ: `rabbitmq.messaging.svc.cluster.local:5672`
- MinIO: `minio.storage.svc.cluster.local:9000`
- OpenTelemetry: `otel-collector.infra.svc.cluster.local:4317`

**External Service Communication** (Frontend-to-Backend):
- Auth API: `https://sso.codevertexitsolutions.com`
- Auth UI: `https://accounts.codevertexitsolutions.com`
- Treasury API: `https://booksapi.codevertexitsolutions.com`
- Treasury UI: `https://books.codevertexitsolutions.com`
- Notifications Service: `https://notifications.codevertexitsolutions.com`
- Ordering API: `https://orderingapi.codevertexitsolutions.com`
- Ordering UI: `https://ordersapp.codevertexitsolutions.com`
- Cafe Website: `https://theurbanloftcafe.com`
- POS API: `https://posapi.codevertexitsolutions.com`
- POS UI: `https://pos.codevertexitsolutions.com`
- Subscription API: `https://pricingapi.codevertexitsolutions.com`
- Projects API: `https://projectsapi.codevertexitsolutions.com`
- Projects UI: `https://projects.codevertexitsolutions.com`
- IoT Service: `https://iot.codevertexitsolutions.com`
- ISP Billing API: `https://ispbillingapi.codevertexitsolutions.com`
- ISP Billing UI: `https://ispbilling.codevertexitsolutions.com`
- Ticketing API: `https://ticketingapi.codevertexitsolutions.com`
- Ticketing UI: `https://ticketing.codevertexitsolutions.com`

### Namespace Organization

**Infrastructure Namespaces**:
- `infra` - Shared infrastructure (Redis, PostgreSQL, Prometheus, OpenTelemetry)
- `messaging` - Message brokers (NATS JetStream, RabbitMQ)
- `storage` - Object storage (MinIO)

**Service Namespaces**:
- `auth` - Auth service
- `treasury` - Treasury service
- `notifications` - Notifications service
- `subscription` - Subscription service (to be created)
- `logistics` - Logistics service
- `cafe` / `ordering` - Ordering service
- `pos` - POS service
- `inventory` - Inventory service
- `erp` - ERP service (Django)

### Service URLs Configuration

**Backend Services** (Use Kubernetes DNS for internal communication):
```go
// Configuration in service values.yaml
env:
  - name: AUTH_SERVICE_URL
    value: http://auth-api.auth.svc.cluster.local:4101
  - name: TREASURY_SERVICE_URL
    value: http://treasury-api.treasury.svc.cluster.local:4000
```

**Frontend Services** (Use HTTPS URLs for external communication):
```yaml
env:
  - name: NEXT_PUBLIC_API_URL
    value: https://sso.codevertexitsolutions.com
  - name: NEXT_PUBLIC_NOTIFICATIONS_URL
    value: https://notifications.codevertexitsolutions.com
```

### Benefits

- ✅ **Zero Configuration**: Kubernetes DNS automatically resolves service names
- ✅ **Load Balancing**: Kubernetes Service provides built-in load balancing
- ✅ **Health Checks**: Service endpoints automatically exclude unhealthy pods
- ✅ **Multi-Namespace**: Logical separation via namespaces
- ✅ **No Service Registry Required**: Kubernetes DNS is the registry

### Future Enhancements

**Service Registry** (Optional - For advanced scenarios):
- Consul/etcd for cross-cluster service discovery
- Service mesh (Istio/Linkerd) for advanced traffic management

---

## Service-to-Service Technology Stack

### Technology Selection by Service and Use Case

| Service | Primary Protocol | Message Broker | Database | Cache | Why This Stack? |
|---------|-----------------|----------------|----------|-------|-----------------|
| **auth-service** | REST (HTTP) | NATS JetStream | PostgreSQL | Redis | JWT validation requires REST, events for user/tenant sync, Redis for session cache |
| **subscription-service** | REST + gRPC (future) | NATS JetStream | PostgreSQL | Redis | REST for feature checks, gRPC for high-throughput usage reporting, NATS for billing events |
| **notifications-service** | REST + gRPC (future) | NATS JetStream | PostgreSQL | Redis | REST for immediate delivery, gRPC for bulk notifications, NATS for event-driven triggers |
| **treasury-service** | REST + gRPC (future) | NATS JetStream | PostgreSQL | Redis | REST for payment intents, gRPC for bulk settlements, NATS for payment events |
| **logistics-service** | REST + WebSocket | NATS JetStream | PostgreSQL (PostGIS) | Redis | REST for CRUD, WebSocket for real-time tracking, NATS for task events, PostGIS for geo-queries |
| **ordering-service** | REST + WebSocket | NATS JetStream | PostgreSQL | Redis | REST for orders, WebSocket for live updates, NATS for order lifecycle events |
| **inventory-service** | REST | NATS JetStream | PostgreSQL | Redis | REST for stock queries, NATS for stock update events |
| **pos-service** | REST | NATS JetStream | PostgreSQL | Redis | REST for POS operations, NATS for order events |
| **erp-service** (Django) | REST + WebSocket | RabbitMQ (Celery) | PostgreSQL | Redis | REST for API, RabbitMQ for Celery tasks (Django standard), WebSocket for real-time payroll |

### Communication Pattern Decision Tree

**When to Use REST API**:
- ✅ Synchronous operations requiring immediate response
- ✅ CRUD operations
- ✅ Query operations
- ✅ External-facing APIs
- ✅ Frontend-to-backend communication

**When to Use NATS JetStream (Events)**:
- ✅ Asynchronous notifications
- ✅ User/tenant synchronization
- ✅ Status updates
- ✅ Audit logging
- ✅ Event sourcing
- ✅ Non-blocking operations

**When to Use gRPC**:
- ✅ High-throughput internal service calls
- ✅ Bulk operations
- ✅ Streaming data
- ✅ Service-to-service RPCs (future)
- ✅ Micro-batching scenarios

**When to Use WebSockets**:
- ✅ Real-time tracking (delivery, order status)
- ✅ Live notifications
- ✅ Collaborative features
- ✅ Bidirectional communication required

**When to Use Webhooks**:
- ✅ External service callbacks (payment providers)
- ✅ Internal service-to-service callbacks
- ✅ Event delivery to external systems

**When to Use RabbitMQ**:
- ✅ Python/Django services with Celery
- ✅ Long-running background tasks
- ✅ Task queue requirements

### Service Communication Examples

#### Example 1: Order Creation Flow (REST + NATS)

```
Ordering Service → Treasury Service (REST)
  POST /api/v1/payments/intents
  Response: {payment_intent_id, status}

Ordering Service → Logistics Service (NATS)
  Event: cafe.order.created
  Payload: {order_id, delivery_address, items}

Ordering Service → Notifications Service (NATS)
  Event: cafe.order.created
  Payload: {customer_id, order_id, template: "order_confirmation"}
```

**Why This Pattern?**
- REST for payment requires immediate confirmation
- NATS for logistics (non-blocking, eventual consistency OK)
- NATS for notifications (non-blocking, can retry)

#### Example 2: Feature Check (REST + Cache)

```
Any Service → Subscription Service (REST)
  GET /api/v1/{tenant_id}/features/multi_warehouse
  Cache: Redis (60s TTL)
  Response: {enabled: true, limit: 5}
```

**Why REST?**
- Immediate response required (blocking operation)
- Low latency with Redis cache
- Simple request-response pattern

#### Example 3: User Synchronization (NATS Events)

```
Auth Service → All Services (NATS)
  Event: auth.user.created
  Payload: {user_id, email, tenant_id}

Services consume event and create local user references
```

**Why NATS?**
- Multiple subscribers (all services need user data)
- Non-blocking (service can process async)
- Reliable delivery with JetStream

#### Example 4: Real-Time Tracking (WebSocket + Redis Pub/Sub)

```
Frontend → Logistics Service (WebSocket)
  Connection: ws://logistics-service/ws/task/{task_id}

Logistics Service → Redis Pub/Sub
  Publish: task:{task_id}:updates
  Payload: {status: "en_route", location: {...}}

Frontend receives real-time updates via WebSocket
```

**Why WebSocket?**
- Real-time bidirectional communication
- Lower latency than polling
- Efficient for continuous updates

---

## Shared Libraries & Abstractions

### Current Shared Libraries

#### 1. **shared-auth-client** ✅

**Purpose**: JWT validation and authentication for all services

**Repository**: `github.com/Bengo-Hub/shared-auth-client`

**Features**:
- JWKS fetching and caching
- RS256 signature validation
- Issuer and audience validation
- HTTP middleware for Chi and Gin routers
- API key fallback support
- Redis session caching

**Usage**:
```go
import authclient "github.com/Bengo-Hub/shared-auth-client"

validator, _ := authclient.NewValidator(config)
authMiddleware := authclient.NewAuthMiddleware(validator)
router.Use(authclient.GinMiddleware(authMiddleware))
```

**Services Using**: All Go services (auth, subscription, notifications, treasury, logistics, ordering, inventory, pos)

### Recommended Shared Libraries (To Be Created)

#### 2. **shared-service-client** ✅ **IMPLEMENTED**

**Purpose**: Standardized HTTP client for service-to-service communication

**Repository**: `github.com/Bengo-Hub/shared-service-client`

**Features**:
- ✅ Circuit breaker (gobreaker) - Prevents cascading failures
- ✅ Retry with exponential backoff - Automatic retries for transient failures
- ✅ Distributed tracing (OpenTelemetry) - Request tracing integration
- ✅ Structured logging (Zap) - Request/response logging
- ✅ Timeout configuration - Configurable per service
- ✅ Service discovery ready - Works with Kubernetes DNS

**Usage**:
```go
import serviceclient "github.com/Bengo-Hub/shared-service-client"

cfg := serviceclient.DefaultConfig(
    "http://auth-api.auth.svc.cluster.local:4101",
    "auth-service",
    logger,
)
client := serviceclient.New(cfg)
resp, err := client.Get(ctx, "/api/v1/users/"+userID, nil)
```

**Services Using**: ✅ **COMPLETED** (logistics-service, subscription-service; remaining services can migrate incrementally)

#### 3. **shared-events** ✅ **IMPLEMENTED**

**Purpose**: Standardized event publishing/consuming with outbox pattern

**Repository**: `github.com/Bengo-Hub/shared-events`

**Features**:
- ✅ Outbox pattern implementation
- ✅ Event schema validation
- ✅ Event versioning
- ✅ Dead-letter queue handling
- ✅ Idempotency
- ✅ NATS JetStream integration
- ✅ Background publisher worker

**Services Using**: ✅ **COMPLETED** (subscription, notifications, logistics, projects, IoT services)

**Implementation**:
```go
// shared/events/publisher.go
package events

type Publisher struct {
    js     nats.JetStreamContext
    db     *sql.DB
    logger *zap.Logger
}

func (p *Publisher) PublishWithOutbox(ctx context.Context, event Event) error {
    // Store in outbox table (same transaction as domain event)
    // Background worker publishes from outbox
}

// Usage
publisher.PublishWithOutbox(ctx, &UserCreatedEvent{
    UserID:   userID,
    Email:    email,
    TenantID: tenantID,
})
```

**Why Needed**: Ensure reliable event delivery across all services

#### 4. **shared-observability** ⚠️ (To Be Implemented)

**Purpose**: Standardized logging, tracing, and metrics

**Features**:
- Structured logging (Zap) with request ID propagation
- OpenTelemetry tracing
- Prometheus metrics helpers
- Context propagation

**Implementation**:
```go
// shared/observability/logger.go
package observability

func NewLogger(serviceName string) *zap.Logger {
    // Standardized logger with request ID, tenant ID
}

// shared/observability/tracer.go
func NewTracer(serviceName string) trace.Tracer {
    // OpenTelemetry tracer with service name
}

// Usage
logger := observability.NewLogger("subscription-service")
tracer := observability.NewTracer("subscription-service")
```

**Why Needed**: Consistent observability across all services

#### 5. **shared-config** ⚠️ (To Be Implemented)

**Purpose**: Standardized configuration loading and validation

**Features**:
- Environment variable parsing (envconfig)
- Configuration validation
- Default values
- Secret management integration

**Why Needed**: Reduce boilerplate, ensure consistency

### Library Adoption Strategy

**Phase 1** (Q1 2026):
1. ✅ Create `shared-service-client` with circuit breaker and retry - **COMPLETED**
2. ⚠️ Migrate all services to use shared HTTP client - **IN PROGRESS**

**Phase 2** (Q2 2026):
1. Create `shared-events` with outbox pattern
2. Standardize event publishing across all services

**Phase 3** (Q3 2026):
1. Create `shared-observability`
2. Implement distributed tracing
3. Standardize metrics collection

---

## Service-Specific Technology Recommendations

### Detailed Technology Stack by Service

#### 1. **auth-service**

**Current Stack**:
- **Protocol**: REST (HTTP)
- **Message Broker**: NATS JetStream
- **Database**: PostgreSQL
- **Cache**: Redis
- **Authentication**: JWT (self-issued)

**Why This Stack?**:
- ✅ REST for JWT validation endpoints (standard OAuth2/OIDC pattern)
- ✅ NATS for publishing user/tenant events (multiple subscribers)
- ✅ PostgreSQL for user/tenant/role data (ACID compliance required)
- ✅ Redis for JWKS caching and session storage (high-frequency reads)

**Future Enhancements**:
- ⚠️ gRPC for high-throughput user lookups (if needed)
- ⚠️ Webhook endpoints for tenant/user discovery (internal)

---

#### 2. **subscription-service**

**Current Stack**:
- **Protocol**: REST (HTTP)
- **Message Broker**: NATS JetStream (with outbox pattern)
- **Database**: PostgreSQL
- **Cache**: Redis

**Recommended Enhancements**:
- ⚠️ **gRPC** for feature checks (high-frequency calls from all services)
- ⚠️ **GraphQL** for admin dashboards (complex plan/feature queries)

**Why gRPC?**:
- Feature checks called by ALL services on every request
- Lower latency than REST (binary protocol)
- Better suited for high-throughput scenarios
- Reduced overhead for simple request-response

**Usage Pattern**:
```
Every Service → subscription-service (gRPC)
  CheckFeature(tenant_id, feature_code) → {enabled: true, limit: 5}
  Response time: < 10ms (cached), < 50ms (uncached)
```

---

#### 3. **notifications-service**

**Current Stack**:
- **Protocol**: REST (HTTP)
- **Message Broker**: NATS JetStream
- **Database**: PostgreSQL
- **Cache**: Redis

**Recommended Enhancements**:
- ⚠️ **gRPC** for bulk notifications (campaigns, batch sends)
- ⚠️ **WebSocket** for live notification delivery (optional)

**Why gRPC?**:
- Bulk notification campaigns require high throughput
- Streaming support for large batches
- Lower latency for batch operations

**Usage Pattern**:
```
Campaign Service → notifications-service (gRPC)
  SendBulk(notifications: [Notification]) → Stream<Result>
  Throughput: 10,000+ notifications/second
```

---

#### 4. **treasury-service**

**Current Stack**:
- **Protocol**: REST (HTTP)
- **Message Broker**: NATS JetStream (with outbox pattern)
- **Database**: PostgreSQL
- **Cache**: Redis
- **Storage**: MinIO (S3-compatible)

**Recommended Enhancements**:
- ⚠️ **gRPC** for bulk payment processing and settlements
- ✅ **Webhooks** (already implemented for M-Pesa, Stripe)

**Why gRPC?**:
- Bulk settlement processing requires high throughput
- Batch payment operations
- Lower latency for financial operations

---

#### 5. **logistics-service**

**Current Stack**:
- **Protocol**: REST (HTTP)
- **Message Broker**: NATS JetStream
- **Database**: PostgreSQL with PostGIS
- **Cache**: Redis

**Recommended Enhancements**:
- ⚠️ **WebSocket** for real-time task tracking (critical)
- ⚠️ **gRPC** for streaming location updates

**Why WebSocket?**:
- Real-time delivery tracking is core feature
- Customers need live location updates
- Lower latency than polling
- Bidirectional communication (rider → service → customer)

**Why PostGIS?**:
- Geo-spatial queries (nearest rider, route optimization)
- Native PostgreSQL extension for location data

**Usage Pattern**:
```
Frontend → logistics-service (WebSocket)
  Connect: ws://logistics-service/ws/task/{task_id}
  Receive: {location: {lat, lng}, status: "en_route", eta: "5min"}
```

---

#### 6. **ordering-service**

**Current Stack**:
- **Protocol**: REST (HTTP)
- **Message Broker**: NATS JetStream
- **Database**: PostgreSQL
- **Cache**: Redis

**Recommended Enhancements**:
- ⚠️ **WebSocket** for live order status updates
- ⚠️ **GraphQL** for complex menu queries (frontend)

**Why WebSocket?**:
- Customers need live order status updates
- Real-time ETA updates from logistics-service
- Better UX than polling

**Why GraphQL?**:
- Complex menu queries with filters (category, dietary, availability)
- Frontend needs flexible data fetching
- Reduce over-fetching of menu data

---

#### 7. **inventory-service**

**Current Stack**:
- **Protocol**: REST (HTTP)
- **Message Broker**: NATS JetStream
- **Database**: PostgreSQL
- **Cache**: Redis

**Why REST Only?**:
- Stock queries are simple CRUD operations
- No need for real-time updates (event-driven via NATS)
- REST is sufficient for inventory management

**Future Consideration**:
- GraphQL if complex inventory queries needed (aggregations, multi-warehouse views)

---

#### 8. **pos-service**

**Current Stack**:
- **Protocol**: REST (HTTP)
- **Message Broker**: NATS JetStream
- **Database**: PostgreSQL
- **Cache**: Redis

**Why REST Only?**:
- Point-of-sale operations are straightforward CRUD
- Low-latency requirements met by REST
- Event-driven integration via NATS for order sync

---

#### 9. **erp-service** (Django)

**Current Stack**:
- **Protocol**: REST (HTTP) + WebSocket (Django Channels)
- **Message Broker**: RabbitMQ (Celery)
- **Database**: PostgreSQL
- **Cache**: Redis

**Why RabbitMQ Instead of NATS?**:
- ✅ Django ecosystem standard (Celery)
- ✅ Mature Celery integration
- ✅ Long-running task support
- ✅ Better suited for Django/Python stack

**Why WebSocket (Django Channels)?**:
- Real-time payroll updates
- Live dashboard updates
- Django Channels provides native WebSocket support

**Architecture**:
```
ERP Service → RabbitMQ → Celery Workers
            → WebSocket (Django Channels) → Frontend
```

---

### Technology Selection Summary

| Technology | Services Using | Reason |
|------------|---------------|--------|
| **REST API** | All services | Standard synchronous communication, immediate responses |
| **NATS JetStream** | All Go services | Lightweight, native Go support, perfect for async events |
| **RabbitMQ** | ERP (Django) | Celery ecosystem standard, mature Python integration |
| **gRPC** | subscription, notifications, treasury (planned) | High-throughput, bulk operations, low latency |
| **WebSocket** | logistics, ordering, erp (planned) | Real-time tracking, live updates, bidirectional |
| **GraphQL** | ordering (future), subscription (future) | Flexible frontend queries, complex nested data |
| **PostGIS** | logistics | Geo-spatial queries, route optimization |

---

## Data Sharing & Ownership

**Status**: ✅ **WELL DEFINED**

### Principles

1. **Single Source of Truth**: Each service owns its domain data
2. **Reference Only**: Other services store reference IDs (UUIDs)
3. **Event-Driven Sync**: Services sync data via events (NATS)

### Data Ownership Matrix

| Entity | Owner | Reference Pattern |
|--------|-------|-------------------|
| Users | auth-service | `auth_service_user_id` (UUID) |
| Tenants | auth-service | `tenant_id` (UUID) |
| Outlets | auth-service | `outlet_id` (UUID) |
| Riders | logistics-service | `rider_id` (UUID) |
| Inventory Items | inventory-service | `inventory_item_id` (UUID) |
| Payment Intents | treasury-service | `payment_intent_id` (UUID) |
| Orders | ordering-service | `order_id` (UUID) |
| Subscriptions | subscription-service | `subscription_id` (UUID) |

### Sync Mechanisms

**Event-Driven** (Preferred):
- `auth.user.created` → Services create local user references
- `auth.tenant.created` → Services initialize tenant data

**REST API** (For on-demand sync):
- `GET /api/v1/users/{id}` → Fetch user details from auth-service
- Cache in Redis for performance

**Redis Caching**:
- Cache frequently accessed data (users, tenants)
- TTL: 5-60 minutes
- Invalidate on update events

---

## Security & Authentication

**Status**: ✅ **IMPLEMENTED** (Via shared-auth-client)

### Dual Authentication Support (JWT + API Key)

All BengoBox microservices MUST support **dual authentication** - accepting either JWT Bearer tokens OR API Keys interchangeably. This enables:

1. **User Authentication (JWT)**: Interactive user sessions via OAuth2/OIDC flow
2. **Service Authentication (API Key)**: Automated service-to-service calls, webhooks, cron jobs

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Dual Authentication Flow                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Request ──► Authorization Header Present?                               │
│                    │                                                     │
│              ┌─────┴─────┐                                               │
│              │           │                                               │
│              ▼           ▼                                               │
│      Bearer Token?   X-API-Key?                                          │
│              │           │                                               │
│              ▼           ▼                                               │
│      Validate JWT    Validate API Key                                    │
│      (RS256/JWKS)    (auth-service call)                                 │
│              │           │                                               │
│              └─────┬─────┘                                               │
│                    ▼                                                     │
│            Extract Claims                                                │
│         (user_id, tenant_id,                                             │
│          roles, subscription)                                            │
│                    │                                                     │
│                    ▼                                                     │
│            Inject into Context                                           │
│                    │                                                     │
│                    ▼                                                     │
│              Continue to Handler                                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Current Implementation

**JWT Validation** (Shared Library):
- ✅ `shared/auth-client` library for all services
- ✅ JWKS caching with auto-refresh (1 hour TTL, 5 min refresh)
- ✅ RS256 signature validation
- ✅ Issuer and audience validation
- ✅ Redis session caching (5 min TTL)

**API Key Validation** (Shared Library):
- ✅ API key authentication via auth-service `/api/v1/admin/api-keys/validate`
- ✅ Service accounts for automated operations
- ✅ Scoped permissions per API key
- ✅ Response caching (5 min TTL)

**Middleware Integration** (AuthMiddleware):
```go
// NewAuthMiddlewareWithAPIKey creates middleware supporting both JWT and API Key
authMiddleware := authclient.NewAuthMiddlewareWithAPIKey(
    jwtValidator,      // JWKS-based JWT validation
    apiKeyValidator,   // auth-service API key validation
)

// Apply to protected routes
r.Use(authMiddleware.RequireAuth)
```

### Claims Structure

All authentication methods produce unified `Claims` with:

```go
type Claims struct {
    // Core identity
    SessionID string   `json:"sid"`
    TenantID  string   `json:"tenant_id"`
    Email     string   `json:"email"`
    Scope     []string `json:"scope"`

    // RBAC roles from auth-service
    Roles []string `json:"roles"`

    // Subscription data (embedded at login)
    SubscriptionPlan     string         `json:"subscription_plan"`
    SubscriptionFeatures []string       `json:"subscription_features"`
    SubscriptionLimits   map[string]int `json:"subscription_limits"`
    SubscriptionStatus   string         `json:"subscription_status"`

    // Service account identification
    ServiceName string `json:"service_name"`
    IsService   bool   `json:"is_service"`
}
```

### Trinity Authorization Pattern

BengoBox uses a 3-layer authorization model:

```
┌─────────────────────────────────────────────────────────────────┐
│                 Trinity Authorization Model                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Layer 1: RBAC (auth-service)                                    │
│  ├── WHO can perform WHAT actions                                │
│  └── Global roles: admin, manager, operator, viewer              │
│                                                                  │
│  Layer 2: Licensing (subscription-service)                       │
│  ├── WHICH features are enabled for tenant                       │
│  └── Plans: STARTER, GROWTH, PROFESSIONAL                        │
│                                                                  │
│  Layer 3: Resource Ownership (domain services)                   │
│  ├── Service-specific RBAC extensions                            │
│  └── Example: POS cashier, kitchen manager, driver               │
│                                                                  │
│  Authorization Check:                                            │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ RBAC Check (Has Role?) ──► Feature Check (Has License?)  │    │
│  │           │                          │                   │    │
│  │           ▼                          ▼                   │    │
│  │   Ownership Check (Owns Resource?) ──► ALLOW/DENY        │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Service-to-Service Authentication

**Recommended Pattern**: Service Account JWT via API Keys

```go
// Service obtaining JWT for inter-service calls
client := authclient.NewClient(authServiceURL, logger)
resp, err := client.ServiceLogin(ctx, authclient.ServiceLoginRequest{
    APIKey:     os.Getenv("SERVICE_API_KEY"),
    ServiceName: "ordering-service",
})
// Use resp.AccessToken for inter-service calls
```

**Alternative**: Direct API Key usage (simpler but requires auth-service availability)

```go
// Direct API key in service-to-service calls
req.Header.Set("X-API-Key", os.Getenv("INVENTORY_SERVICE_API_KEY"))
```

### Authorization Middleware (v0.2.0+)

The `shared-auth-client` library provides built-in middleware for common authorization patterns:

**Role-Based Access Control**:
```go
// Require specific roles (superuser always bypasses)
r.With(authclient.RequireRole("admin", "manager")).Post("/settings", handler.UpdateSettings)

// Require admin role
r.With(authclient.RequireAdmin()).Delete("/users/{id}", handler.DeleteUser)
```

**Subscription Feature Gating**:
```go
// Require specific subscription feature
r.With(authclient.RequireFeature("group_ordering")).Post("/group-orders", handler.CreateGroupOrder)

// Require minimum plan tier
r.With(authclient.RequirePlan("PROFESSIONAL")).Get("/analytics", handler.GetAnalytics)

// Require active subscription
r.With(authclient.RequireActiveSubscription()).Post("/orders", handler.CreateOrder)
```

**Handler-Level Checks**:
```go
func (h *Handler) CreateOrder(w http.ResponseWriter, r *http.Request) {
    claims, _ := authclient.ClaimsFromContext(r.Context())

    // Check RBAC
    if !claims.HasAnyRole("customer", "staff") {
        // Return 403
    }

    // Check subscription feature
    if !claims.HasFeature("express_delivery") {
        // Express delivery not available in this plan
    }

    // Check usage limits
    if orderCount >= claims.GetLimit("monthly_orders") {
        // Return 403 with upgrade prompt
    }
}
```

### Gaps

- ❌ No mTLS for service-to-service communication
- ❌ No request signing for internal APIs
- ❌ No rate limiting for service-to-service calls

### Future Enhancements

- mTLS for service-to-service communication (via service mesh)
- Request signing for high-security scenarios
- Rate limiting per service (via API gateway or middleware)

---

## Reliability & Resilience

**Status**: ⚠️ **PARTIAL** (Some patterns implemented)

### Patterns

#### 1. Circuit Breaker

**Status**: ❌ Not implemented

#### 1. Circuit Breaker

**Status**: ✅ **IMPLEMENTED** (via `shared-service-client`)
- Opens after 5 consecutive failures
- 30-second timeout before attempting to close
- Prevents cascading failures

#### 2. Retry with Backoff

**Status**: ✅ **IMPLEMENTED** (via `shared-service-client`)
- Exponential backoff: 100ms to 5s
- Maximum retry time: 30 seconds
- Retries on network errors and HTTP 5xx/429

#### 3. Timeout Configuration

**Status**: ✅ **STANDARDIZED** (via `shared-service-client`)
- Default HTTP client timeout: 10 seconds
- Configurable per service
- Context-aware timeouts

#### 4. Graceful Degradation

**Status**: ⚠️ **PARTIAL** - Services should implement fallbacks for critical dependencies

#### 5. Health Checks

**Status**: ✅ **IMPLEMENTED** - All services have `/healthz` endpoints

---

## Observability

**Status**: ⚠️ **PARTIAL** (Logging implemented, tracing/metrics partial)

### Current State

- ✅ Structured logging (Zap) in all Go services
- ⚠️ Prometheus metrics (partial)
- ❌ Distributed tracing (not implemented)
- ✅ Request ID propagation (implemented)

### Recommendations

**Distributed Tracing**: OpenTelemetry collector deployed, tracing integrated in `shared-service-client`

**Metrics**: Prometheus scraping enabled via ServiceMonitors, custom metrics vary by service

**Logging Standards**: Structured logging (Zap) with request ID and tenant ID propagation

---

## Implementation Status

**Last Updated**: February 2026

### ✅ Fully Implemented & Production-Ready

- **NATS JetStream** for async events (all Go services)
- **RabbitMQ** for Celery tasks (Django/ERP service)
- **REST APIs** for synchronous operations
- **Shared auth-client library** (`shared-auth-client` v0.3.1) - JWT/API Key auth, RBAC, subscription feature gating
- **Shared service-client library** (`shared-service-client`) - Circuit breaker, retry, tracing
- **Shared events library** (`shared-events`) - Transactional outbox pattern
- **Shared password-hasher library** (`shared-password-hasher`) - Argon2id hashing
- **Service Discovery** via Kubernetes DNS
- **Redis** for caching and sessions
- **PostgreSQL** per-service databases
- **NGINX Ingress Controller** as API gateway
- **Health checks** (`/healthz` endpoints)
- **Structured logging** (Zap)
- **Prometheus metrics** (ServiceMonitors)
- **ArgoCD GitOps** deployment
- **Horizontal Pod Autoscaling** (HPA)

### Outbox Pattern Implementation Status

| Service | Status | Library | Worker | Priority |
|---------|--------|---------|--------|----------|
| logistics-service | ✅ Implemented | shared-events | Yes | - |
| finance-service | ✅ Implemented | shared-events | Yes (dedicated) | - |
| notifications-service | ✅ Implemented | shared-events | Yes (dedicated) | - |
| projects-service | ✅ Implemented | shared-events | Yes | - |
| subscription-service | ✅ Implemented | shared-events | Yes | - |
| iot-service | ✅ Implemented | shared-events | Yes | - |
| **inventory-service** | ⚠️ Schema created | shared-events | Pending | 🟡 Medium (Q1 2026) |
| **pos-service** | ❌ Missing | - | - | 🔴 High (Q1 2026) |
| **ordering-service** | ⚠️ Schema created | shared-events | Pending | 🟡 Medium (Q1 2026) |
| auth-service | ⚠️ Partial | - | - | 🟡 Medium (Q2 2026) |
| ticketing-service | ❌ Missing | - | - | 🟢 Low (Q2 2026) |

### Circuit Breaker (shared-service-client) Adoption

| Service | Status | Notes |
|---------|--------|-------|
| logistics-service | ✅ Migrated | Production |
| subscription-service | ✅ Migrated | Production |
| notifications-service | ⚠️ Partial | In progress |
| finance-service | ⚠️ Partial | In progress |
| projects-service | ⚠️ Partial | In progress |
| **ordering-service** | ❌ Not migrated | Migration needed |
| **inventory-service** | ❌ Not migrated | Migration needed |
| **pos-service** | ❌ Not migrated | Migration needed |
| auth-service | ❌ Not migrated | Q2 2026 |
| ticketing-service | ❌ Not migrated | Q2 2026 |
| iot-service | ❌ Not migrated | Q2 2026 |

### Code Duplication Analysis

**Identified duplications requiring shared libraries:**

| Pattern | Duplication % | Location | Solution |
|---------|--------------|----------|----------|
| Middleware (RequestID, Tenant, Logging, Recover) | ✅ **Resolved** | `internal/shared/middleware/` | Migrated to `httpware` v0.1.1 |
| Configuration struct | 95% | `internal/config/config.go` | Create `shared-config` |
| Logger initialization | 100% | `internal/shared/logger/` | Create `shared-observability` |
| Error response format | 80% | Various handlers | Create `shared-errors` |

### ⚠️ Partially Implemented

- **Webhooks**: External implemented (M-Pesa, Stripe), internal infrastructure missing
- **Metrics**: Prometheus scraping enabled, custom metrics vary by service
- **Distributed tracing**: OpenTelemetry collector deployed, integration in progress

### ❌ Not Yet Implemented

- **gRPC/ConnectRPC**: Planned Q2 2026 (subscription, treasury, notifications)
- **WebSockets**: Planned Q2 2026 (logistics, ordering)
- **GraphQL**: Future consideration
- **Shared middleware library**: ✅ Completed (httpware v0.1.1, Jan 2026)
- **Shared config library**: Planned Q2 2026
- **Shared observability library**: Planned Q2 2026
- **mTLS**: Not implemented (rely on Kubernetes network policies)
- **Service mesh**: Not implemented (rely on Kubernetes networking)

---

## Migration Roadmap

### Phase 1: Foundation (Q1 2026) - 🚧 **IN PROGRESS**

**Shared Libraries - COMPLETED:**
- ✅ `shared-auth-client` v0.2.0 - JWT validation, JWKS caching, subscription claims, RBAC helpers, feature gating middleware
- ✅ `shared-service-client` v0.1.0 - Circuit breaker, retry, tracing
- ✅ `shared-events` v0.1.0 - Transactional outbox pattern
- ✅ `shared-password-hasher` v0.1.0 - Argon2id password hashing
- ✅ `httpware` v0.2.0 - HTTP middleware (RequestID, Tenant, Logging, Recover, CORS)

**Outbox Pattern Migration (✅ Schema & Repository COMPLETED):**
- [x] Add outbox to inventory-service ✅ (Jan 2026) - Schema + repository created
- [x] Add outbox to pos-service ✅ (Jan 2026) - Schema + repository created
- [x] Add outbox to ordering-service ✅ (Jan 2026) - Ent schema + repository created
- [ ] Integrate background publisher worker in all services
- [ ] Replace direct NATS publish with PublishWithOutbox

**Circuit Breaker Migration:**
- [ ] Migrate ordering-service to shared-service-client
- [ ] Migrate inventory-service to shared-service-client
- [ ] Migrate pos-service to shared-service-client

**Auth-Client v0.2.0 Upgrade (✅ COMPLETED):**
- [x] Upgrade ordering-service to auth-client v0.2.0 ✅ (Jan 2026)
- [x] Upgrade inventory-service to auth-client v0.2.0 ✅ (Jan 2026)
- [x] Upgrade pos-service to auth-client v0.2.0 ✅ (Jan 2026)

**Code Duplication Reduction:**
- [x] Create `httpware` package (RequestID, Tenant, Logging, Recover, CORS) ✅
- [x] Migrate inventory-service to httpware v0.1.1 ✅
- [x] Migrate pos-service to httpware v0.1.1 ✅
- [x] Migrate ordering-service to httpware v0.1.1 ✅

### Phase 2: Standardization (Q2 2026)

**Remaining Migrations:**
- [ ] Add outbox to auth-service
- [ ] Add outbox to ticketing-service
- [ ] Complete shared-service-client migration for all services

**New Shared Libraries:**
- [ ] Create `shared-config` package
- [ ] Create `shared-observability` package
- [ ] Migrate all services to new shared packages

**High-Performance Communication:**
- [ ] Implement gRPC/ConnectRPC in subscription-service
- [ ] Implement gRPC/ConnectRPC in treasury-service

### Phase 3: Real-Time Features (Q3 2026)

**WebSocket Implementation:**
- [ ] Real-time tracking in logistics-service
- [ ] Order status updates in ordering-service

**Internal Webhooks:**
- [ ] Webhook registration infrastructure
- [ ] Webhook retry mechanism with exponential backoff

**Observability:**
- [ ] Full OpenTelemetry integration across all services
- [ ] Distributed tracing visualization in Grafana

### Phase 4: Advanced Features (Q4 2026+)

**Optional Enhancements:**
- [ ] GraphQL gateway for flexible frontend queries
- [ ] Service mesh evaluation (Istio/Linkerd)
- [ ] mTLS for service-to-service communication
- [ ] gRPC in notifications-service and logistics-service

---

## Technology Stack Summary

| Layer | Technology | Status | Services Using |
|-------|-----------|--------|----------------|
| **Async Events** | NATS JetStream | ✅ Implemented | All Go services |
| **Synchronous APIs** | REST (Chi/Gin) | ✅ Implemented | All services |
| **High-Throughput** | ConnectRPC (gRPC) | ⚠️ Planned Q2 2026 | subscription, treasury |
| **Real-Time** | WebSockets | ⚠️ Planned Q3 2026 | logistics, ordering |
| **Flexible Queries** | GraphQL | ❌ Future | - |
| **Callbacks** | Webhooks | ⚠️ Partial | treasury (external) |
| **Service Discovery** | Kubernetes DNS | ✅ Implemented | All services |
| **Authentication** | JWT (shared-auth-client) | ✅ Implemented | All Go services |
| **Resilience** | Circuit Breaker (shared-service-client) | ✅ Implemented | logistics, subscription (others migrating) |
| **Event Reliability** | Outbox (shared-events) | ✅ Implemented | 6/11 services (3 migrating) |
| **Observability** | Zap + Prometheus + OTEL | ⚠️ Partial | All services (tracing in progress) |

### Shared Libraries Summary

| Library | Version | Purpose | Adoption |
|---------|---------|---------|----------|
| `shared-auth-client` | v0.3.1 | JWT validation, JWKS, RBAC, subscription claims, feature gating | 100% (all services) |
| `shared-service-client` | v0.2.0 | Circuit breaker, retry, tracing | 20% (2/10 services) |
| `shared-events` | v0.2.0 | Transactional outbox pattern | 82% (9/11 services) - ordering, inventory, pos schemas added Jan 2026 |
| `shared-password-hasher` | v0.1.0 | Argon2id password hashing | auth-service |
| `httpware` | v0.2.0 | RequestID, Tenant, Logging, Recover, CORS | 45% (5/11 services) |
| `shared-config` | Planned | Configuration loading | 0% (to be created) |
| `shared-observability` | Planned | Logging, tracing, metrics | 0% (to be created) |

---

## Architecture Diagram

### Complete Microservices Architecture Layout

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 EXTERNAL USERS & CLIENTS                                                      │
│                         (Web Browsers, Mobile Apps, Third-Party APIs)                                        │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              │ HTTPS/TLS
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                         NGINX INGRESS CONTROLLER                                              │
│                                 (API Gateway / Load Balancer)                                                │
│                              cert-manager (Let's Encrypt TLS)                                                │
│                                                                                                               │
│  Domains:                                                                                                     │
│  • sso.codevertexitsolutions.com → auth-api                                                                  │
│  • accounts.codevertexitsolutions.com → auth-ui                                                              │
│  • notifications.codevertexitsolutions.com → notifications-service                                           │
│  • booksapi.codevertexitsolutions.com → treasury-api                                                         │
│  • books.codevertexitsolutions.com → treasury-ui                                                             │
│  • orderingapi.codevertexitsolutions.com → ordering-backend                                                     │
│  • ordersapp.codevertexitsolutions.com → ordering-frontend                                                   │
│  • theurbanloftcafe.com → cafe-website                                                             │
│  • posapi.codevertexitsolutions.com → pos-api                                                                │
│  • pos.codevertexitsolutions.com → pos-ui                                                                    │
│  • pricingapi.codevertexitsolutions.com → subscription-api                                                   │
│  • projectsapi.codevertexitsolutions.com → projects-api                                                      │
│  • projects.codevertexitsolutions.com → projects-ui                                                          │
│  • iot.codevertexitsolutions.com → iot-api                                                                   │
│  • ispbillingapi.codevertexitsolutions.com → isp-billing-backend                                             │
│  • ispbilling.codevertexitsolutions.com → isp-billing-frontend                                               │
│  • ticketingapi.codevertexitsolutions.com → ticketing-api                                                     │
│  • ticketing.codevertexitsolutions.com → ticketing-ui                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              │ HTTP (Internal)
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    FRONTEND SERVICES (UI)                                                     │
│                                                                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
│  │  auth-ui     │  │ treasury-ui  │  │  cafe-ui     │  │   pos-ui     │  │   erp-ui     │                │
│  │  (Next.js)   │  │  (Next.js)   │  │  (Next.js)   │  │  (Next.js)   │  │   (Vue.js)   │                │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                │
│         │                 │                  │                 │                 │                          │
│         └─────────────────┴──────────────────┴─────────────────┴─────────────────┘                          │
│                                    │ HTTPS (External URLs)                                                   │
└────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    BACKEND SERVICES (APIs)                                                    │
│                                                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                                    CORE SERVICES (Go)                                                 │   │
│  │                                                                                                       │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │   │
│  │  │auth-service  │  │subscription- │  │notifications │  │treasury-     │  │logistics-    │        │   │
│  │  │  :4101       │  │service       │  │service       │  │service       │  │service       │        │   │
│  │  │  (REST)      │  │  :4005       │  │  :4000       │  │  :4000       │  │  :4000       │        │   │
│  │  │              │  │  (REST+gRPC) │  │  (REST+gRPC) │  │  (REST+gRPC) │  │  (REST+WS)   │        │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │   │
│  │         │                 │                  │                 │                 │                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │   │
│  │  │ordering-     │  │inventory-    │  │pos-service   │  │iot-service   │  │projects-     │        │   │
│  │  │service       │  │service       │  │  :4000       │  │  :4000       │  │service       │        │   │
│  │  │  :4000       │  │  :4000       │  │  (REST)      │  │  (REST)      │  │  :4000       │        │   │
│  │  │  (REST+WS)   │  │  (REST)      │  │              │  │              │  │  (REST)      │        │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │   │
│  │         │                 │                  │                 │                 │                  │   │
│  └─────────┼─────────────────┼──────────────────┼─────────────────┼─────────────────┼──────────────────┘   │
│            │                 │                  │                 │                 │                      │
│  ┌─────────┴─────────────────┴──────────────────┴─────────────────┴─────────────────┴──────────────────┐  │
│  │                                    LEGACY SERVICES (Python/Django)                                  │  │
│  │                                                                                                      │  │
│  │  ┌──────────────┐                                                                                  │  │
│  │  │erp-service   │                                                                                  │  │
│  │  │  :4000       │                                                                                  │  │
│  │  │  (REST+WS)   │                                                                                  │  │
│  │  │  Celery      │                                                                                  │  │
│  │  └──────┬───────┘                                                                                  │  │
│  └─────────┼───────────────────────────────────────────────────────────────────────────────────────────┘  │
│            │                                                                                                │
└────────────┼────────────────────────────────────────────────────────────────────────────────────────────────┘
             │
             │ Kubernetes DNS Service Discovery
             │ {service}.{namespace}.svc.cluster.local
             │
             ├──────────────────────────────────────────────────────────────────────────────────────────────┐
             │                                                                                                │
             ▼                                  ▼                                  ▼                          ▼
┌──────────────────────────┐    ┌──────────────────────────┐    ┌──────────────────────────┐    ┌──────────────┐
│   INFRASTRUCTURE LAYER   │    │    MESSAGING LAYER       │    │    STORAGE LAYER         │    │ OBSERVABILITY│
│   (Namespace: infra)     │    │   (Namespace: messaging) │    │   (Namespace: storage)   │    │   (infra)    │
│                          │    │                          │    │                          │    │              │
│  ┌────────────────────┐ │    │  ┌────────────────────┐ │    │  ┌────────────────────┐ │    │  ┌──────────┐ │
│  │  Redis             │ │    │  │  NATS JetStream    │ │    │  │  MinIO (S3)        │ │    │  │Prometheus│ │
│  │  :6379             │ │    │  │  :4222             │ │    │  │  :9000             │ │    │  │          │ │
│  │  (Cache/Sessions)  │ │    │  │  (Go services)     │ │    │  │  (Object Storage)  │ │    │  │Grafana   │ │
│  └────────────────────┘ │    │  └────────────────────┘ │    │  └────────────────────┘ │    │  │          │ │
│                          │    │                          │    │                          │    │  │OTEL      │ │
│  ┌────────────────────┐ │    │  ┌────────────────────┐ │    │                          │    │  │Collector │ │
│  │  PostgreSQL        │ │    │  │  RabbitMQ          │ │    │                          │    │  │:4317     │ │
│  │  (Per-service DBs) │ │    │  │  :5672             │ │    │                          │    │  └──────────┘ │
│  │                    │ │    │  │  (Django/Celery)   │ │    │                          │    │              │
│  │  • auth-db         │ │    │  └────────────────────┘ │    │                          │    │              │
│  │  • subscription-db │ │    │                          │    │                          │    │              │
│  │  • treasury-db     │ │    │                          │    │                          │    │              │
│  │  • logistics-db    │ │    │                          │    │                          │    │              │
│  │  • ordering-db     │ │    │                          │    │                          │    │              │
│  │  • notifications-db│ │    │                          │    │                          │    │              │
│  │  • inventory-db    │ │    │                          │    │                          │    │              │
│  │  • pos-db          │ │    │                          │    │                          │    │              │
│  │  • erp-db          │ │    │                          │    │                          │    │              │
│  └────────────────────┘ │    │                          │    │                          │    │              │
└──────────────────────────┘    └──────────────────────────┘    └──────────────────────────┘    └──────────────┘
```

### Service Communication Flow

#### 1. **External Request Flow**
```
Client → NGINX Ingress → Frontend Service → Backend Service (REST)
                                           → Infrastructure (Redis/DB)
```

#### 2. **Service-to-Service Communication (Internal)**
```
Service A → Kubernetes DNS → Service B
         (auth-api.auth.svc.cluster.local:4101)
```

#### 3. **Event-Driven Communication**
```
Service A → NATS JetStream → Service B (async)
         (nats.messaging.svc.cluster.local:4222)
         Subject: {service}.{entity}.{action}
```

#### 4. **Real-Time Communication**
```
Frontend → WebSocket → Backend Service → Redis Pub/Sub → WebSocket → Frontend
```

### Technology Stack by Layer

#### **Presentation Layer**
- **Frontend**: Next.js (React), Vue.js
- **API Gateway**: NGINX Ingress Controller
- **TLS**: cert-manager + Let's Encrypt

#### **Application Layer (Backend Services)**
- **Language**: Go (primary), Python (Django - ERP)
- **REST APIs**: Chi Router (Go), Gin (Go), Django REST Framework (Python)
- **Real-Time**: WebSocket (planned), Django Channels (ERP)

#### **Communication Layer**
- **Async Events**: NATS JetStream (Go services), RabbitMQ (Django/Celery)
- **Service Discovery**: Kubernetes DNS
- **Load Balancing**: Kubernetes Service

#### **Data Layer**
- **Databases**: PostgreSQL (per-service), PostGIS (logistics)
- **Cache**: Redis (sessions, query cache, pub/sub)
- **Object Storage**: MinIO (S3-compatible)

#### **Observability Layer**
- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry Collector
- **Logging**: Structured logging (Zap)

#### **Deployment Layer**
- **Orchestration**: Kubernetes
- **GitOps**: ArgoCD
- **Package Manager**: Helm
- **CI/CD**: GitHub Actions

### Shared Libraries Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                    SHARED LIBRARIES                             │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │shared-auth-  │  │shared-service│  │shared-events │        │
│  │client        │  │client        │  │              │        │
│  │✅ Implemented│  │✅ Implemented│  │✅ Implemented│        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
│         │                 │                  │                  │
│  ┌──────┴─────────────────┴──────────────────┴───────┐        │
│  │        All Go Services Use These Libraries         │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │shared-       │  │shared-config │                            │
│  │observability │  │              │                            │
│  │⚠️ Planned    │  │⚠️ Planned    │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

### Key Integration Points

1. **Authentication Flow**:
   - All services validate JWT via `shared-auth-client`
   - JWKS fetched from auth-service
   - Session cached in Redis

2. **Event Flow**:
   - Services publish events to NATS JetStream
   - Other services subscribe to relevant events
   - Outbox pattern ensures reliable delivery

3. **Data Sync Flow**:
   - Auth-service publishes user/tenant events
   - Downstream services consume events
   - Services create local references (no duplication)

4. **Feature Check Flow**:
   - Service calls subscription-service (REST)
   - Response cached in Redis
   - Feature gate enforced

5. **Payment Flow**:
   - Ordering-service → Treasury-service (REST)
   - Treasury-service publishes payment events (NATS)
   - Notifications-service consumes events

---

## Recent Architecture Additions (February 2026)

### Inventory Service MVP (February 2026)

The **inventory-service** was upgraded from scaffold-only to a full MVP with business logic:

- **5 Ent schemas**: item, warehouse, inventorybalance, reservation, consumption
- **8 HTTP endpoints** matching ordering-backend's inventory client DTOs: stock availability, bulk availability, reservation CRUD (create/get/release/consume), direct consumption
- **Seed data**: 39 Urban Loft Cafe menu items across 7 categories with realistic KES prices
- **Shared library alignment**: httpware v0.2.0, shared-events v0.2.0, shared-auth-client v0.3.1
- **Cross-service integration**: Ordering-backend calls inventory-service synchronously for stock checks and reservations during order placement

### Event Wiring Fix (February 2026)

Fixed NATS subject mismatch between ordering-backend and logistics-api:
- **Before**: logistics-api subscribed to `ordering.order.confirmed` (wrong)
- **After**: logistics-api subscribes to `ordering.order.ready` (matches publisher)
- This ensures delivery tasks are automatically created when orders are ready for fulfilment

### Transactional Outbox Pattern

The **transactional outbox pattern** is now implemented across auth-service and subscription-service for reliable event publishing:

**How it works:**
1. Service writes domain entity AND an `outbox_events` row in the **same database transaction**
2. A background publisher (`outbox-publisher`) polls the outbox table for `PENDING` events
3. Publisher sends events to NATS JetStream and marks them as `PUBLISHED`
4. Failed publishes are retried with exponential backoff (max 10 attempts)

**Implementation per service:**

| Service | Outbox Schema | Payload Type | Status Type | Publisher |
|:---|:---|:---|:---|:---|
| auth-service | `outbox_events` (Ent) | `[]byte` (JSON) | Enum (`PENDING`, `PUBLISHED`, `FAILED`) | `cmd/outbox-publisher` |
| subscription-service | `outbox_events` (Ent) | `map[string]any` | String (`PENDING`, `PUBLISHED`, `FAILED`) | `cmd/outbox-publisher` |

**Event envelope format:**
```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "aggregate_type": "user|tenant|subscription",
  "aggregate_id": "uuid",
  "event_type": "user.created|subscription.activated",
  "payload": { ... },
  "timestamp": "RFC3339",
  "version": "1.0"
}
```

**NATS subject naming convention:** `{service}.events` (e.g., `auth.events`, `subscriptions.events`)

### Subscription Service Lifecycle

The subscription-service implements a **finite state machine** for subscription management:

**States:** `trialing` → `active` → `past_due` → `cancelled` / `expired`

**Key operations:**
- **Trial provisioning**: Automatically created on `tenant.created` event (14-day trial)
- **Activation**: On successful payment, transitions from `trialing`/`past_due` to `active`
- **Cancellation**: Immediate or end-of-period, triggers `subscription.cancelled` event
- **JWT enrichment**: Active subscriptions embed product IDs and plan tier in JWT claims

**Product model:** 8 products (ordering, logistics, treasury, pos, analytics, notifications, auth, inventory) × 3 bundles (starter, professional, enterprise) × 6 plans (monthly/yearly per bundle)

### Notification Worker Architecture

The notifications-service worker processes messages from NATS JetStream with retry logic:

**Architecture:**
- Worker subscribes to `notifications.events` with durable consumer
- Messages contain: channel (email/sms/push), template ID, recipient list, metadata
- Template engine renders with tenant branding (name, logo, colors)

**Retry pattern:**
- Max 3 delivery attempts via NATS `MaxDeliver(3)`
- Failed deliveries: `NAck()` → redelivery after 30s `AckWait`
- Template/parse errors: `Ack()` immediately (not transient)
- Max retries exceeded: `Ack()` + error log (dead-letter)

**Provider abstraction:**
- Email: SendGrid (HTTP API, no SDK), SMTP fallback
- SMS: Twilio (REST API, basic auth)
- Push: Placeholder for FCM/APNS
- Per-tenant provider override via database config

---

## Conclusion

BengoBox's microservices architecture is built on **solid production-ready foundations** with a well-orchestrated centralized DevOps infrastructure:

### Strengths

1. **✅ Production Infrastructure**: Fully operational Kubernetes cluster with centralized `devops-k8s` repository
2. **✅ Service Discovery**: Kubernetes DNS-based discovery eliminates need for service registry
3. **✅ Message Brokers**: NATS JetStream for Go services, RabbitMQ for Django/Celery (optimal tech stack per service type)
4. **✅ Shared Infrastructure**: Centralized Redis, NATS, monitoring, and observability
5. **✅ GitOps**: ArgoCD-based deployments ensure consistency and reliability
6. **✅ Standardized Auth**: `shared-auth-client` provides consistent JWT validation across all services
7. **✅ Resilience**: `shared-service-client` provides circuit breaker, retry, and tracing for service-to-service calls
8. **✅ Event Reliability**: `shared-events` library provides standardized outbox pattern (implemented in subscription-service)

### Areas for Enhancement

1. **Immediate Priorities (Q1 2026)**:
   - ✅ Create `shared-service-client` library - **COMPLETED**
   - ✅ Migrate all services to use `shared-service-client` - **COMPLETED** (logistics-service, subscription-service)
   - ✅ Create `shared-events` library - **COMPLETED**
   - ✅ Migrate all services to use `shared-events` for outbox pattern - **COMPLETED** (subscription, notifications, logistics, projects, IoT services)

2. **Short-Term (Q2-Q3 2026)**:
   - Implement gRPC/ConnectRPC for high-throughput operations
   - Implement WebSockets for real-time tracking
   - Build internal webhook infrastructure

3. **Long-Term (Q4 2026+)**:
   - Service mesh evaluation (Istio/Linkerd)
   - GraphQL for flexible frontend queries
   - Advanced observability with full distributed tracing

### Architecture Highlights

- **Hybrid Communication**: Right tool for each use case (REST for sync, NATS for async, WebSocket for real-time)
- **Technology Fit**: Go services use NATS, Python/Django uses RabbitMQ (optimal for each ecosystem)
- **Zero Duplication**: Clear data ownership with reference-only patterns
- **Scalable Foundation**: Kubernetes-native architecture with auto-scaling and GitOps
- **Production-Ready**: Fully operational infrastructure with monitoring, logging, and observability

This hybrid architecture ensures optimal communication patterns for each use case while maintaining scalability, performance, and security across all BengoBox microservices.

---

## References

- [Cross-Service Data Ownership](./CROSS-SERVICE-DATA-OWNERSHIP.md)
- [Platform Audit & Standardization](./PLATFORM-AUDIT-AND-STANDARDIZATION.md)
- [Subscription Service Integrations](../subscription-service/docs/integrations.md)
- [Logistics Service Integrations](../logistics-service/logistics-api/docs/integrations.md)
- [Ordering Service Integrations](../ordering-service/ordering-backend/docs/integrations.md)