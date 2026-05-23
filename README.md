# UiPath Automation Monitoring Platform

Enterprise-grade full-stack platform for monitoring UiPath Orchestrator workloads, queues, jobs, robots, and AI/agentic workflows with real-time dashboards, SLA alerting, multi-environment support, RBAC, and audit logging.

## Quick start

```bash
# Copy environment templates
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Start infrastructure + apps
docker compose up -d

# Backend (local dev)
cd backend && pip install -r requirements/dev.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend (local dev)
cd frontend && npm install && npm run dev
```

## Documentation

| Document | Description |
|----------|-------------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, data flows, module boundaries |
| [docs/PACKAGES.md](docs/PACKAGES.md) | Recommended dependencies |
| [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md) | Environment variable strategy |
| [docs/API_MODULES.md](docs/API_MODULES.md) | API route organization |
| [docs/SERVICES.md](docs/SERVICES.md) | Service layer patterns |

## Repository layout

```
├── backend/          # FastAPI application
├── frontend/         # React + Vite + MUI + AG Grid
├── docker/           # Compose overrides, init scripts
├── docs/             # Architecture & runbooks
├── infra/            # IaC placeholders (Terraform/K8s)
└── docker-compose.yml
```

## License

Proprietary — internal use.
