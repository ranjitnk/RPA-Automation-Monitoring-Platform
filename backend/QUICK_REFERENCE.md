"""
Quick Reference Guide for FastAPI Backend
"""

# 🚀 QUICK REFERENCE GUIDE

## Immediate Next Steps

### 1. Get Started (5 minutes)
```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
# Visit http://localhost:8000/api/docs
```

### 2. Test Endpoints
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@test.com","password":"Demo123456","full_name":"Demo User"}'

# Login  
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@test.com","password":"Demo123456"}'

# Check Health
curl http://localhost:8000/health
```

### 3. Create New Module

Follow the template in `IMPLEMENTATION_GUIDE.md` or:

```bash
# 1. Create model in app/models/module_name.py
# 2. Create schemas in app/modules/module_name/schemas.py
# 3. Create repository in app/modules/module_name/repository.py
# 4. Create service in app/modules/module_name/service.py
# 5. Create router in app/modules/module_name/router.py
# 6. Register in app/api/v1/router.py
```

## Key Files Location

| Feature | File | Location |
|---------|------|----------|
| Configuration | config.py | `app/core/` |
| Database | database.py | `app/core/` |
| JWT & Password | security.py | `app/core/` |
| Redis Cache | cache.py | `app/core/` |
| Elasticsearch | elasticsearch_client.py | `app/core/` |
| Scheduler | scheduler.py | `app/core/` |
| Logging | logging_config.py | `app/core/` |
| Exceptions | exceptions.py | `app/core/` |
| Models | *.py | `app/models/` |
| Schemas | common.py | `app/schemas/` |
| Dependencies | deps.py | `app/api/` |
| Main Router | router.py | `app/api/v1/` |
| Health Endpoint | health.py | `app/api/v1/endpoints/` |
| Auth Module | auth/ | `app/modules/` |
| Jobs Module | jobs/ | `app/modules/` |

## Common Commands

```bash
# Run application
uvicorn app.main:app --reload

# Run tests
pytest tests/ -v

# Code formatting
black app/ tests/

# Linting
flake8 app/ tests/

# Type checking
mypy app/

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1

# Install dependencies
pip install -r requirements.txt

# Generate requirements
pip freeze > requirements.txt
```

## Architecture Layers

```
HTTP Requests
    ↓
Middleware (CORS, Logging, Errors)
    ↓
API Layer (FastAPI Routers)
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (Data Access)
    ↓
Infrastructure (DB, Cache, Search, Scheduler)
```

## Authentication Flow

```
1. Register → POST /auth/register → Create user
2. Login → POST /auth/login → Get access token
3. Request → Add header: Authorization: Bearer <token>
4. Validate → Token decoded in dependency
5. Execute → Endpoint receives validated user_id
```

## Database Layer Pattern

```python
# 1. Query with SQLAlchemy
query = select(User).where(User.email == email)
result = await db.execute(query)
user = result.scalars().first()

# 2. Add new record
user = User(email=email, hashed_password=hash)
db.add(user)
await db.flush()

# 3. Update record
user.is_active = False
await db.flush()

# 4. Commit transaction
await db.commit()

# 5. Delete record
await db.delete(user)
await db.commit()
```

## Service Layer Pattern

```python
async def service_method(self, data: InputSchema) -> OutputSchema:
    # 1. Validate input (Pydantic handles this)
    # 2. Call repository for data operations
    item = await self.repo.create_item(data.model_dump())
    # 3. Perform business logic
    # 4. Cache if needed
    await cache_set(key, item)
    # 5. Return response schema
    return OutputSchema.model_validate(item)
```

## API Response Pattern

```python
# Success
return SuccessResponseSchema(
    data=item_schema,
    message="Item created successfully"
)

# Error (Auto-handled)
raise ResourceNotFoundError("Item", item_id)
# → 404 with error details

# List
return SuccessResponseSchema(data=items_list)

# Paginated
return PaginatedResponseSchema(
    data=items,
    total=total_count,
    page=page_num,
    page_size=page_size,
    total_pages=total_pages
)
```

## Dependency Injection Pattern

```python
# Use in endpoints
async def endpoint(
    db: AsyncSession = Depends(get_db),
    user_id: str = Header(Depends(get_current_user_id)),
    config = Depends(get_config),
    redis = Depends(get_redis),
):
    service = MyService(db)
    return await service.do_something(user_id)
