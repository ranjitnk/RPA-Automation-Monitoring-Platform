# Production FastAPI Backend

## Folder structure

```
backend/
├── alembic/                    # Database migrations
│   └── versions/
├── app/
│   ├── main.py                 # App factory + lifespan
│   ├── api/
│   │   ├── deps.py             # Dependency injection providers
│   │   └── v1/
│   │       ├── router.py       # Route aggregation
│   │       └── health.py       # Liveness / readiness
│   ├── core/
│   │   ├── config.py           # Environment settings
│   │   ├── database.py         # Async SQLAlchemy
│   │   ├── security.py         # JWT + passwords
│   │   ├── cache.py            # Redis
│   │   ├── elasticsearch_client.py
│   │   ├── scheduler.py        # APScheduler
│   │   ├── exceptions.py
│   │   ├── handlers.py         # Global exception handlers
│   │   └── logging.py
│   ├── middleware/
│   │   └── logging.py          # Request logging + correlation ID
│   ├── models/                 # SQLAlchemy ORM (shared)
│   ├── schemas/                # Shared Pydantic schemas
│   └── modules/                # Domain modules
│       ├── auth/               # router, service, repository, schemas
│       ├── jobs/
│       ├── queues/
│       ├── robots/
│       ├── logs/
│       ├── ai_monitoring/
│       ├── alerts/
│       ├── dashboards/
│       └── orchestrator_connector/
├── requirements/
├── tests/
└── scripts/
```

## Dependency injection

FastAPI `Depends()` wires layers in `app/api/deps.py`:

```python
def get_job_service(db: AsyncSession = Depends(get_db)) -> JobService:
    return JobService(JobRepository(db))
```

Routes depend on **services**; services depend on **repositories**; repositories use **AsyncSession**.

## API map

| Prefix | Module |
|--------|--------|
| `/api/v1/health/live` | Liveness |
| `/api/v1/health/ready` | Readiness (DB, Redis, ES) |
| `/api/v1/auth/*` | Register, login, refresh, me |
| `/api/v1/jobs` | Job list/create (scoped by `X-Environment-Id`) |
| `/api/v1/queues` | Queue list |
| `/api/v1/robots` | Robot list |
| `/api/v1/logs/search` | Elasticsearch log search |
| `/api/v1/ai-monitoring/runs` | AI workflow runs |
| `/api/v1/alerts` | Alerts + rules |
| `/api/v1/dashboards/summary` | Cached KPI summary |
| `/api/v1/orchestrator/environments` | Connector CRUD + sync |

## Run locally

```bash
cd backend
pip install -r requirements/dev.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```
