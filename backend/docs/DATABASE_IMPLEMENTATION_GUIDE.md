-- Database Implementation & Integration Guide
-- For Backend Development Team

-- ============================================================================
-- QUICK START
-- ============================================================================

/*
STEP 1: Create PostgreSQL database
    createdb -U postgres observability_db

STEP 2: Apply schema
    psql -U postgres -d observability_db -f alembic/versions/20250524_0002_create_observability_schema.sql

STEP 3: Apply operational scripts
    psql -U postgres -d observability_db -f docs/DATABASE_OPERATIONS.sql

STEP 4: Verify installation
    psql -U postgres -d observability_db -c "\dt"

STEP 5: Configure connection in app
    DATABASE_URL=postgresql://postgres:password@localhost:5432/observability_db
*/

-- ============================================================================
-- TABLE RELATIONSHIPS DIAGRAM
-- ============================================================================

/*
roles (1) ----< (M) users
              |
              v
        audit_logs
              ^
              |
        +-----+-----------+---------+
        |     |           |         |
    machines robots    alerts    jobs
        |     | (1)     |         |
        |     v (M)     v         |
        |   (2)  \    (3)    \   |
        |   jobs ----- queue_items
        |     |         |
        v     v         |
    queues   robots     |
              |         |
              v (opt)   |
          orch_logs <---+
              
              ai_traces
              (linked to jobs/robots)
              
              sla_metrics
              (aggregate view of jobs)

Legend:
(M) = Many
(1) = One
(opt) = Optional FK
(2) = Foreign Key
(3) = Foreign Key
*/

-- ============================================================================
-- API ENDPOINT TO TABLE MAPPING
-- ============================================================================

/*
Backend API Endpoints:

GET    /api/v1/jobs              → SELECT * FROM jobs ORDER BY start_time DESC
GET    /api/v1/jobs/:id          → SELECT * FROM jobs WHERE id = :id
GET    /api/v1/jobs?robot_id=:id → SELECT * FROM jobs WHERE robot_id = :id
GET    /api/v1/jobs?status=:s    → SELECT * FROM jobs WHERE status = :s
GET    /api/v1/jobs/:id/logs     → SELECT * FROM orchestrator_logs WHERE job_id = :id

GET    /api/v1/robots            → SELECT * FROM robots WHERE is_enabled = TRUE
GET    /api/v1/robots/:id        → SELECT * FROM robots WHERE id = :id
GET    /api/v1/robots/stats      → SELECT * FROM mv_robot_health_snapshot

GET    /api/v1/queues            → SELECT * FROM queues
GET    /api/v1/queues/:id/items  → SELECT * FROM queue_items WHERE queue_id = :id
GET    /api/v1/queues/:id/stats  → SELECT * FROM mv_queue_performance WHERE id = :id

GET    /api/v1/alerts            → SELECT * FROM alerts WHERE deleted_at IS NULL
GET    /api/v1/alerts/:id        → SELECT * FROM alerts WHERE id = :id
PUT    /api/v1/alerts/:id/acknowledge → UPDATE alerts SET acknowledged_by = :user_id
PUT    /api/v1/alerts/:id/resolve     → UPDATE alerts SET resolved_by = :user_id

GET    /api/v1/logs              → SELECT * FROM orchestrator_logs ORDER BY timestamp DESC
GET    /api/v1/logs?level=:l     → SELECT * FROM orchestrator_logs WHERE log_level = :l
GET    /api/v1/logs/search       → SELECT * FROM orchestrator_logs WHERE message ILIKE :q

GET    /api/v1/ai-monitoring     → SELECT * FROM ai_traces ORDER BY timestamp DESC
GET    /api/v1/ai-monitoring/anomalies → SELECT * FROM ai_traces WHERE is_anomaly = TRUE

GET    /api/v1/sla               → SELECT * FROM sla_metrics WHERE metric_date = CURRENT_DATE
GET    /api/v1/sla/history       → SELECT * FROM sla_metrics ORDER BY metric_date DESC

GET    /api/v1/audit             → SELECT * FROM audit_logs ORDER BY timestamp DESC
GET    /api/v1/audit?user_id=:id → SELECT * FROM audit_logs WHERE user_id = :id

POST   /api/v1/auth/login        → SELECT * FROM users WHERE email = :email (verify password)
*/

-- ============================================================================
-- PYTHON SQLALCHEMY MODEL EXAMPLES
-- ============================================================================

/*
# Example SQLAlchemy models matching the schema

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    role = relationship('Role')

class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    robot_id = Column(Integer, ForeignKey('robots.id'))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    status = Column(String(50), nullable=False)
    input_arguments = Column(JSON)
    output_arguments = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)
    
    robot = relationship('Robot')
    logs = relationship('OrchestratorLog')
    queue_items = relationship('QueueItem')

class Robot(Base):
    __tablename__ = 'robots'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    machine_id = Column(Integer, ForeignKey('machines.id'), nullable=False)
    status = Column(String(50), default='Offline')
    robot_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    machine = relationship('Machine')
    jobs = relationship('Job')
*/

-- ============================================================================
-- PERFORMANCE TUNING CHECKLIST
-- ============================================================================

