"""
Comprehensive documentation for the FastAPI Backend Architecture.
"""

# Backend Architecture Documentation

## Project Overview

This is a production-ready FastAPI backend for the BOT Insight Report system. It provides:
- RESTful API with async support
- JWT authentication & authorization
- PostgreSQL database with SQLAlchemy ORM
- Redis caching layer
- Elasticsearch for logging and searching
- Background job scheduling
- Global exception handling
- Structured logging

## Architecture Layers

### 1. **Core Layer** (`app/core/`)
Infrastructure and utilities:
- `config.py` - Environment-based configuration using Pydantic
- `database.py` - SQLAlchemy async engine and session management
- `security.py` - JWT token generation/validation and password hashing
- `cache.py` - Redis client with async operations
- `elasticsearch_client.py` - Elasticsearch connection and operations
- `scheduler.py` - APScheduler for background tasks
- `logging_config.py` - Structured logging setup
- `handlers_config.py` - Global exception handlers
- `exceptions.py` - Custom exception classes

### 2. **Models Layer** (`app/models/`)
SQLAlchemy ORM models:
- `base_model.py` - Base model with common fields (id, created_at, updated_at, etc.)
- `user.py` - User model for authentication
- `job.py` - Job/process execution tracking
- `robot.py` - RPA robot agents
- `queue.py` - Transaction queues
- `environment.py` - Deployment environments
- `alert.py` - System alerts
- `ai_monitoring.py` - AI workflow metrics

### 3. **Schemas Layer** (`app/schemas/`)
Pydantic models for request/response validation:
- `common.py` - Base schemas and common patterns

### 4. **API Layer** (`app/api/`)
HTTP endpoints and routing:
- `deps.py` - Dependency injection and base classes
- `v1/router.py` - Main API router
- `v1/endpoints/health.py` - Health check endpoints

### 5. **Modules Layer** (`app/modules/`)
Feature modules with MVC pattern:

Each module contains:
- `schemas.py` - Pydantic schemas for the module
- `models.py` - SQLAlchemy models (in app/models/)
- `repository.py` - Database access layer (CRUD operations)
- `service.py` - Business logic layer
- `router.py` - API endpoints

#### Modules:
- **auth** - User registration, login, profile management
- **jobs** - Job/process execution tracking
- **queues** - Transaction queue management
- **robots** - Robot/agent management
- **logs** - Log aggregation and searching
- **ai_monitoring** - AI workflow metrics
- **alerts** - Alert management
- **dashboards** - Dashboard data aggregation
- **orchestrator_connector** - UiPath Orchestrator integration

## Design Patterns

### 1. **Dependency Injection**
```python
async def endpoint(db: AsyncSession = Depends(get_db)) -> Response:
    service = MyService(db)
    return await service.do_something()
```

### 2. **Repository Pattern**
- Abstracts database access
- Enables testing and switching databases
- CRUD operations centralized

### 3. **Service Pattern**
- Contains business logic
- Uses repositories for data access
- Handles validation and exceptions

### 4. **Schema Pattern**
- Pydantic models for validation
- Separate request (Input) and response (Output) schemas
- Type safety and automatic OpenAPI documentation

## API Response Format

### Success Response
```json
{
  "status": "success",
  "data": {...},
  "message": "Optional message"
}
```

### Error Response
```json
{
  "status": "error",
  "error_code": "ERROR_CODE",
  "message": "Human readable message",
  "details": {}
}
```

## Authentication

JWT-based authentication with access and refresh tokens:
- Access token: 30 minutes expiration
- Refresh token: 7 days expiration
- Token in Authorization header: `Bearer <token>`

### Protected Routes
```python
async def protected_endpoint(authorization: str = Header(None)):
    user_id = await get_current_user_id(authorization)
```

## Database

### Async Support
- Uses SQLAlchemy async engine
- AsyncSession for queries
- Connection pooling for production

### Migrations
- Alembic for database versioning
- Automatic migration tracking

### Models
- All models inherit from `BaseModel`
- Common fields: id, created_at, updated_at, created_by, updated_by

## Caching

### Redis
- Async Redis client
- Namespaced keys: `module:action:identifier`
- Configurable TTL

