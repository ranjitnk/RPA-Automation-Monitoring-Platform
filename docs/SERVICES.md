# Service layer structure

## Pattern

Each domain has a service class (or module of functions) that:

1. Accepts `AsyncSession` and optional `UserContext` in constructor/factory.
2. Encapsulates transactions (`async with session.begin()`).
3. Raises domain exceptions from `app.core.exceptions`.
4. Never imports FastAPI `Request`/`Response`.

## Service catalog

| Service | File | Responsibilities |
|---------|------|------------------|
| `AuthService` | `auth_service.py` | Login, token refresh, password reset |
| `UserService` | `user_service.py` | CRUD users, assign roles |
| `RBACService` | `rbac_service.py` | Permission checks, role resolution |
| `EnvironmentService` | `environment_service.py` | Environment CRUD, credential encrypt/decrypt |
| `OrchestratorSyncService` | `orchestrator_sync_service.py` | Coordinate full/incremental sync |
| `QueueService` | `queue_service.py` | Queue metrics, history |
| `JobService` | `job_service.py` | Job listing, details, trends |
| `RobotService` | `robot_service.py` | Robot status, machine mapping |
| `AIWorkflowService` | `ai_workflow_service.py` | Agentic run ingestion & metrics |
| `DashboardService` | `dashboard_service.py` | Aggregate KPIs, cached rollups |
| `SLAService` | `sla_service.py` | Rules, evaluation, alert lifecycle |
| `AuditService` | `audit_service.py` | Write audit events, query ES/DB |
| `RealtimeService` | `realtime_service.py` | Publish Redis events |
| `NotificationService` | `notification_service.py` | Email, webhook, Teams adapters |

## Integrations (called by services, not API)

| Client | File |
|--------|------|
| Orchestrator OAuth | `integrations/uipath/auth.py` |
| Orchestrator REST | `integrations/uipath/client.py` |
| Queues API | `integrations/uipath/queues.py` |
| Jobs API | `integrations/uipath/jobs.py` |
| Robots API | `integrations/uipath/robots.py` |
| Elasticsearch | `integrations/elasticsearch/logger.py` |

## Workers invoke services

```text
tasks/sync_environment.py  → OrchestratorSyncService.sync_all(env_id)
tasks/evaluate_sla.py      → SLAService.evaluate_environment(env_id)
tasks/dispatch_alerts.py   → NotificationService.send_pending()
```

## Testing

- Unit test services with mocked repositories and httpx MockTransport.
- Integration tests use test DB + httpx ASGI client.
