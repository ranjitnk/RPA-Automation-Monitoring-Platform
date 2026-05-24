# Docker Deployment Guide - UiPath Observability Platform

## Overview

This guide provides comprehensive instructions for deploying the UiPath Observability Platform using Docker and Docker Compose in both development and production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (Development)](#quick-start-development)
3. [Production Deployment](#production-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Service Architecture](#service-architecture)
6. [Monitoring & Health Checks](#monitoring--health-checks)
7. [Backup & Recovery](#backup--recovery)
8. [Troubleshooting](#troubleshooting)
9. [Security Considerations](#security-considerations)

---

## Prerequisites

### System Requirements

**Development Environment:**
- Docker 20.10+
- Docker Compose 1.29+
- 8GB RAM minimum
- 20GB free disk space
- CPU: 4 cores recommended

**Production Environment:**
- Docker 20.10+ (latest stable)
- Docker Compose 1.29+ or Docker Compose V2
- 16GB+ RAM minimum (32GB recommended)
- 100GB+ SSD for data persistence
- CPU: 8+ cores recommended
- Linux kernel 5.0+

### Installation

**Ubuntu/Debian:**
```bash
# Install Docker
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# Add current user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

**macOS/Windows:**
- Download and install Docker Desktop from https://www.docker.com/products/docker-desktop

### Verify Installation

```bash
docker --version
docker-compose --version
docker run hello-world
```

---

## Quick Start (Development)

### 1. Clone Repository

```bash
git clone https://github.com/your-org/uipath-observability.git
cd uipath-observability
```

### 2. Create Environment File

```bash
cp .env.example .env
```

The `.env.example` file contains all available environment variables with documentation.

### 3. Start Services

```bash
# Start all services in background
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
```

### 4. Verify Services

```bash
# Check service status
docker-compose ps

# Test health endpoints
curl http://localhost:8000/api/v1/health      # Backend
curl http://localhost:5601                     # Kibana
curl http://localhost                          # Frontend (via Nginx)
```

### 5. Access Applications

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost | - |
| Backend API | http://localhost:8000/api/v1 | JWT Auth |
| API Docs | http://localhost:8000/docs | - |
| Kibana | http://localhost:5601 | elastic / changeme |
| PostgreSQL | localhost:5432 | postgres / postgres |
| Redis | localhost:6379 | redis_password |

### 6. Stop Services

```bash
# Stop all services (preserve data)
docker-compose down

# Stop and remove volumes (reset database)
docker-compose down -v
```

---

## Production Deployment

### 1. Prepare Production Environment

```bash
# Create production environment file
cp .env.example .env.prod

# Edit with production values
vim .env.prod
```

### 2. Critical Production Configuration

Set these variables in `.env.prod`:

```bash
# Database
POSTGRES_PASSWORD=<strong-random-password>
POSTGRES_SSLMODE=require

# Redis
REDIS_PASSWORD=<strong-random-password>

# Elasticsearch
ELASTIC_PASSWORD=<strong-random-password>
KIBANA_PASSWORD=<strong-random-password>
KIBANA_ENCRYPTION_KEY=<32-char-random-key>
ELASTIC_SECURITY_ENABLED=true

# JWT
JWT_SECRET=<strong-random-secret-min-32-chars>

# Frontend/Backend
ENVIRONMENT=production
LOG_LEVEL=WARNING
CORS_ORIGINS=https://yourdomain.com

# Nginx
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443
```

### 3. Generate Secure Secrets

```bash
# Generate JWT secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate Elasticsearch passwords
openssl rand -base64 32

# Generate Kibana encryption key
openssl rand -base64 24
```

### 4. Configure SSL Certificates

For HTTPS, place certificates in `docker/nginx/ssl/`:

```bash
# Create SSL directory
mkdir -p docker/nginx/ssl

# Copy your certificates (from Let's Encrypt or CA)
cp /path/to/cert.pem docker/nginx/ssl/cert.pem
cp /path/to/key.pem docker/nginx/ssl/key.pem

# Set permissions
chmod 600 docker/nginx/ssl/key.pem
```

### 5. Deploy with Production Compose File

```bash
# Start production environment
docker-compose \
  --env-file .env.prod \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  up -d

# View logs
docker-compose \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  logs -f
```

### 6. Verify Production Deployment

```bash
# Check all services are healthy
docker-compose \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  ps

# Expected output should show "healthy" status for all services
```

### 7. Set Up Automatic Backups

Create a backup script at `/opt/observability/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backup/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

docker-compose exec -T postgres pg_dump \
  -U postgres observability_db \
  | gzip > "$BACKUP_DIR/backup_$TIMESTAMP.sql.gz"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

Schedule with cron:

```bash
# Run daily at 2 AM
0 2 * * * /opt/observability/backup.sh
```

---

## Environment Configuration

### File Structure

```
.env.example              # Template with all variables documented
.env                      # Development environment (git-ignored)
.env.prod                 # Production environment (git-ignored)
docker/
├── nginx/
│   ├── nginx.conf       # Main Nginx configuration
│   ├── nginx-prod.conf  # Production-specific settings
│   └── conf.d/
│       ├── api.conf     # Backend API routing
│       ├── frontend.conf # Frontend SPA routing
│       └── websocket.conf # WebSocket configuration
├── redis/
│   ├── redis.conf       # Development Redis config
│   └── redis-prod.conf  # Production Redis config
├── elasticsearch/
│   ├── elasticsearch.yml        # Development ES config
│   └── elasticsearch-prod.yml   # Production ES config
├── postgres/
│   ├── init/            # SQL init scripts
│   ├── postgresql.conf  # PostgreSQL tuning
│   └── backup/          # Automated backups
```

### Key Environment Variables

**Database:**
- `POSTGRES_DB` - Database name
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password (change in production!)
- `POSTGRES_SSLMODE` - SSL requirement (prefer/require)

**Cache:**
- `REDIS_PASSWORD` - Redis authentication (change in production!)
- `REDIS_TTL` - Cache entry time-to-live

**Search:**
- `ELASTICSEARCH_HOST` - ES cluster URL
- `ELASTIC_PASSWORD` - ES password (change in production!)
- `ELASTIC_SECURITY_ENABLED` - Enable SSL/auth

**Backend:**
- `ENVIRONMENT` - development/staging/production
- `LOG_LEVEL` - DEBUG/INFO/WARNING/ERROR/CRITICAL
- `JWT_SECRET` - JWT signing key (change in production!)
- `JWT_EXPIRATION_HOURS` - Token lifetime

**Frontend:**
- `VITE_API_BASE_URL` - Backend API URL
- `VITE_WS_URL` - WebSocket URL

---

## Service Architecture

### Docker Compose Services

```yaml
┌─────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy                   │
│                  Port 80 (HTTP) / 443 (HTTPS)           │
└──────────────┬──────────────────────────────┬───────────┘
               │                              │
        ┌──────▼────────┐            ┌───────▼──────────┐
        │  Frontend SPA │            │  Backend API     │
        │  Port 5173    │            │  Port 8000       │
        │  React + Vite │            │  FastAPI         │
        └──────────────┘            └───────┬──────┬────┘
                                            │      │
                    ┌───────────────────────┘      └────┬─────────┐
                    │                                   │         │
          ┌─────────▼──────────┐         ┌──────────────▼──┐   ┌──▼──────────┐
          │   PostgreSQL       │         │  Redis Cache    │   │ ElasticSearch
          │   Port 5432        │         │  Port 6379      │   │ Port 9200
          │   Time-Series DB   │         │  Session Store  │   │ Log Storage
          └────────────────────┘         └─────────────────┘   └──┬──────────┘
                                                                    │
                                                            ┌───────▼─────┐
                                                            │  Kibana     │
                                                            │  Port 5601  │
                                                            │  Dashboards │
                                                            └─────────────┘
```

### Service Dependencies

```
nginx (port 80/443)
├── depends_on: frontend, backend
│
frontend (port 5173)
├── depends_on: backend
│
backend (port 8000)
├── depends_on: postgres (healthy)
├── depends_on: redis (healthy)
├── depends_on: elasticsearch (healthy)
│
postgres (port 5432)
├── initialized from: docker/postgres/init/
├── volumes: postgres_data:/var/lib/postgresql/data
│
redis (port 6379)
├── volumes: redis_data:/data
│
elasticsearch (port 9200)
├── depends_on: none
├── volumes: elasticsearch_data:/usr/share/elasticsearch/data
│
kibana (port 5601)
├── depends_on: elasticsearch (healthy)
```

### Health Checks

Each service includes health checks:

| Service | Check Endpoint | Interval | Retries |
|---------|---|---|---|
| PostgreSQL | pg_isready | 10s | 5 |
| Redis | redis-cli ping | 10s | 5 |
| ElasticSearch | /_cluster/health | 10s | 5 |
| Kibana | /api/status | 10s | 5 |
| Backend | /api/v1/health | 10s | 5 |
| Frontend | HTTP 200 | 10s | 5 |
| Nginx | /health endpoint | 10s | 5 |

---

## Monitoring & Health Checks

### Health Check Commands

```bash
# Check all services
docker-compose ps

# Backend API health
curl -s http://localhost:8000/api/v1/health | jq .

# Database connectivity
docker-compose exec postgres pg_isready -U postgres

# Redis connectivity
docker-compose exec redis redis-cli ping

# Elasticsearch cluster status
curl http://localhost:9200/_cluster/health

# View service logs
docker-compose logs backend --tail 100
```

### Common Issues & Solutions

**Service won't start:**
```bash
# Check logs for errors
docker-compose logs <service-name>

# Ensure port is not in use
lsof -i :<port>

# Check disk space
df -h
```

**Database connection failed:**
```bash
# Verify database is initialized
docker-compose exec postgres psql -U postgres -l

# Check database logs
docker-compose logs postgres
```

**Redis connection issues:**
```bash
# Check Redis is accepting connections
docker-compose exec redis redis-cli -a redis_password ping

# Check Redis memory
docker-compose exec redis redis-cli INFO memory
```

---

## Backup & Recovery

### Automated Backups

**PostgreSQL:**
```bash
# Create backup
docker-compose exec -T postgres pg_dump -U postgres observability_db | gzip > backup.sql.gz

# Restore from backup
gunzip < backup.sql.gz | docker-compose exec -T postgres psql -U postgres -d observability_db
```

**Redis:**
```bash
# Copy RDB file
docker-compose cp redis:/data/dump.rdb ./backups/redis.rdb

# Restore (stop Redis, copy file back, restart)
docker-compose stop redis
docker-compose cp ./backups/redis.rdb redis:/data/dump.rdb
docker-compose start redis
```

**ElasticSearch:**
```bash
# Create snapshot repository
curl -X PUT "localhost:9200/_snapshot/backup" \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "fs",
    "settings": {
      "location": "/elasticsearch/backup"
    }
  }'

# Create snapshot
curl -X PUT "localhost:9200/_snapshot/backup/snapshot-$(date +%Y%m%d)"
```

### Recovery Procedures

```bash
# Restore database from backup
docker-compose down
docker volume rm observability_postgres_data
docker-compose up -d postgres
gunzip < backup.sql.gz | docker-compose exec -T postgres psql -U postgres

# Rebuild indices
docker-compose exec elasticsearch curl -X POST "localhost:9200/_reindex"
```

---

## Troubleshooting

### Common Problems

**Out of Memory**
```bash
# Check memory usage
docker stats

# Increase container limits in docker-compose.prod.yml
services:
  elasticsearch:
    deploy:
      resources:
        limits:
          memory: 4G
```

**Slow Queries**
```bash
# Enable query logging
# In docker-compose.yml environment:
DATABASE_QUERY_LOGGING=true
DATABASE_QUERY_LOGGING_THRESHOLD=1000

# View slow logs
docker-compose logs backend | grep slow
```

**WebSocket Connection Issues**
```bash
# Check WebSocket endpoint
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  http://localhost/ws/

# View Nginx WebSocket logs
docker-compose logs nginx | grep -i upgrade
```

**Port Already in Use**
```bash
# Find process using port
sudo lsof -i :8000

# Change port in .env
BACKEND_PORT=8001
docker-compose down && docker-compose up -d
```

---

## Security Considerations

### Production Security Checklist

- [ ] Change all default passwords (Postgres, Redis, Elasticsearch)
- [ ] Generate new JWT secret
- [ ] Set `ENVIRONMENT=production`
- [ ] Enable SSL/TLS (HTTPS)
- [ ] Set up firewall rules (restrict to authorized IPs)
- [ ] Enable Elasticsearch security
- [ ] Use strong CORS_ORIGINS (not *)
- [ ] Set DATABASE SSL mode to require
- [ ] Implement rate limiting (Nginx configured)
- [ ] Enable audit logging
- [ ] Set up backup procedures
- [ ] Monitor resource usage
- [ ] Keep Docker images updated

### Network Security

```yaml
# Only expose necessary ports
networks:
  observability_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.30.0.0/16

# External only for Nginx
ports:
  - "80:80"      # HTTP (redirect to HTTPS)
  - "443:443"    # HTTPS
  # Internal services accessible only within network
```

### Secrets Management

**Never commit secrets to Git:**
```bash
# Add to .gitignore
.env
.env.prod
docker/nginx/ssl/
backups/
```

**Use environment files:**
```bash
# Load from secure source
source /secure/location/.env.prod
docker-compose --env-file /secure/location/.env.prod up -d
```

---

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Redis Docker Image](https://hub.docker.com/_/redis)
- [Elasticsearch Docker Image](https://www.docker.elastic.co/)
- [Nginx Docker Image](https://hub.docker.com/_/nginx)

---

## Support & Troubleshooting

For issues or questions:

1. Check Docker logs: `docker-compose logs <service>`
2. Review environment configuration: `cat .env`
3. Verify service health: `docker-compose ps`
4. Check system resources: `docker stats`
5. Review official documentation links above

---

**Last Updated:** 2024
**Version:** 1.0
