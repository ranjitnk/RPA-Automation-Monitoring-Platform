# API module separation

Base path: `/api/v1`

## Router registration (`app/api/v1/router.py`)

| Prefix | Module | Tag |
|--------|--------|-----|
| `/auth` | `auth.py` | Authentication |
| `/users` | `users.py` | Users |
| `/roles` | `roles.py` | RBAC |
| `/environments` | `environments.py` | Multi-environment |
| `/orchestrator` | `orchestrator.py` | Orchestrator metadata sync |
| `/queues` | `queues.py` | Queue monitoring |
| `/jobs` | `jobs.py` | Job monitoring |
| `/robots` | `robots.py` | Robot monitoring |
| `/ai-workflows` | `ai_workflows.py` | AI/agentic monitoring |
| `/dashboards` | `dashboards.py` | KPIs & widgets |
| `/sla` | `sla.py` | SLA rules & alerts |
| `/audit` | `audit.py` | Audit log queries |
| `/realtime` | `realtime.py` | WebSocket upgrade |
| `/health` | `health.py` | Liveness/readiness |

## Versioning

- URL versioning: `/api/v1/...`
- Breaking changes → `app/api/v2/`
- Deprecation headers: `Sunset`, `Link`

## Common dependencies (`app/api/deps.py`)

```python
get_db()              # AsyncSession
get_current_user()    # JWT → User
require_permission()  # RBAC factory
get_environment()     # X-Environment-Id validation
```

## Example route flow

```
POST /api/v1/sla/rules
  → deps: auth + permission("sla:write") + environment
  → schema: SLARuleCreate
  → service: SLAService.create_rule()
  → audit: AuditService.log(...)
  → response: SLARuleResponse
```

## WebSocket

`WS /api/v1/realtime/ws?token=...&environment_id=...`

Topics: `jobs`, `queues`, `robots`, `alerts`

## OpenAPI

- Tags mirror modules above.
- Group external vs internal routes via `include_in_schema` for admin-only endpoints.