### Usage
```python
from app.core.cache import cache_set, cache_get, make_cache_key

key = make_cache_key("user", str(user_id), "profile")
await cache_set(key, user_data, ttl=3600)
cached = await cache_get(key)
```

## Logging

### Structured Logging
- JSON format for production
- Text format for development
- Console and file output
- Automatic context addition

## Background Tasks

### APScheduler
- Async support
- Cron and interval triggers
- Job persistence

### Usage
```python
from app.core.scheduler import add_interval_job, add_cron_job

async def task():
    pass

add_interval_job(task, minutes=5, id="my_task")
add_cron_job(task, "0 9 * * MON-FRI", id="weekday_task")
```

## Error Handling

### Exception Hierarchy
```
AppException (base)
├── ValidationError
├── AuthenticationError
├── AuthorizationError
├── ResourceNotFoundError
├── DuplicateResourceError
├── DatabaseError
├── ExternalServiceError
├── CacheError
├── ConfigurationError
└── RateLimitError
```

### Global Exception Handlers
- AppException → Custom response with status code
- RequestValidationError → 422 with field details
- Generic Exception → 500 with safe message

## Configuration

### Environment-Based
- Development, staging, production
- Separate configurations via .env file
- Settings validation with Pydantic

### Key Settings
- Database URL and echo
- Redis URL and TTL
- Elasticsearch configuration
- Scheduler timezone
- CORS origins
- Logging level and format

## Health Checks

### Endpoints
- `/health` - Full health check with service status
- `/health/live` - Liveness probe (Kubernetes)
- `/health/ready` - Readiness probe (Kubernetes)

### Checked Services
- Database
- Redis
- Elasticsearch

## Testing

### Structure
```
tests/
├── conftest.py          # Pytest fixtures
├── test_health.py       # Health endpoint tests
└── modules/
    ├── test_auth.py
    ├── test_jobs.py
    └── ...
```

### Fixtures
- Database session
- Redis client
- HTTP client

## Deployment

### Docker
- Dockerfile for containerization
- Multi-stage builds for optimization
- Health check configuration

### Production Settings
- DEBUG = False
- Connection pooling enabled
- Structured JSON logging
- HTTPS only
- Secure CORS configuration

## Getting Started

### 1. Setup Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Setup
```bash
alembic upgrade head
```

### 4. Run Application
```bash
uvicorn app.main:app --reload
```

### 5. Access API
- API docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Project Structure Summary

```
backend/
├── app/
│   ├── core/              # Infrastructure layer
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── api/
│   │   ├── v1/           # API v1
│   │   └── deps.py       # Dependencies
│   ├── modules/           # Feature modules
│   │   ├── auth/
│   │   ├── jobs/
│   │   └── ...
│   ├── middleware/        # Middleware
│   └── main.py           # App factory
├── alembic/              # Database migrations
├── tests/                # Test suite
├── requirements.txt      # Dependencies
├── .env.example          # Configuration template
└── Dockerfile            # Containerization
```

## Key Features

✅ **Modular Architecture** - Easy to extend with new modules  
✅ **Async Support** - Non-blocking I/O throughout  
✅ **Type Safety** - Full type hints and Pydantic validation  
✅ **Exception Handling** - Global error handling with proper HTTP status codes  
✅ **Logging** - Structured JSON logging for monitoring  
✅ **Authentication** - JWT-based with refresh tokens  
✅ **Caching** - Redis integration for performance  
✅ **Search** - Elasticsearch for logging and search  
✅ **Scheduling** - Background tasks with APScheduler  
✅ **Database** - Async SQLAlchemy with migrations  
✅ **Documentation** - Auto-generated OpenAPI/Swagger  
✅ **Testing Ready** - Pytest fixtures and patterns  
✅ **Production Ready** - CORS, health checks, monitoring  

## Next Steps

1. **Implement remaining modules** (queues, robots, logs, etc.)
2. **Add authentication middleware** for protected routes
3. **Setup CI/CD** for automated testing and deployment
4. **Add monitoring** (Prometheus, OpenTelemetry)
5. **Performance testing** and optimization
6. **Security hardening** (rate limiting, input validation)
7. **Documentation** (API docs, architecture)