/*
[ ] Connection Pooling
    - Configure PgBouncer or SQLAlchemy connection pool
    - Pool size: (CPU cores * 2) + 1
    - Max overflow: 10
    - Pool recycle: 3600 seconds

[ ] Query Optimization
    - Use prepared statements to prevent SQL injection
    - Always specify WHERE conditions for DELETE/UPDATE
    - Use LIMIT for paginated queries
    - Avoid SELECT * unless necessary

[ ] Indexing Strategy
    - Foreign key columns indexed (automatic)
    - Status/status_date columns indexed
    - Timestamp columns indexed for range queries
    - Add composite indexes for frequently JOINed tables

[ ] Caching
    - Cache materialized views (refresh schedule)
    - Redis cache for frequently accessed data (users, roles)
    - Implement cache invalidation on writes

[ ] Batch Operations
    - Use BULK INSERT for millions of records
    - Batch DELETE operations (delete 10K at a time)
    - Use COPY for CSV imports

[ ] Monitoring
    - Enable slow query log (> 1 second)
    - Monitor pg_stat_statements
    - Check table bloat (autovacuum effectiveness)
    - Monitor disk space usage
    - Monitor connection count
    - Alert on high cache miss ratio
*/

-- ============================================================================
-- COMMON QUERIES FOR BACKEND IMPLEMENTATION
-- ============================================================================

-- 1. Get recent jobs with robot info
SELECT 
    j.id, j.name, j.status, j.start_time, j.duration_seconds,
    r.name as robot_name, m.name as machine_name
FROM jobs j
LEFT JOIN robots r ON j.robot_id = r.id
LEFT JOIN machines m ON r.machine_id = m.id
WHERE j.deleted_at IS NULL
ORDER BY j.start_time DESC
LIMIT 100;

-- 2. Get job failure analysis
SELECT 
    j.name as process_name,
    COUNT(*) as total_jobs,
    SUM(CASE WHEN j.status = 'Failed' THEN 1 ELSE 0 END) as failed_jobs,
    ROUND(100.0 * SUM(CASE WHEN j.status = 'Failed' THEN 1 ELSE 0 END) / COUNT(*), 2) as failure_rate,
    AVG(j.duration_seconds) as avg_duration_sec
FROM jobs j
WHERE j.start_time > NOW() - INTERVAL '7 days'
  AND j.deleted_at IS NULL
GROUP BY j.name
ORDER BY failure_rate DESC;

-- 3. Get robot status overview
SELECT 
    r.name,
    r.status,
    m.name as machine,
    r.execution_sessions,
    COUNT(j.id) as jobs_today,
    SUM(CASE WHEN j.status = 'Failed' THEN 1 ELSE 0 END) as failed_today,
    MAX(j.end_time) as last_job_completed
FROM robots r
LEFT JOIN machines m ON r.machine_id = m.id
LEFT JOIN jobs j ON r.id = j.robot_id AND DATE(j.start_time) = CURRENT_DATE
WHERE r.is_enabled = TRUE AND r.deleted_at IS NULL
GROUP BY r.id, r.name, r.status, m.name, r.execution_sessions
ORDER BY r.name;

-- 4. Get active alerts by severity
SELECT 
    severity,
    status,
    COUNT(*) as count,
    MAX(created_at) as latest
FROM alerts
WHERE deleted_at IS NULL
  AND (status = 'New' OR status = 'Acknowledged')
GROUP BY severity, status
ORDER BY 
    CASE severity 
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
        ELSE 5
    END;

-- 5. Get queue performance stats
SELECT 
    q.name,
    q.item_count,
    q.success_count,
    q.failed_count,
    COUNT(CASE WHEN qi.status = 'Pending' THEN 1 END) as pending_items,
    COUNT(CASE WHEN qi.status = 'Processing' THEN 1 END) as processing_items,
    AVG(EXTRACT(EPOCH FROM (NOW() - qi.created_at))/60) as avg_wait_time_min
FROM queues q
LEFT JOIN queue_items qi ON q.id = qi.queue_id AND qi.deleted_at IS NULL
WHERE q.deleted_at IS NULL
GROUP BY q.id, q.name
ORDER BY q.name;

-- 6. Get AI anomaly detection results
SELECT 
    at.id,
    at.model_name,
    at.anomaly_score,
    at.confidence_score,
    j.name as job_name,
    r.name as robot_name,
    at.timestamp
FROM ai_traces at
LEFT JOIN jobs j ON at.job_id = j.id
LEFT JOIN robots r ON at.robot_id = r.id
WHERE at.is_anomaly = TRUE
  AND at.timestamp > NOW() - INTERVAL '24 hours'
ORDER BY at.anomaly_score DESC;

-- ============================================================================
-- DATA IMPORT PROCEDURES
-- ============================================================================

-- Import jobs from Orchestrator API (bulk insert)
INSERT INTO jobs (name, release_id, robot_id, start_time, end_time, status, 
                  input_arguments, output_arguments, orchestrator_job_id, created_at)
