"""
Backend README with setup and usage instructions.
"""

# BOT Insight Report - FastAPI Backend

A production-ready FastAPI backend for the BOT Insight Report system providing monitoring, job management, and analytics for UiPath RPA processes.

## Features

- ✅ **RESTful API** with FastAPI and async/await support
- ✅ **JWT Authentication** with access and refresh tokens
- ✅ **PostgreSQL** database with async SQLAlchemy ORM
- ✅ **Redis** caching for performance optimization
- ✅ **Elasticsearch** for logging and search capabilities
- ✅ **Background Jobs** with APScheduler for scheduled tasks
- ✅ **Structured Logging** with JSON format for production
- ✅ **Global Exception Handling** with proper HTTP status codes
- ✅ **Modular Architecture** for easy extension and maintenance
- ✅ **Health Checks** for Kubernetes integration
- ✅ **CORS Support** for frontend integration
- ✅ **Type Safety** with full type hints and Pydantic validation

## Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Elasticsearch 8+

## Installation

### 1. Clone the repository
```bash
cd backend
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Setup database
```bash
# Create database
createdb bot_insight

# Run migrations
alembic upgrade head
```

### 6. Start external services (Docker)
```bash
# Start PostgreSQL, Redis, and Elasticsearch
docker-compose up -d
```

## Running the Application

### Development Mode
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Access API Documentation
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Project Structure

```
backend/
├── app/
│   ├── core/                    # Infrastructure & utilities
│   │   ├── config.py           # Configuration management
│   │   ├── database.py         # Database setup
│   │   ├── security.py         # JWT and password utilities
│   │   ├── cache.py            # Redis client
│   │   ├── elasticsearch_client.py  # ES client
│   │   ├── scheduler.py        # Background scheduler
│   │   ├── logging_config.py   # Logging setup
│   │   ├── handlers_config.py  # Exception handlers
│   │   └── exceptions.py       # Custom exceptions
│   │
│   ├── models/                  # SQLAlchemy models
│   │   ├── base_model.py       # Base model with common fields
│   │   ├── user.py             # User model
│   │   ├── job.py              # Job model
│   │   ├── robot.py            # Robot model
│   │   ├── queue.py            # Queue model
│   │   ├── environment.py      # Environment model
│   │   ├── alert.py            # Alert model
│   │   └── ai_monitoring.py    # AI monitoring model
│   │
│   ├── schemas/                 # Pydantic schemas
│   │   └── common.py           # Common schemas
│   │
│   ├── api/                     # API layer
│   │   ├── deps.py             # Dependencies & base classes
│   │   └── v1/
│   │       ├── router.py       # Main API router
│   │       └── endpoints/
│   │           └── health.py   # Health check endpoints
│   │
│   ├── modules/                 # Feature modules
│   │   ├── auth/               # Authentication
│   │   │   ├── schemas.py      # Auth schemas
│   │   │   ├── repository.py   # User repository
│   │   │   ├── service.py      # Auth business logic
│   │   │   └── router.py       # Auth routes
│   │   ├── jobs/               # Job management
│   │   ├── queues/             # Queue management
│   │   ├── robots/             # Robot management
│   │   ├── logs/               # Log management
│   │   ├── ai_monitoring/      # AI monitoring
│   │   ├── alerts/             # Alert management
│   │   ├── dashboards/         # Dashboard data
│   │   └── orchestrator_connector/  # Orchestrator integration
│   │
│   ├── middleware/              # Middleware
│   │   └── logging.py          # Request/response logging
│   │
│   └── main.py                 # Application factory
│
├── alembic/                     # Database migrations
│   ├── versions/               # Migration scripts
│   └── env.py                  # Migration configuration
│
├── tests/                       # Test suite
│   ├── conftest.py            # Pytest configuration
│   └── test_health.py         # Health endpoint tests
│
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── Dockerfile                 # Container configuration
├── docker-compose.yml         # Docker Compose setup
├── ARCHITECTURE_GUIDE.md      # Architecture documentation
└── IMPLEMENTATION_GUIDE.md    # Implementation checklist
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/profile` - Get user profile
- `PUT /api/v1/auth/profile` - Update user profile
- `POST /api/v1/auth/change-password` - Change password

### Jobs
- `POST /api/v1/jobs` - Create job
- `GET /api/v1/jobs/{job_id}` - Get job details
- `GET /api/v1/jobs/robot/{robot_id}` - Get robot jobs
- `PUT /api/v1/jobs/{job_id}` - Update job
- `DELETE /api/v1/jobs/{job_id}` - Delete job

### Health
- `GET /health` - Full health check
- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness probe

*Additional endpoints for queues, robots, logs, alerts, etc. to be implemented*

## Database Models

All models extend `BaseModel` and include:
- `id` - Primary key
- `created_at` - Timestamp of creation
- `updated_at` - Timestamp of last update
- `created_by` - User who created the record
- `updated_by` - User who last updated the record

### Key Models

**User**
- Email and username (unique)
- Hashed password
- Profile information
- Last login timestamp

**Job**
- Name and description
- Status tracking (pending, running, completed, failed, stopped)
- Robot and environment association
- Execution metrics (duration, success/failure counts)
- Retry configuration

**Robot**
- Name and machine information
- Version and health status
- Job execution statistics
- Last heartbeat tracking

**Queue**
- Transaction queue management
- Processing metrics and rates
- Retry configuration
- Environment association

**Alert**
- Multiple severity levels (info, warning, error, critical)
- Status tracking (open, acknowledged, resolved)
- Association with jobs/robots/environments
- Metadata for detailed information

**AI Monitoring**
- Workflow metrics and confidence scores
- Execution performance tracking
- Model version tracking
- Anomaly detection data

## Configuration

### Environment Variables (.env)

```env
# Application
APP_NAME=BOT Insight Report API
DEBUG=False
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/bot_insight

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis
REDIS_URL=redis://localhost:6379/0

# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

See `.env.example` for complete configuration options.

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run with Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Run Specific Test
```bash
pytest tests/test_health.py::test_health_check_success -v
```

### Run in Watch Mode
```bash
ptw tests/
```

## Code Quality

### Format Code
```bash
black app/ tests/
```

### Lint
```bash
flake8 app/ tests/
```

### Type Checking
```bash
mypy app/
```

### Run All Quality Checks
```bash
black app/ tests/ && flake8 app/ tests/ && mypy app/
```

## Database Migrations

### Create New Migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback Last Migration
```bash
alembic downgrade -1
```

### View Migration History
```bash
alembic history
```

## Docker Support

### Build Image
```bash
docker build -t bot-insight-backend:latest -f Dockerfile .
```

### Run Container
```bash
docker run -p 8000:8000 --env-file .env bot-insight-backend:latest
```

### Docker Compose
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f backend
```

## Performance Optimization

- **Database**: Uses connection pooling in production
- **Caching**: Redis integration for frequently accessed data
- **Async**: Full async/await support for I/O operations
- **Pagination**: Default page size of 20 items
- **Indexes**: Database indexes on frequently queried fields

## Security Considerations

1. **Secrets**: Never commit `.env` file to version control
2. **JWT**: Secrets are used to sign tokens
3. **Passwords**: Hashed with bcrypt (12 rounds)
4. **CORS**: Configured to allow specified origins only
5. **HTTPS**: Required in production
6. **Rate Limiting**: Implement for production deployments

## Monitoring & Observability

- **Health Checks**: Available for Kubernetes probes
- **Structured Logging**: JSON format for easy parsing
- **Request Tracing**: Automatic X-Process-Time header
- **Error Tracking**: Global exception handlers with proper status codes

## Troubleshooting

### Database Connection Error
```
Error: could not connect to server
```
- Ensure PostgreSQL is running
- Check DATABASE_URL format
- Verify credentials

### Redis Connection Error
```
Error: ConnectionError: Error -2 connecting
```
- Ensure Redis is running on correct port
- Check REDIS_URL configuration

### Elasticsearch Connection Error
```
Error: ConnectionError: Unable to connect
```
- Ensure Elasticsearch is running
- Check host and port configuration
- Verify authentication if required

### JWT Token Invalid
```
Error: Invalid token
```
- Check token format (should start with "Bearer ")
- Verify SECRET_KEY matches
- Check token expiration

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Run quality checks
5. Submit a pull request

## Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes and test
pytest tests/ -v

# 3. Format and lint
black app/ tests/
flake8 app/ tests/
mypy app/

# 4. Create migration if needed
alembic revision --autogenerate -m "Description"

# 5. Commit and push
git add .
git commit -m "feat: Add my feature"
git push origin feature/my-feature
```

## Deployment

### Production Checklist
- [ ] Set DEBUG=False
- [ ] Use strong SECRET_KEY
- [ ] Setup HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Setup database backups
- [ ] Setup monitoring and alerting
- [ ] Configure log aggregation
- [ ] Test health checks
- [ ] Load test the application
- [ ] Security audit
- [ ] Documentation updated

### Production Environment Variables
```env
DEBUG=False
ENVIRONMENT=production
SQLALCHEMY_ECHO=False
LOG_LEVEL=WARNING
CORS_ORIGINS=["https://yourdomain.com"]
```

## Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async Guide](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Redis Python Client](https://github.com/redis/redis-py)
- [Elasticsearch Python Client](https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/index.html)
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)

## License

Proprietary - UiPath BOT Insight Report

## Support

For issues and questions, please contact the development team.

## Changelog

### v1.0.0 (Current)
- Initial release with core infrastructure
- Authentication module with JWT
- Jobs module for job management
- Health check endpoints
- Documentation and implementation guide
