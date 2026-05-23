# Recommended packages

## Backend (Python 3.12+)

### Core
| Package | Purpose |
|---------|---------|
| `fastapi` | Async API framework |
| `uvicorn[standard]` | ASGI server |
| `gunicorn` | Production process manager |
| `pydantic-settings` | Typed settings from env |
| `sqlalchemy[asyncio]` | Async ORM |
| `asyncpg` | PostgreSQL async driver |
| `alembic` | Migrations |
| `httpx` | Async HTTP client (Orchestrator) |
| `tenacity` | Retries with backoff |
| `python-jose[cryptography]` | JWT |
| `passlib[bcrypt]` | Password hashing |
| `cryptography` | Credential encryption |

### Workers & realtime
| Package | Purpose |
|---------|---------|
| `celery[redis]` | Task queue |
| `redis` | Cache, broker, pub/sub |
| `websockets` | WS protocol support |

### Observability
| Package | Purpose |
|---------|---------|
| `structlog` | Structured logging |
| `python-json-logger` | JSON log format |
| `elastic-transport` + `elasticsearch[async]` | ES client (v8) |
| `opentelemetry-api` | Tracing hooks (optional) |
| `prometheus-fastapi-instrumentator` | Metrics endpoint |

### Quality
| Package | Purpose |
|---------|---------|
| `pytest`, `pytest-asyncio`, `httpx` | Tests |
| `ruff` | Lint + format |
| `mypy` | Type checking |

See `backend/requirements/base.txt` for pinned versions.

## Frontend (Node 20+)

### Core
| Package | Purpose |
|---------|---------|
| `react`, `react-dom` | UI |
| `vite` | Build tool |
| `@vitejs/plugin-react` | React plugin |
| `typescript` | Type safety |
| `react-router-dom` | Routing |

### UI & data
| Package | Purpose |
|---------|---------|
| `@mui/material`, `@mui/icons-material` | Components |
| `@emotion/react`, `@emotion/styled` | MUI styling |
| `ag-grid-community`, `ag-grid-react` | Data grids |
| `@tanstack/react-query` | Server state |
| `zustand` | Client UI state |
| `axios` | HTTP client |
| `date-fns` | Date formatting |
| `recharts` | Dashboard charts |

### Auth & realtime
| Package | Purpose |
|---------|---------|
| `jwt-decode` | Parse token claims |
| `socket.io-client` or native `WebSocket` | Realtime |

### Dev quality
| Package | Purpose |
|---------|---------|
| `eslint`, `@typescript-eslint/*` | Lint |
| `prettier` | Format |
| `vitest`, `@testing-library/react` | Unit tests |

See `frontend/package.json`.
