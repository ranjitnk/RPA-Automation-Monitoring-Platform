# UiPath Observability Platform - PostgreSQL Schema Design

## Overview
This document describes the complete PostgreSQL schema for the UiPath automation observability platform with production-grade performance optimizations, audit tracking, and retention policies.

## Design Principles

1. **Normalization**: Normalized to 3NF to reduce redundancy
2. **Performance**: Strategic indexing on frequently queried columns
3. **Audit Trail**: All tables track created_at, updated_at, deleted_at
4. **Retention**: Time-based partitioning for archival and cleanup
5. **Scalability**: Designed for millions of records
6. **Relationships**: Proper foreign keys with cascade delete where appropriate

---

## Table Definitions

### 1. Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(32),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    CONSTRAINT fk_user_role FOREIGN KEY (role_id) REFERENCES roles(id)
);

CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_username ON users(username) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_role_id ON users(role_id);
CREATE INDEX idx_users_is_active ON users(is_active) WHERE deleted_at IS NULL;
```

**Rationale**:
- Email/username indexed for login performance
- Partial index on deleted_at for soft deletes
- is_active index for active user queries
- MFA fields for future security enhancements

---

### 2. Roles Table

```sql
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '[]',
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ck_role_permissions CHECK (permissions IS NOT NULL)
);

CREATE INDEX idx_roles_name ON roles(name);

-- System roles
INSERT INTO roles (name, description, permissions, is_system) VALUES
('admin', 'Full system access', '["*:*"]'::jsonb, TRUE),
('manager', 'Manage jobs and alerts', '["jobs:*", "alerts:*", "robots:read"]'::jsonb, TRUE),
('user', 'Read own resources', '["jobs:read", "alerts:read", "robots:read"]'::jsonb, TRUE),
('viewer', 'Read-only access', '["*:read"]'::jsonb, TRUE);
```

**Rationale**:
- JSONB for flexible permission model
- System roles cannot be deleted
- String format: "resource:action" for easy querying

---

### 3. Machines Table

```sql
CREATE TABLE machines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    hostname VARCHAR(255),
    ip_address INET,
    os_type VARCHAR(50),
    os_version VARCHAR(100),
    cpu_cores INTEGER,
    ram_gb INTEGER,
    disk_gb INTEGER,
    orchestrator_machine_id VARCHAR(100) UNIQUE,
    is_enabled BOOLEAN DEFAULT TRUE,
    last_heartbeat TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_machines_name ON machines(name) WHERE deleted_at IS NULL;
CREATE INDEX idx_machines_enabled ON machines(is_enabled) WHERE deleted_at IS NULL;
CREATE INDEX idx_machines_heartbeat ON machines(last_heartbeat DESC);
CREATE INDEX idx_machines_orch_id ON machines(orchestrator_machine_id);
```

**Rationale**:
- INET type for IP address validation
- Heartbeat index for machine health queries
- Metadata JSONB for custom properties
- Unique on orchestrator_machine_id for sync

---

### 4. Robots Table

```sql
CREATE TABLE robots (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    machine_id INTEGER NOT NULL,
    robot_type VARCHAR(50) NOT NULL, -- 'Attended', 'Unattended', 'NonProduction'
    lic_robot_id VARCHAR(100) UNIQUE,
    username VARCHAR(255),
    domain VARCHAR(255),
    is_enabled BOOLEAN DEFAULT TRUE,
    status VARCHAR(50) DEFAULT 'Offline', -- 'Available', 'Offline', 'Executing', 'Unavailable'
    execution_sessions INTEGER DEFAULT 0,
    last_activity TIMESTAMP,
    license_key VARCHAR(100),
    robot_version VARCHAR(50),
    orchestrator_robot_id VARCHAR(100) UNIQUE,
    tags TEXT[],
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    CONSTRAINT fk_robot_machine FOREIGN KEY (machine_id) REFERENCES machines(id),
    CONSTRAINT ck_robot_type CHECK (robot_type IN ('Attended', 'Unattended', 'NonProduction')),
    CONSTRAINT ck_robot_status CHECK (status IN ('Available', 'Offline', 'Executing', 'Unavailable'))
);