SELECT 
    api_response->>'Name',
    api_response->>'ReleaseId',
    r.id,
    TO_TIMESTAMP(api_response->>'StartTime', 'YYYY-MM-DD HH24:MI:SS'),
    CASE WHEN api_response->>'EndTime' IS NOT NULL 
         THEN TO_TIMESTAMP(api_response->>'EndTime', 'YYYY-MM-DD HH24:MI:SS')
         ELSE NULL 
    END,
    api_response->>'State',
    (api_response->'InputArguments')::JSONB,
    (api_response->'OutputArguments')::JSONB,
    api_response->>'Id',
    CURRENT_TIMESTAMP
FROM 
    json_array_elements('{}'::json) as api_response
    LEFT JOIN robots r ON r.orchestrator_robot_id = api_response->>'RobotId'
ON CONFLICT (orchestrator_job_id) DO UPDATE SET
    end_time = EXCLUDED.end_time,
    status = EXCLUDED.status,
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================================
-- ERROR HANDLING & LOGGING
-- ============================================================================

-- Log API errors to audit_logs
INSERT INTO audit_logs (action, resource_type, status, error_message, ip_address)
VALUES (
    'API_CALL',
    'Job',
    'Failure',
    'Failed to fetch job details: Connection timeout',
    '192.168.1.1'::inet
);

-- Track user authentication
INSERT INTO audit_logs (user_id, action, status, ip_address, timestamp)
SELECT 
    u.id,
    'LOGIN',
    'Success',
    '192.168.1.1'::inet,
    CURRENT_TIMESTAMP
FROM users u
WHERE u.email = 'user@example.com';

-- ============================================================================
-- SECURITY RECOMMENDATIONS
-- ============================================================================

/*
1. Use parameterized queries to prevent SQL injection
   BAD:  SELECT * FROM users WHERE email = '" + email + "'"
   GOOD: SELECT * FROM users WHERE email = %s (with parameter binding)

2. Encrypt sensitive data
   - Password hashes using bcrypt/argon2
   - API keys using pgcrypto
   - Connection strings (use environment variables)

3. Enable SSL/TLS for connections
   sslmode=require in connection string

4. Implement Row-Level Security (RLS)
   ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

5. Use application user context
   SET app.user_id = 123; (set before queries)
   RESET app.user_id;

6. Regular backups
   - Automated daily full backups
   - Point-in-time recovery enabled
   - Test restore procedures monthly

7. Monitor audit_logs regularly
   - Unexpected DELETE operations
   - Failed authentication attempts
   - Data access patterns
*/

-- ============================================================================
-- TROUBLESHOOTING GUIDE
-- ============================================================================

/*
Problem: Slow job queries
Solution:
  - Check EXPLAIN ANALYZE output
  - Verify indexes exist on robot_id, status, start_time
  - Run ANALYZE jobs; to update statistics
  - Consider partitioning if table > 100M rows

Problem: Connection pool exhausted
Solution:
  - Increase max_connections in postgresql.conf
  - Reduce pool size if not all used
  - Check for connection leaks in application
  - Query: SELECT * FROM pg_stat_activity;

Problem: High disk usage
Solution:
  - Run VACUUM FULL on large tables
  - Check table bloat: pgstattuple extension
  - Archive/delete old data per retention policy
  - Run REINDEX to compact indexes

Problem: Materialized views not refreshing
Solution:
  - Check cron jobs for scheduled refresh
  - Run REFRESH MATERIALIZED VIEW CONCURRENTLY mv_name;
  - Monitor: SELECT * FROM pg_stat_user_tables;

Problem: Audit triggers failing
Solution:
  - Check trigger function: SELECT * FROM pg_proc WHERE proname = 'audit_table_changes';
  - Verify application sets app.user_id context
  - Check audit_logs table for error records
*/

-- ============================================================================
-- MIGRATION PATH (Alembic)
-- ============================================================================

/*
# In alembic/env.py, configure for PostgreSQL:

sqlalchemy.url = postgresql://user:password@localhost/observability_db

# Create migrations:
alembic revision --autogenerate -m "Add new column"
alembic upgrade head

# Downgrade:
alembic downgrade -1

# Check migration history:
alembic history

# For production deployments:
1. Backup database
2. Test migration on staging
3. Run migration during maintenance window
4. Verify data integrity
5. Enable monitoring
*/

-- ============================================================================
-- PERFORMANCE BASELINE QUERIES
-- ============================================================================

-- Database size
SELECT pg_size_pretty(pg_database_size('observability_db'));

-- Total table size
SELECT pg_size_pretty(SUM(pg_total_relation_size(schemaname||'.'||tablename)))
FROM pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema');

-- Index sizes
SELECT 
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_indexes
LEFT JOIN pg_stat_user_indexes ON indexname = indexname
ORDER BY pg_relation_size(indexrelid) DESC;

-- Connection count
SELECT count(*) FROM pg_stat_activity;

-- Cache hit ratio
SELECT 
    ROUND(100.0 * SUM(heap_blks_hit) / (SUM(heap_blks_hit) + SUM(heap_blks_read)), 2) as cache_hit_ratio
FROM pg_statio_user_tables;

-- ============================================================================
-- END OF IMPLEMENTATION GUIDE
-- ============================================================================
