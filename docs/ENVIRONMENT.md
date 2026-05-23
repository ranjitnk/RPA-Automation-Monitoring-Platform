# Environment variable strategy

## Principles

1. **Layered config:** defaults in code → `.env` (local) → deployment secrets (Docker/K8s).
2. **Never commit secrets:** only `.env.example` files in git.
3. **Prefix namespaces:** `APP_`, `DB_`, `REDIS_`, `ES_`, `JWT_`, `ORCH_` (defaults), `CELERY_`.
4. **Single settings object:** `app.core.config.Settings` loads once at startup.
5. **Environment-specific files:** optional `.env.development`, `.env.staging` (gitignored).

## File layout

```
.env.example              # Root: compose + shared URLs
backend/.env.example      # Backend-only secrets & tuning
frontend/.env.example     # VITE_* public vars only
```

## Variable categories

### Application
| Variable | Description |
|----------|-------------|
| `APP_ENV` | `development` \| `staging` \| `production` |
| `APP_DEBUG` | Enable OpenAPI docs, verbose errors |
| `APP_NAME` | Service name for logs |
| `APP_LOG_LEVEL` | `DEBUG` … `CRITICAL` |
| `APP_CORS_ORIGINS` | Comma-separated allowed origins |

### Database
| Variable | Description |
|----------|-------------|
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | PostgreSQL |
| `DATABASE_URL` | Optional full DSN override |

### Redis & workers
| Variable | Description |
|----------|-------------|
| `REDIS_URL` | Cache + pub/sub |
| `CELERY_BROKER_URL` | Usually same as Redis |
| `CELERY_RESULT_BACKEND` | Result store |

### JWT & security
| Variable | Description |
|----------|-------------|
| `JWT_SECRET_KEY` | Signing key (min 32 bytes) |
| `JWT_ALGORITHM` | Default `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Short-lived access |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL |
| `CREDENTIALS_ENCRYPTION_KEY` | Fernet key for Orchestrator secrets |

### Elasticsearch
| Variable | Description |
|----------|-------------|
| `ES_ENABLED` | Toggle shipping logs to ES |
| `ES_URL` | Cluster URL |
| `ES_USERNAME`, `ES_PASSWORD` | Basic auth (if used) |
| `ES_INDEX_PREFIX` | e.g. `uipath-monitor` |

### UiPath Orchestrator (platform defaults)
Per-environment values are stored in DB; these are optional fallbacks for dev:

| Variable | Description |
|----------|-------------|
| `ORCH_DEFAULT_URL` | Dev Orchestrator URL |
| `ORCH_CLIENT_ID`, `ORCH_CLIENT_SECRET` | OAuth (cloud) |
| `ORCH_SYNC_INTERVAL_SECONDS` | Polling interval |

### Frontend (`VITE_` only — exposed to browser)
| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | Backend REST base |
| `VITE_WS_URL` | WebSocket URL |
| `VITE_APP_TITLE` | Browser title |

## Docker Compose

- Root `.env` consumed by `docker-compose.yml` via `${VAR}` substitution.
- Backend service mounts `backend/.env` or uses `env_file` directive.
- Production: inject via Docker secrets / K8s `Secret` + `ConfigMap`.

## Validation

`Settings` uses Pydantic validators:
- Fail fast on missing `JWT_SECRET_KEY` in production.
- Warn if `APP_DEBUG=true` when `APP_ENV=production`.
