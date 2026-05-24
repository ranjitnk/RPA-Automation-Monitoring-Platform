-- PostgreSQL Operational Scripts & Maintenance for Observability Platform
-- Run these scripts regularly for optimal database performance

-- ============================================================================
-- SECTION 1: DATA RETENTION & CLEANUP
-- ============================================================================

-- Daily cleanup script (run via cron job every day)
-- Cleanup old logs (keep 90 days)
DELETE FROM orchestrator_logs 
WHERE timestamp < NOW() - INTERVAL '90 days';

-- Archive and cleanup old queue items (keep 1 year)
CREATE TEMP TABLE queue_items_to_archive AS
SELECT * FROM queue_items 
WHERE created_at < NOW() - INTERVAL '1 year'
  AND status IN ('Completed', 'Failed');

INSERT INTO queue_items_archive SELECT * FROM queue_items_to_archive;
DELETE FROM queue_items WHERE id IN (SELECT id FROM queue_items_to_archive);

-- Mark old soft-deleted records for permanent deletion (keep 30 days of deleted records)
DELETE FROM jobs WHERE deleted_at < NOW() - INTERVAL '30 days';
DELETE FROM robots WHERE deleted_at < NOW() - INTERVAL '30 days';
DELETE FROM alerts WHERE deleted_at < NOW() - INTERVAL '30 days';
DELETE FROM audit_logs WHERE deleted_at < NOW() - INTERVAL '30 days';

-- ============================================================================
-- SECTION 2: MATERIALIZED VIEWS FOR ANALYTICS
-- ============================================================================

-- Daily job statistics (refresh daily)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_job_stats AS
SELECT 
    DATE(start_time) as report_date,
    robot_id,
    status,
    COUNT(*) as job_count,
    AVG(COALESCE(duration_seconds, 0)) as avg_duration_sec,
    MAX(duration_seconds) as max_duration_sec,
    MIN(duration_seconds) as min_duration_sec,
    SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_count,
    SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) as failed_count,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) / 
        NULLIF(COUNT(*), 0), 2
    ) as success_rate_percent
FROM jobs
WHERE start_time > NOW() - INTERVAL '90 days'
  AND deleted_at IS NULL
GROUP BY DATE(start_time), robot_id, status
ORDER BY report_date DESC, robot_id;

CREATE INDEX IF NOT EXISTS idx_mv_daily_job_stats_date ON mv_daily_job_stats(report_date DESC);
CREATE INDEX IF NOT EXISTS idx_mv_daily_job_stats_robot ON mv_daily_job_stats(robot_id);

-- Hourly alert statistics (refresh hourly)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_hourly_alert_stats AS
SELECT 
    DATE_TRUNC('hour', created_at) as hour_timestamp,
    severity,
    status,
    COUNT(*) as alert_count,
    COUNT(CASE WHEN acknowledged_at IS NULL THEN 1 END) as unacknowledged_count
FROM alerts
WHERE created_at > NOW() - INTERVAL '7 days'
  AND deleted_at IS NULL
GROUP BY DATE_TRUNC('hour', created_at), severity, status
ORDER BY hour_timestamp DESC;

CREATE INDEX IF NOT EXISTS idx_mv_hourly_alerts_time ON mv_hourly_alert_stats(hour_timestamp DESC);

-- Robot health snapshot (refresh every 15 minutes)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_robot_health_snapshot AS
SELECT 
    r.id,
    r.name,
    r.status,
    COUNT(j.id) as jobs_last_24h,
    SUM(CASE WHEN j.status = 'Completed' THEN 1 ELSE 0 END) as completed_jobs,
    SUM(CASE WHEN j.status = 'Failed' THEN 1 ELSE 0 END) as failed_jobs,
    ROUND(
        100.0 * SUM(CASE WHEN j.status = 'Completed' THEN 1 ELSE 0 END) / 
        NULLIF(COUNT(j.id), 0), 2
    ) as success_rate,
    MAX(j.end_time) as last_job_time,
    r.last_activity
FROM robots r
LEFT JOIN jobs j ON r.id = j.robot_id AND j.start_time > NOW() - INTERVAL '1 day'
WHERE r.deleted_at IS NULL
GROUP BY r.id, r.name, r.status, r.last_activity
ORDER BY r.name;

