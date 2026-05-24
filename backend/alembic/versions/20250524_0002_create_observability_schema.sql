-- PostgreSQL Schema for UiPath Observability Platform
-- Created: 2026-05-24
-- Version: 1.0
-- Description: Complete schema with all tables, relationships, indexes, and constraints

-- ============================================================================
-- ROLES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '[]',
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ck_role_permissions CHECK (permissions IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name);

-- Insert system roles
INSERT INTO roles (name, description, permissions, is_system) VALUES
('admin', 'Full system access', '["*:*"]'::jsonb, TRUE),
('manager', 'Manage jobs and alerts', '["jobs:*", "alerts:*", "robots:read"]'::jsonb, TRUE),
('user', 'Read own resources', '["jobs:read", "alerts:read", "robots:read"]'::jsonb, TRUE),
('viewer', 'Read-only access', '["*:read"]'::jsonb, TRUE)
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- USERS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
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
    
    CONSTRAINT fk_user_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_users_role_id ON users(role_id);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active) WHERE deleted_at IS NULL;

-- ============================================================================
-- MACHINES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS machines (
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

CREATE INDEX IF NOT EXISTS idx_machines_name ON machines(name) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_machines_enabled ON machines(is_enabled) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_machines_heartbeat ON machines(last_heartbeat DESC);
CREATE INDEX IF NOT EXISTS idx_machines_orch_id ON machines(orchestrator_machine_id);

-- ============================================================================
-- ROBOTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS robots (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    machine_id INTEGER NOT NULL,
    robot_type VARCHAR(50) NOT NULL,
    lic_robot_id VARCHAR(100) UNIQUE,
    username VARCHAR(255),
    domain VARCHAR(255),
    is_enabled BOOLEAN DEFAULT TRUE,
    status VARCHAR(50) DEFAULT 'Offline',
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

CREATE INDEX IF NOT EXISTS idx_robots_machine_id ON robots(machine_id);
CREATE INDEX IF NOT EXISTS idx_robots_status ON robots(status) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_robots_robot_type ON robots(robot_type) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_robots_is_enabled ON robots(is_enabled) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_robots_last_activity ON robots(last_activity DESC);
CREATE INDEX IF NOT EXISTS idx_robots_tags ON robots USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_robots_orch_id ON robots(orchestrator_robot_id);

-- ============================================================================
-- JOBS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    release_id VARCHAR(100),
    robot_id INTEGER,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    status VARCHAR(50) NOT NULL,
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

CREATE INDEX IF NOT EXISTS idx_jobs_robot_id ON jobs(robot_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_jobs_start_time ON jobs(start_time DESC) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_jobs_end_time ON jobs(end_time DESC) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_release_id ON jobs(release_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_jobs_orch_id ON jobs(orchestrator_job_id);

-- ============================================================================
-- QUEUES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS queues (
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

CREATE INDEX IF NOT EXISTS idx_queues_name ON queues(name) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_queues_orch_id ON queues(orchestrator_queue_id);

-- ============================================================================
-- QUEUE ITEMS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS queue_items (
    id BIGSERIAL PRIMARY KEY,
    queue_id INTEGER NOT NULL,
    job_id INTEGER,
    reference_id VARCHAR(255),
    priority INTEGER DEFAULT 0,
    status VARCHAR(50) NOT NULL,
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

CREATE INDEX IF NOT EXISTS idx_queue_items_queue_id ON queue_items(queue_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_queue_items_status ON queue_items(status) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_queue_items_created_at ON queue_items(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_queue_items_priority ON queue_items(priority DESC) WHERE status = 'Pending';
CREATE INDEX IF NOT EXISTS idx_queue_items_due_date ON queue_items(due_date) WHERE status IN ('Pending', 'Processing');
CREATE INDEX IF NOT EXISTS idx_queue_items_orch_id ON queue_items(orchestrator_queue_item_id);

-- ============================================================================
-- ALERTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    source VARCHAR(100),
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

CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_job_id ON alerts(job_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_alerts_robot_id ON alerts(robot_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_alerts_source ON alerts(source) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_alerts_first_occurrence ON alerts(first_occurrence DESC);

-- ============================================================================
-- AI TRACES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_traces (
    id BIGSERIAL PRIMARY KEY,
    job_id INTEGER,
    robot_id INTEGER,
    trace_name VARCHAR(255) NOT NULL,
    trace_type VARCHAR(50),
    model_name VARCHAR(255),
    model_version VARCHAR(50),
    input_data JSONB,
    output_data JSONB,
    predictions JSONB,
    confidence_score NUMERIC(5, 4),
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

CREATE INDEX IF NOT EXISTS idx_ai_traces_job_id ON ai_traces(job_id);
CREATE INDEX IF NOT EXISTS idx_ai_traces_robot_id ON ai_traces(robot_id);
CREATE INDEX IF NOT EXISTS idx_ai_traces_timestamp ON ai_traces(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_ai_traces_is_anomaly ON ai_traces(is_anomaly, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_ai_traces_trace_type ON ai_traces(trace_type, timestamp DESC);

-- ============================================================================
-- ORCHESTRATOR LOGS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS orchestrator_logs (
    id BIGSERIAL PRIMARY KEY,
    job_id INTEGER,
    robot_id INTEGER,
    log_level VARCHAR(50) NOT NULL,
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

CREATE INDEX IF NOT EXISTS idx_orch_logs_timestamp ON orchestrator_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_orch_logs_log_level ON orchestrator_logs(log_level, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_orch_logs_job_id ON orchestrator_logs(job_id);
CREATE INDEX IF NOT EXISTS idx_orch_logs_robot_id ON orchestrator_logs(robot_id);
CREATE INDEX IF NOT EXISTS idx_orch_logs_correlation_id ON orchestrator_logs(correlation_id);
CREATE INDEX IF NOT EXISTS idx_orch_logs_request_id ON orchestrator_logs(request_id);

-- ============================================================================
-- SLA METRICS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS sla_metrics (
    id BIGSERIAL PRIMARY KEY,
    process_name VARCHAR(255) NOT NULL,
    metric_date DATE NOT NULL,
    total_jobs INTEGER DEFAULT 0,
    successful_jobs INTEGER DEFAULT 0,
    failed_jobs INTEGER DEFAULT 0,
    total_duration_seconds BIGINT DEFAULT 0,
    average_duration_seconds NUMERIC(10, 2),
    success_rate_percent NUMERIC(5, 2),
    target_success_rate_percent NUMERIC(5, 2) DEFAULT 99.00,
    target_average_duration_seconds NUMERIC(10, 2),
    status VARCHAR(50),
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

CREATE INDEX IF NOT EXISTS idx_sla_metrics_process_name ON sla_metrics(process_name);
CREATE INDEX IF NOT EXISTS idx_sla_metrics_metric_date ON sla_metrics(metric_date DESC);
CREATE INDEX IF NOT EXISTS idx_sla_metrics_status ON sla_metrics(status) WHERE metric_date = CURRENT_DATE;
CREATE UNIQUE INDEX IF NOT EXISTS idx_sla_metrics_process_date ON sla_metrics(process_name, metric_date);

-- ============================================================================
-- AUDIT LOGS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    request_id VARCHAR(100),
    status VARCHAR(50),
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT ck_audit_action CHECK (action IN ('CREATE', 'UPDATE', 'DELETE', 'ACKNOWLEDGE', 'RESOLVE', 'LOGIN', 'LOGOUT')),
    CONSTRAINT ck_audit_status CHECK (status IN ('Success', 'Failure'))
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action, timestamp DESC);

-- ============================================================================
-- EXTENSIONS
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

-- Summary: All tables created successfully
-- Total Tables: 12
-- Total Indexes: 50+
-- Constraints: Primary Keys, Foreign Keys, Check Constraints, Unique Constraints
