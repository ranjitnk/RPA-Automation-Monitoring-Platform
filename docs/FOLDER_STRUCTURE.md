# Folder structure

```
BOT Insight Report/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── docker-compose.prod.yml
├── README.md
│
├── docker/
│   ├── nginx/nginx.conf              # Root reverse proxy (prod)
│   └── postgres/init/                # DB extensions on first boot
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API_MODULES.md
│   ├── ENVIRONMENT.md
│   ├── FOLDER_STRUCTURE.md
│   ├── PACKAGES.md
│   └── SERVICES.md
│
├── infra/
│   ├── k8s/README.md
│   └── terraform/README.md
│
├── backend/
│   ├── Dockerfile
│   ├── .env.example
│   ├── alembic.ini
│   ├── pyproject.toml
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── requirements/
│   │   ├── base.txt
│   │   └── dev.txt
│   ├── tests/
│   └── app/
│       ├── main.py
│       ├── api/
│       │   ├── deps.py
│       │   └── v1/
│       │       ├── router.py
│       │       ├── auth.py
│       │       ├── environments.py
│       │       ├── queues.py | jobs.py | robots.py
│       │       ├── ai_workflows.py
│       │       ├── dashboards.py | sla.py | audit.py
│       │       ├── realtime.py
│       │       └── health.py
│       ├── core/
│       │   ├── config.py
│       │   ├── database.py
│       │   ├── security.py
│       │   ├── logging.py
│       │   └── exceptions.py
│       ├── models/
│       ├── schemas/
│       ├── services/
│       ├── repositories/
│       ├── integrations/
│       │   ├── uipath/
│       │   └── elasticsearch/
│       └── workers/
│           ├── celery_app.py
│           └── tasks/
│
└── frontend/
    ├── Dockerfile
    ├── .env.example
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── api/
        ├── components/
        │   ├── layout/
        │   └── grid/
        ├── features/
        │   ├── auth/
        │   ├── dashboard/
        │   ├── queues/
        │   ├── jobs/
        │   ├── robots/
        │   ├── ai-workflows/
        │   ├── sla/
        │   ├── audit/
        │   └── environments/
        ├── routes/
        ├── stores/
        └── theme/
```