CREATE INDEX IF NOT EXISTS idx_robot_health_status ON mv_robot_health_snapshot(status);

-- Queue performance metrics (refresh daily)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_queue_performance AS
SELECT 
    q.id,
    q.name,
    q.item_count,
    q.success_count,
    q.failed_count,
    COUNT(CASE WHEN qi.status IN ('Pending', 'Processing') THEN 1 END) as active_items,
    AVG(CASE WHEN qi.status = 'Completed' THEN qi.duration_seconds ELSE NULL END) as avg_processing_time_sec,
    MAX(CASE WHEN qi.status IN ('Pending', 'Processing') THEN EXTRACT(EPOCH FROM (NOW() - qi.created_at))/60 END) as max_wait_time_min
FROM queues q
LEFT JOIN queue_items qi ON q.id = qi.queue_id AND qi.deleted_at IS NULL
WHERE q.deleted_at IS NULL
GROUP BY q.id, q.name, q.item_count, q.success_count, q.failed_count;

-- Refresh materialized views
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_job_stats;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_hourly_alert_stats;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_robot_health_snapshot;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_queue_performance;

-- ============================================================================
-- SECTION 3: AUDIT TRIGGER IMPLEMENTATION
-- ============================================================================

-- Create audit trigger function
CREATE OR REPLACE FUNCTION audit_table_changes()
RETURNS TRIGGER AS $$
DECLARE
    v_user_id INTEGER;
    v_old_row JSONB;
    v_new_row JSONB;
    v_changes JSONB;
BEGIN
    -- Get current user from app context (set by application)
    v_user_id := COALESCE(
        current_setting('app.user_id', true)::INTEGER,
        NULL
    );
    
    v_old_row := CASE WHEN TG_OP = 'DELETE' OR TG_OP = 'UPDATE' THEN row_to_json(OLD) ELSE NULL END;
    v_new_row := CASE WHEN TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN row_to_json(NEW) ELSE NULL END;
    
    -- Calculate changes (delta) for updates
    IF TG_OP = 'UPDATE' THEN
        v_changes := (v_new_row::jsonb - v_old_row::jsonb);
    ELSE
        v_changes := NULL;
    END IF;
    
    -- Insert audit log
    INSERT INTO audit_logs (
        user_id,
        action,
        resource_type,
        resource_id,
        old_values,
        new_values,
        changes,
        ip_address,
        user_agent,
        status,
        timestamp
    ) VALUES (
        v_user_id,
        TG_ARGV[0]::VARCHAR,
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        v_old_row,
        v_new_row,
        v_changes,
        COALESCE(inet_client_addr(), '0.0.0.0'::inet),
        current_setting('app.user_agent', true),
        'Success',
        CURRENT_TIMESTAMP
    );
    
    RETURN COALESCE(NEW, OLD);
