# Docker Deployment Quick Reference

## Development Deployment

### Quick Start (5 minutes)

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Start all services
docker-compose up -d

# 3. Wait for services to be healthy
sleep 10
docker-compose ps

# 4. Access applications
echo "Frontend: http://localhost"
echo "Backend API: http://localhost:8000/api/v1"
echo "API Docs: http://localhost:8000/docs"
echo "Kibana: http://localhost:5601"
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f nginx

# Last 100 lines
docker-compose logs --tail 100 backend
```

### Stop & Clean

```bash
# Stop services (preserve data)
docker-compose down

# Full reset (delete volumes)
docker-compose down -v

# Remove specific service
docker-compose stop backend
docker-compose rm backend
```

---

## Production Deployment

### Pre-Deployment Checklist

```bash
# 1. Verify Docker installation
docker --version
docker-compose --version

# 2. Check system requirements
free -h                 # Memory
df -h                   # Disk space
nproc                   # CPU cores (should be 8+)

# 3. Create production environment
cp .env.example .env.prod
# Edit .env.prod with production values
vim .env.prod

# 4. Generate secrets
python3 -c "import secrets; print('JWT_SECRET='+secrets.token_urlsafe(32))"
python3 -c "import secrets; print('POSTGRES_PASSWORD='+secrets.token_urlsafe(32))"
python3 -c "import secrets; print('REDIS_PASSWORD='+secrets.token_urlsafe(32))"
openssl rand -base64 32  # ELASTIC_PASSWORD
openssl rand -base64 32  # KIBANA_ENCRYPTION_KEY

# 5. Copy SSL certificates
mkdir -p docker/nginx/ssl
cp /path/to/cert.pem docker/nginx/ssl/
cp /path/to/key.pem docker/nginx/ssl/
chmod 600 docker/nginx/ssl/key.pem
```

### Deploy Production

```bash
# 1. Build images (optional, uses pre-built if available)
docker-compose build

# 2. Start all services with production config
docker-compose \
  --env-file .env.prod \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  up -d

# 3. Wait for all services to be healthy
sleep 30
docker-compose \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  ps

# 4. Run database migrations
docker-compose exec backend alembic upgrade head

# 5. Seed initial data (optional)
docker-compose exec backend python scripts/seed_admin.py

# 6. Verify services
curl https://yourdomain.com                  # Frontend
curl https://yourdomain.com/api/v1/health    # Backend
```

### Ongoing Operations

```bash
# View production logs
docker-compose \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  logs -f

# Backup database (daily)
docker-compose exec -T postgres pg_dump -U postgres observability_db | \
  gzip > "/backups/db_$(date +%Y%m%d_%H%M%S).sql.gz"

# Restart service
docker-compose \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  restart backend

# Update service (minimal downtime)
docker-compose \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  up -d backend  # Restart backend with health checks
```

---

## Health Check Commands

### Service Status

```bash
# Quick status check
docker-compose ps

# Detailed health info
docker inspect $(docker-compose ps -q backend) | jq '.[] | .State.Health'

# Health check logs
docker inspect $(docker-compose ps -q postgres) | jq '.[] | .State.HealthChecks'
```

### Endpoint Verification

```bash
# Frontend
curl -I http://localhost/

# Backend API
curl http://localhost:8000/api/v1/health

# Database
docker-compose exec postgres psql -U postgres -c "SELECT 1"

# Redis
docker-compose exec redis redis-cli ping

# Elasticsearch
curl http://localhost:9200/_cluster/health | jq .

# Kibana
curl http://localhost:5601/api/status | jq .
```

---

## Common Troubleshooting

### Services Won't Start

```bash
# Check specific service logs
docker-compose logs postgres

# Check for port conflicts
lsof -i :8000

# Check Docker daemon
sudo systemctl status docker

# Restart Docker daemon
sudo systemctl restart docker
docker-compose up -d
```

### High Memory Usage

```bash
# Check memory per container
docker stats

# Reduce Elasticsearch heap
ELASTICSEARCH_HEAP_SIZE=1g docker-compose up -d elasticsearch

# Reduce Redis memory
REDIS_MAX_MEMORY=512mb docker-compose up -d redis
```

### Database Connection Errors

```bash
# Check database logs
docker-compose logs postgres

# Verify database is running
docker-compose exec postgres pg_isready

# Check database user credentials
docker-compose exec postgres psql -U postgres -l
```

### Slow Performance

```bash
# Check system resources
docker stats

# Check slow queries (if enabled)
docker-compose logs backend | grep slow

# Check Nginx cache hit rate
docker-compose logs nginx | grep "X-Cache-Status"

# View database query stats
docker-compose exec postgres psql -U postgres -d observability_db \
  -c "SELECT query, calls, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10"
```

---

## Volume Management

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect observability_postgres_data

# Backup volume
docker run --rm -v observability_postgres_data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/postgres_backup.tar.gz -C /data .

# Restore volume
docker volume create observability_postgres_data_new
docker run --rm -v observability_postgres_data_new:/data -v $(pwd):/backup \
  ubuntu tar xzf /backup/postgres_backup.tar.gz -C /data

# Remove unused volumes
docker volume prune
```