CREATE INDEX idx_robots_machine_id ON robots(machine_id);
CREATE INDEX idx_robots_status ON robots(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_robots_robot_type ON robots(robot_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_robots_is_enabled ON robots(is_enabled) WHERE deleted_at IS NULL;
CREATE INDEX idx_robots_last_activity ON robots(last_activity DESC);
CREATE INDEX idx_robots_tags ON robots USING GIN(tags);
CREATE INDEX idx_robots_orch_id ON robots(orchestrator_robot_id);
```

**Rationale**:
- Tags as TEXT[] with GIN index for flexible categorization
- Status enum-like with check constraint
- Orchestrator IDs for external system sync
- Last activity index for robot health monitoring
- Metadata for custom robot properties

---

### 5. Jobs Table

```sql
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    release_id VARCHAR(100),
    robot_id INTEGER,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    status VARCHAR(50) NOT NULL, -- 'Running', 'Completed', 'Failed', 'Stopped', 'Pending'
    state VARCHAR(255),
    exit_code INTEGER,
    input_arguments JSONB DEFAULT '{}',
    output_arguments JSONB DEFAULT '{}',
    priority INTEGER DEFAULT 0,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 0,
    orchestrator_job_id VARCHAR(100) UNIQUE,
    source_environment VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    CONSTRAINT fk_job_robot FOREIGN KEY (robot_id) REFERENCES robots(id),
    CONSTRAINT ck_job_status CHECK (status IN ('Running', 'Completed', 'Failed', 'Stopped', 'Pending'))
);

-- Time-based partitioning recommended (see partitioning section)
-- For now, create standard indexes
CREATE INDEX idx_jobs_robot_id ON jobs(robot_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_jobs_status ON jobs(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_jobs_start_time ON jobs(start_time DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_jobs_end_time ON jobs(end_time DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);
CREATE INDEX idx_jobs_release_id ON jobs(release_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_jobs_orch_id ON jobs(orchestrator_job_id);
```

**Rationale**:
- Time-based partitioning (see partitioning section)
- Status tracking for monitoring
- JSONB for flexible input/output
- Orchestrator ID for sync
- Composite query indexes on (robot_id, status) helpful

---

### 6. Queues Table

```sql
CREATE TABLE queues (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    max_retries INTEGER DEFAULT 3,
    accept_orphaned_items BOOLEAN DEFAULT FALSE,
    orchestrator_queue_id VARCHAR(100) UNIQUE,
    item_count INTEGER DEFAULT 0,
    processing_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    retry_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_queues_name ON queues(name) WHERE deleted_at IS NULL;
CREATE INDEX idx_queues_orch_id ON queues(orchestrator_queue_id);
```

**Rationale**:
- Denormalized counts for quick stats (updated via triggers)
- Orchestrator sync ID
- Metadata for custom queue properties

---

### 7. Queue Items Table

```sql
CREATE TABLE queue_items (
    id BIGSERIAL PRIMARY KEY,
    queue_id INTEGER NOT NULL,
    job_id INTEGER,
    reference_id VARCHAR(255),
    priority INTEGER DEFAULT 0,
    status VARCHAR(50) NOT NULL, -- 'Pending', 'Processing', 'Completed', 'Failed', 'Retrying'
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    due_date TIMESTAMP,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    error_message TEXT,
    error_stacktrace TEXT,
    orchestrator_queue_item_id VARCHAR(100) UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    CONSTRAINT fk_queue_item_queue FOREIGN KEY (queue_id) REFERENCES queues(id),
    CONSTRAINT fk_queue_item_job FOREIGN KEY (job_id) REFERENCES jobs(id),
    CONSTRAINT ck_queue_item_status CHECK (status IN ('Pending', 'Processing', 'Completed', 'Failed', 'Retrying'))
);

-- Partitioning by date recommended
CREATE INDEX idx_queue_items_queue_id ON queue_items(queue_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_queue_items_status ON queue_items(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_queue_items_created_at ON queue_items(created_at DESC);
CREATE INDEX idx_queue_items_priority ON queue_items(priority DESC) WHERE status = 'Pending';
CREATE INDEX idx_queue_items_due_date ON queue_items(due_date) WHERE status IN ('Pending', 'Processing');
CREATE INDEX idx_queue_items_orch_id ON queue_items(orchestrator_queue_item_id);
```

**Rationale**:
- Large table (hundreds of millions) - BIGSERIAL for IDs
- Partitioning by created_at recommended
- Status-based indexes for workflow queries
- Priority index with filter for active items
- Error tracking for debugging
- Denormalized retry tracking

---

### 8. Alerts Table

```sql
CREATE TABLE alerts (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(50) NOT NULL, -- 'Critical', 'High', 'Medium', 'Low', 'Info'
    status VARCHAR(50) NOT NULL, -- 'New', 'Acknowledged', 'Resolved'
    source VARCHAR(100), -- 'Job', 'Robot', 'Queue', 'SLA', 'AI'
    source_id INTEGER,
    rule_id INTEGER,
    job_id INTEGER,
    robot_id INTEGER,
    acknowledged_by INTEGER,
    acknowledged_at TIMESTAMP,
    resolved_by INTEGER,
    resolved_at TIMESTAMP,
    first_occurrence TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_occurrence TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    occurrence_count INTEGER DEFAULT 1,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    CONSTRAINT fk_alert_acknowledged_by FOREIGN KEY (acknowledged_by) REFERENCES users(id),
    CONSTRAINT fk_alert_resolved_by FOREIGN KEY (resolved_by) REFERENCES users(id),
    CONSTRAINT fk_alert_job FOREIGN KEY (job_id) REFERENCES jobs(id),
    CONSTRAINT fk_alert_robot FOREIGN KEY (robot_id) REFERENCES robots(id),
    CONSTRAINT ck_alert_severity CHECK (severity IN ('Critical', 'High', 'Medium', 'Low', 'Info')),
    CONSTRAINT ck_alert_status CHECK (status IN ('New', 'Acknowledged', 'Resolved'))
);

-- Partitioning by created_at recommended for this time-series table
CREATE INDEX idx_alerts_severity ON alerts(severity) WHERE deleted_at IS NULL;
CREATE INDEX idx_alerts_status ON alerts(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);
CREATE INDEX idx_alerts_job_id ON alerts(job_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_alerts_robot_id ON alerts(robot_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_alerts_source ON alerts(source) WHERE deleted_at IS NULL;
CREATE INDEX idx_alerts_first_occurrence ON alerts(first_occurrence DESC);
```

**Rationale**:
- Large volume table - partitioning recommended
- Status tracking for alert workflow
- User references for acknowledgment/resolution
- Occurrence count for alert aggregation
- Source tracking for different alert types
- Metadata for custom alert properties

---

### 9. AI Traces Table

```sql
CREATE TABLE ai_traces (
    id BIGSERIAL PRIMARY KEY,
    job_id INTEGER,
    robot_id INTEGER,
    trace_name VARCHAR(255) NOT NULL,
    trace_type VARCHAR(50), -- 'Performance', 'Accuracy', 'Anomaly', 'Latency'
    model_name VARCHAR(255),
    model_version VARCHAR(50),
    input_data JSONB,
    output_data JSONB,
    predictions JSONB,
    confidence_score NUMERIC(5, 4), -- 0.0000 to 1.0000
    accuracy_score NUMERIC(5, 4),
    latency_ms NUMERIC(10, 2),
    anomaly_score NUMERIC(5, 4),
    is_anomaly BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_ai_trace_job FOREIGN KEY (job_id) REFERENCES jobs(id),
    CONSTRAINT fk_ai_trace_robot FOREIGN KEY (robot_id) REFERENCES robots(id),
    CONSTRAINT ck_confidence CHECK (confidence_score BETWEEN 0 AND 1),
    CONSTRAINT ck_accuracy CHECK (accuracy_score BETWEEN 0 AND 1),
    CONSTRAINT ck_anomaly CHECK (anomaly_score BETWEEN 0 AND 1)
);

-- Partitioning by timestamp recommended
CREATE INDEX idx_ai_traces_job_id ON ai_traces(job_id);
CREATE INDEX idx_ai_traces_robot_id ON ai_traces(robot_id);
CREATE INDEX idx_ai_traces_timestamp ON ai_traces(timestamp DESC);
CREATE INDEX idx_ai_traces_is_anomaly ON ai_traces(is_anomaly, timestamp DESC);
CREATE INDEX idx_ai_traces_trace_type ON ai_traces(trace_type, timestamp DESC);
```

**Rationale**:
- Large volume time-series data - partitioning critical
- Numeric(5,4) for bounded ML scores
- Anomaly detection for monitoring
- Model versioning for reproducibility
- Timestamp-based indexing for time-range queries

---

### 10. Orchestrator Logs Table

```sql
CREATE TABLE orchestrator_logs (
    id BIGSERIAL PRIMARY KEY,
    job_id INTEGER,
    robot_id INTEGER,
    log_level VARCHAR(50) NOT NULL, -- 'Debug', 'Info', 'Warning', 'Error'
    timestamp TIMESTAMP NOT NULL,
    message TEXT NOT NULL,
    source VARCHAR(255),
    category VARCHAR(100),
    exception_type VARCHAR(255),
    exception_message TEXT,
    exception_stacktrace TEXT,
    request_id VARCHAR(100),
    correlation_id VARCHAR(100),
    user_id INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_orch_log_job FOREIGN KEY (job_id) REFERENCES jobs(id),
    CONSTRAINT fk_orch_log_robot FOREIGN KEY (robot_id) REFERENCES robots(id),
    CONSTRAINT fk_orch_log_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT ck_log_level CHECK (log_level IN ('Debug', 'Info', 'Warning', 'Error'))
);

-- Partitioning by timestamp recommended (daily or weekly)
CREATE INDEX idx_orch_logs_timestamp ON orchestrator_logs(timestamp DESC);
CREATE INDEX idx_orch_logs_log_level ON orchestrator_logs(log_level, timestamp DESC);
CREATE INDEX idx_orch_logs_job_id ON orchestrator_logs(job_id);
CREATE INDEX idx_orch_logs_robot_id ON orchestrator_logs(robot_id);
CREATE INDEX idx_orch_logs_correlation_id ON orchestrator_logs(correlation_id);
CREATE INDEX idx_orch_logs_request_id ON orchestrator_logs(request_id);
```

**Rationale**:
- Massive volume table - partitioning essential
- Request/correlation IDs for distributed tracing
- Exception tracking for error analysis
- Timestamp-based queries critical
- Category index for log filtering

---

### 11. SLA Metrics Table

```sql
CREATE TABLE sla_metrics (
    id BIGSERIAL PRIMARY KEY,
    process_name VARCHAR(255) NOT NULL,
    metric_date DATE NOT NULL,
    total_jobs INTEGER DEFAULT 0,
    successful_jobs INTEGER DEFAULT 0,
    failed_jobs INTEGER DEFAULT 0,
    total_duration_seconds BIGINT DEFAULT 0,
    average_duration_seconds NUMERIC(10, 2),
    success_rate_percent NUMERIC(5, 2), -- 0.00 to 100.00
    target_success_rate_percent NUMERIC(5, 2) DEFAULT 99.00,
    target_average_duration_seconds NUMERIC(10, 2),
    status VARCHAR(50), -- 'On Track', 'At Risk', 'Breached'
    breaches INTEGER DEFAULT 0,
    robot_count INTEGER DEFAULT 0,
    queue_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ck_sla_success_rate CHECK (success_rate_percent BETWEEN 0 AND 100),
    CONSTRAINT ck_sla_target_rate CHECK (target_success_rate_percent BETWEEN 0 AND 100),
    CONSTRAINT ck_sla_status CHECK (status IN ('On Track', 'At Risk', 'Breached'))
);

CREATE INDEX idx_sla_metrics_process_name ON sla_metrics(process_name);
CREATE INDEX idx_sla_metrics_metric_date ON sla_metrics(metric_date DESC);
CREATE INDEX idx_sla_metrics_status ON sla_metrics(status) WHERE metric_date = CURRENT_DATE;
CREATE UNIQUE INDEX idx_sla_metrics_process_date ON sla_metrics(process_name, metric_date);
```

**Rationale**:
- Aggregated daily metrics
- Date-based index for trend queries
- Status tracking for compliance
- Unique constraint prevents duplicate daily entries
- Calculated fields for performance

---

### 12. Audit Logs Table

```sql
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL, -- 'CREATE', 'UPDATE', 'DELETE', 'ACKNOWLEDGE', 'RESOLVE'
    resource_type VARCHAR(100) NOT NULL, -- 'Job', 'Robot', 'Alert', 'User', etc.
    resource_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    changes JSONB, -- Delta of what changed
    ip_address INET,
    user_agent TEXT,
    request_id VARCHAR(100),
    status VARCHAR(50), -- 'Success', 'Failure'
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT ck_audit_action CHECK (action IN ('CREATE', 'UPDATE', 'DELETE', 'ACKNOWLEDGE', 'RESOLVE', 'LOGIN', 'LOGOUT')),
    CONSTRAINT ck_audit_status CHECK (status IN ('Success', 'Failure'))
);

-- Partitioning by timestamp recommended
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action, timestamp DESC);
```

**Rationale**:
- Immutable audit trail
- JSONB for flexible change tracking
- IP address for security tracking
- Request ID for tracing
- Partitioning by timestamp for retention

---

## Partitioning Strategy

### Tables Requiring Partitioning

#### 1. **Jobs Table** - Time-based Partitioning
```sql
-- Partition by month for easier retention
ALTER TABLE jobs SET (fillfactor = 90);

-- Create partitions for rolling window (keep 2 years of data)
-- January 2026 and beyond
CREATE TABLE jobs_2026_01 PARTITION OF jobs
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE jobs_2026_02 PARTITION OF jobs
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- Continue for all months...
```

#### 2. **Queue Items Table** - Time-based Partitioning
```sql
-- Partition by day for high-volume data (millions per day)
CREATE TABLE queue_items_2026_05_24 PARTITION OF queue_items
    FOR VALUES FROM ('2026-05-24') TO ('2026-05-25');
```

#### 3. **Alerts Table** - Time-based Partitioning
```sql
-- Partition by week
CREATE TABLE alerts_2026_w21 PARTITION OF alerts
    FOR VALUES FROM ('2026-05-24') TO ('2026-05-31');
```

#### 4. **AI Traces Table** - Time-based Partitioning
```sql
-- Partition by day for time-series data
CREATE TABLE ai_traces_2026_05_24 PARTITION OF ai_traces
    FOR VALUES FROM ('2026-05-24') TO ('2026-05-25');
```

#### 5. **Orchestrator Logs Table** - Time-based Partitioning
```sql
-- Partition by day (extremely high volume)
-- Keep only 90 days of hot data
CREATE TABLE orch_logs_2026_05_24 PARTITION OF orchestrator_logs
    FOR VALUES FROM ('2026-05-24') TO ('2026-05-25');
```

---

## Indexing Strategy

### B-Tree Indexes (Most Common)
- Foreign keys for joins
- Status columns for filtering
- Date/time columns for sorting
- Name/identifier columns for lookups

### GIN Indexes
- JSONB columns for key searches
- Array columns (tags)
- Full-text search (future enhancement)

### BRIN Indexes
- Large time-series columns (alternative to B-Tree for storage efficiency)
- Orchestrator logs timestamp column

```sql
-- Example BRIN index for massive logs table
CREATE INDEX idx_orch_logs_timestamp_brin ON orchestrator_logs USING BRIN (timestamp);
```

### Partial Indexes
- WHERE deleted_at IS NULL - exclude soft-deleted records
- WHERE status = 'Pending' - only active records

---

## Retention Policy

### Data Retention Guidelines

```
Table                  | Keep Duration | Archive Strategy        | Partition Size
logs                   | 90 days       | Daily partitions       | 1 day
orchestrator_logs      | 90 days       | Daily partitions       | 1 day
queue_items            | 1 year        | Daily partitions       | 1 day
ai_traces              | 1 year        | Daily partitions       | 1 day
alerts                 | 2 years       | Weekly partitions      | 1 week
jobs                   | 2 years       | Monthly partitions     | 1 month
audit_logs             | 7 years       | Monthly partitions     | 1 month
machines               | Forever       | No partitioning        | N/A
robots                 | Forever       | No partitioning        | N/A
queues                 | Forever       | No partitioning        | N/A
users                  | Forever       | No partitioning        | N/A
roles                  | Forever       | No partitioning        | N/A
sla_metrics            | 5 years       | Monthly partitions     | 1 month
```

### Automated Retention Script

```sql
-- Remove old orchestrator logs (90 day retention)
DELETE FROM orchestrator_logs 
WHERE timestamp < NOW() - INTERVAL '90 days';

-- Archive old queue items
CREATE TABLE queue_items_archive_2026_q1 AS
SELECT * FROM queue_items 
WHERE created_at < '2026-04-01' AND created_at >= '2026-01-01';

DELETE FROM queue_items 
WHERE created_at < '2026-04-01' AND created_at >= '2026-01-01';

-- Drop old partitions
DROP TABLE IF EXISTS orch_logs_2026_02_15;
```

---

## Performance Optimizations

### 1. Connection Pooling
```
- Use PgBouncer or connection pooling in application
- Recommended pool size: (cores * 2) + 1
- Example: 8 cores = 17 connections
```

### 2. Query Optimization Settings
```sql
-- In postgresql.conf or SET commands
SET work_mem = '256MB';           -- Per operation memory
SET maintenance_work_mem = '1GB'; -- VACUUM, CREATE INDEX
SET effective_cache_size = '4GB'; -- Query planner hint
SET random_page_cost = 1.1;       -- SSD optimization
SET shared_preload_libraries = 'pg_stat_statements,auto_explain';
```

### 3. Materialized Views for Analytics
```sql
-- Daily job statistics
CREATE MATERIALIZED VIEW mv_daily_job_stats AS
SELECT 
    DATE(start_time) as report_date,
    robot_id,
    status,
    COUNT(*) as job_count,
    AVG(duration_seconds) as avg_duration,
    MAX(duration_seconds) as max_duration,
    SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_count
FROM jobs
WHERE start_time > NOW() - INTERVAL '90 days'
GROUP BY DATE(start_time), robot_id, status;

CREATE INDEX idx_mv_job_stats_date ON mv_daily_job_stats(report_date);

-- Refresh daily
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_job_stats;
```

### 4. Denormalization for Hot Queries
```sql
-- Queue aggregation (updated via trigger)
ALTER TABLE queues ADD COLUMN item_count INTEGER DEFAULT 0;
ALTER TABLE queues ADD COLUMN success_count INTEGER DEFAULT 0;
ALTER TABLE queues ADD COLUMN failed_count INTEGER DEFAULT 0;

-- Trigger to update queue counts
CREATE OR REPLACE FUNCTION update_queue_counts()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE queues 
    SET item_count = (SELECT COUNT(*) FROM queue_items WHERE queue_id = NEW.queue_id),
        success_count = (SELECT COUNT(*) FROM queue_items WHERE queue_id = NEW.queue_id AND status = 'Completed'),
        failed_count = (SELECT COUNT(*) FROM queue_items WHERE queue_id = NEW.queue_id AND status = 'Failed')
    WHERE id = NEW.queue_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_queue_counts
AFTER INSERT, UPDATE, DELETE ON queue_items
FOR EACH ROW EXECUTE FUNCTION update_queue_counts();
```

### 5. EXPLAIN ANALYZE for Query Planning
```sql
EXPLAIN ANALYZE
SELECT j.*, r.name as robot_name, m.name as machine_name
FROM jobs j
LEFT JOIN robots r ON j.robot_id = r.id
LEFT JOIN machines m ON r.machine_id = m.id
WHERE j.start_time > NOW() - INTERVAL '7 days'
  AND j.status = 'Failed'
ORDER BY j.start_time DESC
LIMIT 20;
```

---

## Audit Trail Implementation

### Automatic Audit Triggers
```sql
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs (
        user_id,
        action,
        resource_type,
        resource_id,
        old_values,
        new_values,
        changes
    ) VALUES (
        COALESCE(current_setting('app.user_id')::INTEGER, NULL),
        TG_ARGV[0],
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        CASE WHEN TG_OP = 'UPDATE' OR TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN row_to_json(NEW) ELSE NULL END,
        CASE WHEN TG_OP = 'UPDATE' THEN 
            jsonb_object_agg(key, value)
        ELSE NULL END
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Attach to jobs table
CREATE TRIGGER jobs_audit
AFTER INSERT OR UPDATE OR DELETE ON jobs
FOR EACH ROW EXECUTE FUNCTION audit_trigger('MANAGE_JOBS');
```

---

## Security Best Practices

### 1. Row-Level Security (RLS)
```sql
-- Prevent users from seeing other users' audit logs
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY audit_logs_user_isolation ON audit_logs
    USING (user_id = current_setting('app.user_id')::INTEGER OR current_setting('app.user_role')::TEXT = 'admin');
```

### 2. Encrypted Columns
```sql
-- For sensitive data
ALTER TABLE users ADD COLUMN api_key_encrypted BYTEA;

-- Use pgcrypto extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt API key
UPDATE users SET api_key_encrypted = pgp_sym_encrypt('secret_key', 'passphrase')
WHERE id = 1;
```

### 3. Connection SSL
```
# In postgresql.conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
```

---

## Monitoring & Maintenance

### 1. Table Size Monitoring
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 2. Missing Index Detection
```sql
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
  AND n_distinct > 100
  AND abs(correlation) < 0.1
ORDER BY n_distinct DESC;
```

### 3. Unused Indexes
```sql
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexname NOT LIKE 'pg_toast%'
ORDER BY pg_relation_size(indexrelid) DESC;
```

### 4. Autovacuum Monitoring
```sql
-- Monitor vacuum activity
SELECT 
    schemaname,
    relname,
    n_dead_tup,
    n_tup_upd,
    n_tup_del,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC;
```

---

## Backup & Recovery Strategy

### 1. Full Database Backup
```bash
#!/bin/bash
# Daily full backup
BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

pg_dump -U postgres -d observability_db \
    --format=custom \
    --file="${BACKUP_DIR}/full_${TIMESTAMP}.dump" \
    --compress=9 \
    --verbose \
    2>&1 | tee "${BACKUP_DIR}/full_${TIMESTAMP}.log"
```

### 2. Point-in-Time Recovery (PITR)
```bash
# Enable WAL archiving in postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /wal_archive/%f'
```

### 3. Restore Procedure
```bash
# Restore from backup
pg_restore -U postgres -d observability_db_restore \
    --format=custom \
    /backups/postgres/full_20260524_120000.dump
```

---

## Migration Notes

### Creating the Schema
1. Run all table creation DDL statements
2. Create all indexes after tables (faster insert)
3. Enable partitioning for large tables
4. Set up automatic partition creation script
5. Configure retention policies
6. Set up audit triggers
7. Configure monitoring queries

### Performance Tuning Checklist
- [ ] ANALYZE tables after initial data load
- [ ] Check slow query log
- [ ] Review query plans with EXPLAIN ANALYZE
- [ ] Add missing indexes
- [ ] Consider partitioning for large tables
- [ ] Set up materialized view refresh schedule
- [ ] Configure autovacuum settings per table
- [ ] Monitor connection pool utilization

---

## Summary

This schema is designed for:
- ✅ **Scalability**: Partitioning for billions of records
- ✅ **Performance**: Strategic indexing and denormalization
- ✅ **Auditability**: Complete audit trail with triggers
- ✅ **Retention**: Data lifecycle management
- ✅ **Security**: RLS, encryption, and access control
- ✅ **Observability**: Comprehensive metrics and logging
- ✅ **Maintainability**: Clear structure and documentation

Estimated Storage (per year):
- 50 million jobs: ~25 GB
- 500 million queue items: ~150 GB
- 1 billion logs: ~400 GB
- **Total: ~600 GB per year**

Retention: 2 years = **1.2 TB** (with daily cleanup)