EXCEPTION WHEN OTHERS THEN
    -- Log audit failures but don't break the transaction
    INSERT INTO audit_logs (
        action,
        resource_type,
        resource_id,
        status,
        error_message,
        timestamp
    ) VALUES (
        TG_ARGV[0]::VARCHAR,
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        'Failure',
        SQLERRM,
        CURRENT_TIMESTAMP
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Attach audit triggers to key tables
CREATE TRIGGER audit_jobs AFTER INSERT OR UPDATE OR DELETE ON jobs
FOR EACH ROW EXECUTE FUNCTION audit_table_changes('MANAGE_JOBS');

CREATE TRIGGER audit_robots AFTER INSERT OR UPDATE OR DELETE ON robots
FOR EACH ROW EXECUTE FUNCTION audit_table_changes('MANAGE_ROBOTS');

CREATE TRIGGER audit_alerts AFTER INSERT OR UPDATE OR DELETE ON alerts
FOR EACH ROW EXECUTE FUNCTION audit_table_changes('MANAGE_ALERTS');

CREATE TRIGGER audit_users AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION audit_table_changes('MANAGE_USERS');

-- ============================================================================
-- SECTION 4: QUEUE AGGREGATION TRIGGERS
-- ============================================================================

-- Update queue item counts when queue_items change
CREATE OR REPLACE FUNCTION update_queue_counts()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE queues 
    SET 
        item_count = (SELECT COUNT(*) FROM queue_items WHERE queue_id = COALESCE(NEW.queue_id, OLD.queue_id)),
        success_count = (SELECT COUNT(*) FROM queue_items WHERE queue_id = COALESCE(NEW.queue_id, OLD.queue_id) AND status = 'Completed'),
        failed_count = (SELECT COUNT(*) FROM queue_items WHERE queue_id = COALESCE(NEW.queue_id, OLD.queue_id) AND status = 'Failed'),
        processing_count = (SELECT COUNT(*) FROM queue_items WHERE queue_id = COALESCE(NEW.queue_id, OLD.queue_id) AND status IN ('Processing', 'Retrying')),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = COALESCE(NEW.queue_id, OLD.queue_id);
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_queue_counts
AFTER INSERT OR UPDATE OR DELETE ON queue_items
FOR EACH ROW EXECUTE FUNCTION update_queue_counts();

-- ============================================================================
-- SECTION 5: MONITORING QUERIES
-- ============================================================================

-- Query 1: Find slow jobs (jobs taking longer than average)
-- Run: SELECT ... FROM slow_jobs
CREATE OR REPLACE VIEW v_slow_jobs AS
SELECT 
    j.id,
    j.name,
    r.name as robot_name,
    j.start_time,
    j.duration_seconds,
    (SELECT AVG(duration_seconds) FROM jobs WHERE status = 'Completed' AND robot_id = j.robot_id) as avg_robot_duration,
    CASE 
        WHEN j.duration_seconds > (SELECT AVG(duration_seconds) * 1.5 FROM jobs WHERE status = 'Completed' AND robot_id = j.robot_id)
        THEN 'SLOW'
        ELSE 'NORMAL'
    END as performance_status
FROM jobs j
LEFT JOIN robots r ON j.robot_id = r.id
WHERE j.status = 'Completed'
  AND j.start_time > NOW() - INTERVAL '7 days'
  AND j.deleted_at IS NULL
ORDER BY j.duration_seconds DESC;

-- Query 2: Robot status dashboard
-- Run daily to identify problematic robots
CREATE OR REPLACE VIEW v_robot_status_dashboard AS
SELECT 
    r.id,
    r.name,
    m.name as machine_name,
    r.status,
    r.execution_sessions,
    r.last_activity,
    EXTRACT(HOUR FROM (NOW() - r.last_activity)) as hours_since_activity,
    COUNT(j.id) as jobs_last_7days,
    SUM(CASE WHEN j.status = 'Failed' THEN 1 ELSE 0 END) as failed_jobs_7days,
    ROUND(100.0 * SUM(CASE WHEN j.status = 'Completed' THEN 1 ELSE 0 END) / NULLIF(COUNT(j.id), 0), 2) as success_rate
FROM robots r
LEFT JOIN machines m ON r.machine_id = m.id
LEFT JOIN jobs j ON r.id = j.robot_id AND j.start_time > NOW() - INTERVAL '7 days'
WHERE r.deleted_at IS NULL
GROUP BY r.id, r.name, m.name, r.status, r.execution_sessions, r.last_activity
ORDER BY r.name;

-- Query 3: Detect stuck queue items
-- Items that have been in 'Processing' status too long (> 30 minutes)
CREATE OR REPLACE VIEW v_stuck_queue_items AS
SELECT 
    qi.id,
    qi.reference_id,
    q.name as queue_name,
    qi.status,
    qi.start_time,
    EXTRACT(MINUTE FROM (NOW() - qi.start_time)) as processing_minutes,
    j.name as job_name,
    r.name as robot_name
FROM queue_items qi
LEFT JOIN queues q ON qi.queue_id = q.id
LEFT JOIN jobs j ON qi.job_id = j.id
LEFT JOIN robots r ON j.robot_id = r.id
WHERE qi.status IN ('Processing', 'Retrying')
  AND qi.start_time < NOW() - INTERVAL '30 minutes'
  AND qi.deleted_at IS NULL
ORDER BY qi.start_time;

-- Query 4: Alert trends
CREATE OR REPLACE VIEW v_alert_trends AS
SELECT 
    DATE(created_at) as alert_date,
    severity,
    COUNT(*) as alert_count,
    COUNT(CASE WHEN status = 'Resolved' THEN 1 END) as resolved_count,
    ROUND(100.0 * COUNT(CASE WHEN status = 'Resolved' THEN 1 END) / NULLIF(COUNT(*), 0), 2) as resolution_rate
FROM alerts
WHERE created_at > NOW() - INTERVAL '30 days'
  AND deleted_at IS NULL
GROUP BY DATE(created_at), severity
ORDER BY alert_date DESC, severity;

-- Query 5: Top failing processes
CREATE OR REPLACE VIEW v_top_failing_processes AS
SELECT 
    j.name as process_name,
    COUNT(*) as total_executions,
    SUM(CASE WHEN j.status = 'Failed' THEN 1 ELSE 0 END) as failed_executions,
    ROUND(100.0 * SUM(CASE WHEN j.status = 'Failed' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) as failure_rate,
    AVG(j.duration_seconds) as avg_duration_sec
FROM jobs j
WHERE j.start_time > NOW() - INTERVAL '30 days'
  AND j.deleted_at IS NULL
GROUP BY j.name
HAVING COUNT(*) > 5
ORDER BY failure_rate DESC;

-- ============================================================================
-- SECTION 6: PERFORMANCE ANALYSIS
-- ============================================================================

-- Query: Find unused indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
  AND idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- Query: Table size analysis
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename, 'main')) as main_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename, 'toast')) as toast_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename, 'fsm')) as fsm_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename, 'vm')) as vm_size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Query: Cache hit ratio (should be > 99%)
SELECT 
    sum(heap_blks_read) as heap_read,
    sum(heap_blks_hit) as heap_hit,
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;