---

## Network Commands

```bash
# Inspect Docker network
docker network inspect observability_network

# Test connectivity between containers
docker-compose exec backend ping postgres
docker-compose exec backend ping redis

# Check open ports
docker-compose port nginx
docker-compose port backend
```

---

## Database Operations

### Backup

```bash
# Full database backup
docker-compose exec -T postgres pg_dump -U postgres observability_db > backup.sql

# Compressed backup
docker-compose exec -T postgres pg_dump -U postgres observability_db | gzip > backup.sql.gz

# Backup specific table
docker-compose exec -T postgres pg_dump -U postgres -t jobs observability_db > jobs_backup.sql
```

### Restore

```bash
# Restore from backup
gunzip < backup.sql.gz | docker-compose exec -T postgres psql -U postgres -d observability_db

# Full database restore (creates new database)
docker-compose exec postgres createdb -U postgres observability_db_restored
gunzip < backup.sql.gz | docker-compose exec -T postgres psql -U postgres -d observability_db_restored
```

### Maintenance

```bash
# Vacuum (reclaim disk space)
docker-compose exec postgres psql -U postgres -d observability_db -c "VACUUM ANALYZE"

# Analyze query performance
docker-compose exec postgres psql -U postgres -d observability_db -c "ANALYZE"

# Check database size
docker-compose exec postgres psql -U postgres -d observability_db -c "SELECT pg_size_pretty(pg_database_size('observability_db'))"
```

---

## Scaling & Load Testing

### Scale Services

```bash
# Start multiple backend instances (if load balancer configured)
docker-compose up -d --scale backend=3

# Note: Current setup uses single backend, scale at Kubernetes level
```

### Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Simple load test
ab -n 1000 -c 10 http://localhost/

# API endpoint load test
ab -n 1000 -c 10 http://localhost:8000/api/v1/health

# WebSocket load test (requires wscat)
npm install -g wscat
wscat -c ws://localhost/ws/
```

---

## Monitoring Commands

```bash
# Real-time resource monitoring
docker stats

# View all containers
docker ps -a

# View network usage
docker stats --no-stream --format "table {{.Container}}\t{{.NetIO}}"

# View specific service metrics
docker inspect observability_backend | jq '.[] | {Memory: .State.Memory, CPU: .State.Pid}'

# View event logs
docker events --filter type=container

# Check image sizes
docker images

# View container filesystem changes
docker diff observability_backend
```

---

## Emergency Procedures

### Force Stop All Services

```bash
docker-compose down --remove-orphans
docker system prune -f  # Be careful - removes dangling images/containers
```

### Reset to Clean State

```bash
# Stop services
docker-compose down

# Remove volumes (DELETE ALL DATA)
docker volume rm observability_postgres_data observability_redis_data observability_elasticsearch_data

# Clean images
docker-compose build --no-cache

# Restart fresh
docker-compose up -d
```

### Restore from Backup

```bash
# Stop services
docker-compose down

# Remove old volumes
docker volume rm observability_postgres_data

# Recreate
docker-compose up -d

# Restore data
gunzip < backup.sql.gz | docker-compose exec -T postgres psql -U postgres observability_db
```

---

## Configuration Changes

### Update Environment Variables

```bash
# Edit environment file
vim .env

# Reload services (applies changes)
docker-compose down
docker-compose up -d
```

### Update Service Configuration

```bash
# Edit Nginx configuration
vim docker/nginx/nginx.conf

# Reload Nginx (no downtime)
docker-compose exec nginx nginx -s reload

# Edit Redis configuration
vim docker/redis/redis.conf

# Restart Redis (brief interruption)
docker-compose restart redis
```

---

## Useful Aliases

Add to `~/.bashrc` or `~/.zshrc`:

```bash
alias dc='docker-compose'
alias dcup='docker-compose up -d'
alias dcdown='docker-compose down'
alias dclog='docker-compose logs -f'
alias dcps='docker-compose ps'
alias dcexec='docker-compose exec'

# Production aliases
alias dcprod='docker-compose -f docker-compose.yml -f docker-compose.prod.yml'
alias dcpup='dcprod up -d'
alias dcplog='dcprod logs -f'
```

---

## Performance Tuning

```bash
# Check PostgreSQL index usage
docker-compose exec postgres psql -U postgres -d observability_db \
  -c "SELECT schemaname, tablename, indexname, idx_scan FROM pg_stat_user_indexes ORDER BY idx_scan DESC"

# Check slow queries
docker-compose exec postgres psql -U postgres -d observability_db \
  -c "SELECT query, calls, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10"

# Redis memory info
docker-compose exec redis redis-cli INFO memory

# Elasticsearch cluster stats
curl http://localhost:9200/_stats | jq '.indices'
```

---

**Quick Help:**
```bash
docker-compose --help
docker-compose up --help
docker-compose logs --help
```