```

## Exception Hierarchy

```
AppException (base - 500)
├── ValidationError (422)
├── AuthenticationError (401)
├── AuthorizationError (403)
├── ResourceNotFoundError (404)
├── DuplicateResourceError (409)
├── DatabaseError (500)
├── ExternalServiceError (502)
├── CacheError (500)
├── ConfigurationError (500)
└── RateLimitError (429)
```

## Caching Pattern

```python
# Get from cache
cached = await cache_get("key")

# Set to cache
await cache_set("key", "value", ttl=3600)

# Namespaced key
key = make_cache_key("user", user_id, "profile")

# JSON support
await cache_set_json(key, pydantic_model)
data = await cache_get_json(key, PydanticModel)

# Pattern deletion
await cache_delete_pattern("user:*:profile")
```

## Logging Pattern

```python
from app.core.logging_config import get_logger

logger = get_logger(__name__)

logger.info("Message", extra={
    "field": "value",
    "user_id": user_id
})

logger.error("Error occurred", exc_info=exc, extra={
    "component": "auth"
})
```

## Scheduler Pattern

```python
from app.core.scheduler import add_interval_job, add_cron_job

async def my_task():
    # Do something
    pass

# Run every 5 minutes
add_interval_job(my_task, minutes=5, id="my_task_id")

# Run at 9 AM on weekdays
add_cron_job(my_task, "0 9 * * MON-FRI", id="weekday_task")

# Get all jobs
jobs = get_jobs()

# Pause/resume
pause_job("my_task_id")
resume_job("my_task_id")

# Remove
remove_job("my_task_id")
```

## Configuration Usage

```python
from app.core.config import get_settings

settings = get_settings()

# Access settings
db_url = settings.DATABASE_URL
jwt_secret = settings.SECRET_KEY
redis_url = settings.REDIS_URL
log_level = settings.LOG_LEVEL
```

## Health Check Format

```json
{
  "status": "healthy",
  "timestamp": "2025-05-23T10:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "elasticsearch": "degraded"
  }
}
```

## Environment Configuration

### Development
```env
DEBUG=True
ENVIRONMENT=development
SQLALCHEMY_ECHO=True
LOG_LEVEL=DEBUG
```

### Production
```env
DEBUG=False
ENVIRONMENT=production
SQLALCHEMY_ECHO=False
LOG_LEVEL=WARNING
CORS_ORIGINS=["https://domain.com"]
```

## Documentation Files

1. **README.md** - Installation, running, API overview
2. **ARCHITECTURE_GUIDE.md** - Design patterns, layers, features
3. **IMPLEMENTATION_GUIDE.md** - Checklist, module template, next steps
4. **COMPLETE_SUMMARY.md** - Full summary of what's built
5. **This File** - Quick reference guide

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Database connection failed | Check DATABASE_URL, ensure PostgreSQL running |
| Redis error | Check REDIS_URL, ensure Redis running |
| JWT invalid | Verify SECRET_KEY, check token format |
| CORS error | Check CORS_ORIGINS in .env |
| Module not found | Check __init__.py files exist in each package |
| Alembic error | Ensure models inherit from BaseModel, Base |

## File Structure Checklist

```
✅ backend/
   ✅ app/
      ✅ core/ (config, db, security, cache, ES, scheduler, logging, handlers, exceptions)
      ✅ models/ (user, job, robot, queue, environment, alert, ai_monitoring)
      ✅ schemas/ (common schemas)
      ✅ api/ (deps.py, v1/router.py, v1/endpoints/health.py)
      ✅ modules/ (auth, jobs structure ready)
      ✅ middleware/ (logging middleware)
      ✅ main.py (app factory)
   ✅ alembic/ (migrations)
   ✅ tests/ (test structure)
   ✅ requirements.txt
   ✅ .env.example
   ✅ README.md
   ✅ ARCHITECTURE_GUIDE.md
   ✅ IMPLEMENTATION_GUIDE.md
   ✅ COMPLETE_SUMMARY.md
```

## Performance Tips

- Use pagination for large results
- Implement caching for read-heavy operations
- Add database indexes on frequently queried fields
- Use connection pooling
- Monitor query performance
- Implement rate limiting
- Use async/await properly
- Batch operations when possible

## Security Tips

- Never commit .env file
- Use environment variables for secrets
- Implement HTTPS in production
- Validate all inputs
- Use parameterized queries (SQLAlchemy handles this)
- Implement rate limiting
- Add security headers
- Regular security audits

---

For more details, see the comprehensive documentation files.