-- Query: Long-running queries
SELECT 
    pid,
    now() - pg_stat_activity.query_start as duration,
    query,
    state
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > INTERVAL '5 minutes';

-- ============================================================================
-- SECTION 7: MAINTENANCE TASKS
-- ============================================================================

-- Run ANALYZE to update statistics (weekly)
ANALYZE jobs;
ANALYZE queue_items;
ANALYZE alerts;
ANALYZE orchestrator_logs;
ANALYZE ai_traces;

-- Run VACUUM to reclaim space (daily during off-peak)
VACUUM ANALYZE jobs;
VACUUM ANALYZE queue_items;
VACUUM ANALYZE alerts;

-- Reindex large tables (monthly during maintenance window)
REINDEX TABLE CONCURRENTLY jobs;
REINDEX TABLE CONCURRENTLY queue_items;
REINDEX TABLE CONCURRENTLY alerts;
REINDEX TABLE CONCURRENTLY orchestrator_logs;

-- ============================================================================
-- SECTION 8: BACKUP & RECOVERY
-- ============================================================================

-- Backup script (run daily)
-- psql -U postgres -d observability_db -h localhost \
--     --command="VACUUM FULL ANALYZE"
-- 
-- pg_dump -U postgres -d observability_db -h localhost \
--     --format=custom \
--     --compress=9 \
--     --file=/backups/observability_$(date +%Y%m%d).dump

-- Point-in-time recovery configuration
-- WAL level should be 'replica' or higher
-- archive_mode = on
-- archive_command = 'test ! -f /wal_archive/%f && cp %p /wal_archive/%f'

-- ============================================================================
-- SECTION 9: CONFIG SETTINGS (postgresql.conf)
-- ============================================================================

-- Recommended settings for observability platform:
/*
# Connection and process management
max_connections = 200
superuser_reserved_connections = 10

# Memory settings
shared_buffers = 4GB              -- 25% of system RAM
effective_cache_size = 12GB       -- 75% of system RAM
work_mem = 256MB                  -- (RAM / max_connections) / 2
maintenance_work_mem = 1GB
wal_buffers = 16MB

# Query tuning
random_page_cost = 1.1            -- For SSD
effective_io_concurrency = 200    -- For SSD
checkpoint_timeout = 15min
checkpoint_completion_target = 0.9

# Logging
log_min_duration_statement = 1000  -- Log queries > 1 second
log_statement = 'all'
log_connections = on
log_disconnections = on
log_duration = on

# Autovacuum (tuned for high-volume tables)
autovacuum = on
autovacuum_max_workers = 4
autovacuum_naptime = 10s
autovacuum_vacuum_threshold = 50
autovacuum_vacuum_scale_factor = 0.01
autovacuum_analyze_threshold = 50
autovacuum_analyze_scale_factor = 0.005
*/

-- ============================================================================
-- END OF OPERATIONAL SCRIPTS
-- ============================================================================
