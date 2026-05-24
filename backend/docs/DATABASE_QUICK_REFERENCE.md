# PostgreSQL Schema - Quick Reference Guide

## 📋 Documentation Files

| File | Purpose | Audience |
|------|---------|----------|
| **DATABASE_SCHEMA.md** | Complete schema design with all details | Architects, DBAs |
| **20250524_0002_create_observability_schema.sql** | Executable SQL DDL for schema creation | DevOps, DBAs |
| **DATABASE_OPERATIONS.sql** | Operational scripts, triggers, views, monitoring | DevOps, Operations |
| **DATABASE_IMPLEMENTATION_GUIDE.md** | Backend integration guide, queries, examples | Backend Developers |
| **DATABASE_QUICK_REFERENCE.md** | This file - quick lookup guide | All Teams |

---

## 🗂️ Core Tables (12 Total)

### User Management
- **roles** - System and custom roles with permission matrix
- **users** - User accounts with RBAC

### Infrastructure
- **machines** - Physical/virtual machines hosting robots
- **robots** - Automation robots with status tracking

### Automation Execution
- **jobs** - RPA job execution history
- **queues** - Work queue definitions
- **queue_items** - Individual queue items with processing status

### Monitoring & Alerting
- **alerts** - System alerts with severity and status
- **ai_traces** - ML model predictions and anomaly detection
- **orchestrator_logs** - Execution logs and errors

### Analytics & Compliance
- **sla_metrics** - Daily SLA tracking and compliance
- **audit_logs** - Immutable audit trail of all changes

---

## 🔑 Key Constraints & Relationships

### Foreign Keys
```
users.role_id            → roles.id
robots.machine_id        → machines.id
jobs.robot_id            → robots.id
queue_items.queue_id     → queues.id
queue_items.job_id       → jobs.id (optional)
alerts.job_id            → jobs.id (optional)
alerts.robot_id          → robots.id (optional)
alerts.acknowledged_by   → users.id (optional)
alerts.resolved_by       → users.id (optional)
orchestrator_logs.job_id → jobs.id (optional)
orchestrator_logs.robot_id → robots.id (optional)
orchestrator_logs.user_id → users.id (optional)
ai_traces.job_id         → jobs.id (optional)
ai_traces.robot_id       → robots.id (optional)
audit_logs.user_id       → users.id (optional)
```

### Unique Constraints
```
users.email
users.username
machines.name
machines.orchestrator_machine_id
robots.lic_robot_id
robots.orchestrator_robot_id
queues.name
queues.orchestrator_queue_id
jobs.orchestrator_job_id
queue_items.orchestrator_queue_item_id
ai_traces.id (primary key)
sla_metrics (process_name, metric_date) - composite unique
```

---

## 📊 Table Sizes & Partitioning Strategy

| Table | Expected Daily Volume | Retention | Partitioning |
|-------|----------------------|-----------|---------------|
| jobs | 100K - 1M | 2 years | Monthly by start_time |
| queue_items | 1M - 10M | 1 year | Daily by created_at |
| alerts | 10K - 100K | 2 years | Weekly by created_at |
| orchestrator_logs | 10M - 100M | 90 days | Daily by timestamp |
| ai_traces | 1M - 10M | 1 year | Daily by timestamp |
| sla_metrics | 365 | 5 years | Monthly by metric_date |
| audit_logs | 100K - 1M | 7 years | Monthly by timestamp |
| robots | 100-1K | Forever | None |
| machines | 50-500 | Forever | None |
| queues | 10-100 | Forever | None |
| users | 10-100 | Forever | None |
| roles | 4-10 | Forever | None |

**Total Estimated Storage**: ~600 GB for 2-year retention

---

## 🏃 Quick Setup Commands

```bash
# Create database
createdb -U postgres observability_db

# Apply schema
psql -U postgres -d observability_db -f alembic/versions/20250524_0002_create_observability_schema.sql

# Apply operations (triggers, views, etc.)
psql -U postgres -d observability_db -f docs/DATABASE_OPERATIONS.sql

# Verify installation
psql -U postgres -d observability_db -c "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;"

# Connection string
postgresql://postgres:password@localhost:5432/observability_db
```

---

## 🔍 Common Queries

### Get Recent Jobs
```sql
SELECT j.*, r.name as robot_name 
FROM jobs j 
LEFT JOIN robots r ON j.robot_id = r.id 
ORDER BY j.start_time DESC LIMIT 100;
```

### Get Robot Status
```sql
SELECT * FROM mv_robot_health_snapshot 
ORDER BY name;
```

### Get Active Alerts
```sql
SELECT * FROM alerts 
WHERE status IN ('New', 'Acknowledged') 
ORDER BY severity DESC, created_at DESC;
```

### Get Queue Performance
```sql
SELECT * FROM mv_queue_performance 
ORDER BY name;
```

### Get Stuck Queue Items
```sql
SELECT * FROM v_stuck_queue_items 
WHERE processing_minutes > 30;
```

### Get Daily SLA Metrics
```sql
SELECT * FROM sla_metrics 
WHERE metric_date = CURRENT_DATE 
ORDER BY process_name;
```

### Get Audit Trail by User
```sql
SELECT * FROM audit_logs 
WHERE user_id = :user_id 
ORDER BY timestamp DESC;
```

### Get Anomalies
```sql
SELECT * FROM ai_traces 
WHERE is_anomaly = TRUE 
ORDER BY timestamp DESC;
```

---

## 📈 Performance Optimization Tips

1. **Always use WHERE clauses** - Avoid full table scans
2. **Use indexes on**:
   - Foreign keys (auto-indexed)
   - Status columns
   - Timestamp columns
   - Frequently filtered columns

3. **Partition large tables** by time (monthly/daily)
4. **Use materialized views** for complex analytics
5. **Cache frequently accessed data** (users, roles)
6. **Run ANALYZE** after bulk operations
7. **Monitor query performance** with EXPLAIN ANALYZE
8. **Use connection pooling** (PgBouncer)

### Expected Query Times
- Single record lookup: < 1ms
- List with pagination: 10-100ms
- Aggregation query: 100-500ms
- Complex join: 500ms-2s

---

## 🔐 Security Best Practices

1. **Use SSL/TLS** for connections
2. **Enable Row-Level Security** (RLS) for sensitive data
3. **Hash passwords** with bcrypt/argon2
4. **Encrypt** API keys and secrets
5. **Audit all changes** via audit_logs table
6. **Use parameterized queries** to prevent SQL injection
7. **Set app context** for user tracking:
   ```sql
   SET app.user_id = 123;
   SET app.user_role = 'admin';
   ```
8. **Regular backups** with point-in-time recovery

---

## 🛠️ Maintenance Schedule

| Task | Frequency | Duration | Impact |
|------|-----------|----------|--------|
| ANALYZE | Daily (off-peak) | 5-15 min | None (statistics only) |
| VACUUM | Daily (off-peak) | 10-30 min | None (cleanup) |
| REINDEX | Monthly (maintenance) | 30-60 min | Locks table |
| Backup | Daily | 10-20 min | Low (read-only) |
| Refresh MV | Per schedule | 1-5 min | Blocks concurrent refresh |
| Retention cleanup | Daily | 5-10 min | Cascade deletes |

---

## 📊 Materialized Views

| View | Refresh Rate | Use Case |
|------|--------------|----------|
| mv_daily_job_stats | Daily | Daily reports, trends |
| mv_hourly_alert_stats | Hourly | Alert dashboard |
| mv_robot_health_snapshot | 15 min | Robot status page |
| mv_queue_performance | Daily | Queue analytics |

---

## 🚨 Monitoring & Alerts

### Key Metrics to Monitor
```sql
-- Database size
SELECT pg_size_pretty(pg_database_size('observability_db'));

-- Connection count
SELECT count(*) FROM pg_stat_activity;

-- Cache hit ratio (target > 99%)
SELECT ROUND(100.0 * SUM(heap_blks_hit) / 
    (SUM(heap_blks_hit) + SUM(heap_blks_read)), 2) 
FROM pg_statio_user_tables;

-- Slow queries
SELECT query, calls, mean_time FROM pg_stat_statements 
WHERE mean_time > 1000 ORDER BY mean_time DESC;

-- Table bloat
SELECT * FROM pg_stats WHERE n_dead_tup > 10000;
```

### Alert Thresholds
- Database size growth > 50% month-over-month
- Cache hit ratio < 99%
- Queries taking > 5 seconds
- Connection count > 80% of max
- Disk space < 20% available
- Replication lag > 1 minute

---

## 🔄 Backup & Recovery

### Daily Backup
```bash
pg_dump -U postgres -d observability_db \
    --format=custom --compress=9 \
    --file=/backups/observability_$(date +%Y%m%d).dump
```

### Point-in-Time Recovery
```bash
# Restore to specific time
pg_restore -U postgres -d observability_db_restore \
    /backups/observability_20260524.dump
```

### Recovery Time Objective (RTO)
- Full restore: < 30 minutes
- Point-in-time: < 60 minutes

---

## 🐛 Troubleshooting

| Issue | Diagnosis | Solution |
|-------|-----------|----------|
| Slow queries | EXPLAIN ANALYZE | Add indexes, increase work_mem |
| High disk usage | pg_total_relation_size() | VACUUM FULL, archive old data |
| Connection pool exhausted | pg_stat_activity | Increase pool size, check for leaks |
| Locks blocking queries | pg_locks | Kill long-running queries |
| Slow INSERTS | EXPLAIN INSERT | Disable indexes during bulk load |
| Missing data | Check audit_logs | Verify deletes intentional |
| Replication lag | pg_last_wal_receive_lsn() | Scale standby server |

---

## 📝 Common Code Patterns

### Insert with User Audit
```python
# Python example
user_id = get_current_user_id()
connection.execute(
    text("SET app.user_id = :user_id"),
    {"user_id": user_id}
)
# Insert triggers audit_logs automatically
```

### Soft Delete
```sql
-- Mark as deleted, not permanent removal
UPDATE jobs SET deleted_at = NOW() WHERE id = 123;

-- Query excludes deleted
SELECT * FROM jobs WHERE deleted_at IS NULL;
```

### Bulk Insert
```sql
-- Optimize bulk operations
TRUNCATE jobs_staging;
COPY jobs_staging FROM '/path/to/file.csv' WITH CSV;
INSERT INTO jobs SELECT * FROM jobs_staging;
```

---

## 📞 Support & Resources

### PostgreSQL Documentation
- https://www.postgresql.org/docs/current/
- Performance Tuning: https://wiki.postgresql.org/wiki/Performance_Optimization
- JSONB: https://www.postgresql.org/docs/current/datatype-json.html

### Alembic Migrations
- https://alembic.sqlalchemy.org/
- Auto-generate migrations: `alembic revision --autogenerate -m "message"`

### Tools
- **pgAdmin**: Web UI for database management
- **DBeaver**: Multi-database IDE
- **Datagrip**: IntelliJ-based IDE
- **pgBench**: Performance testing

---

## 🎯 Implementation Checklist

- [ ] Create database
- [ ] Apply schema DDL
- [ ] Apply operations (triggers, views)
- [ ] Create initial roles
- [ ] Create admin user
- [ ] Configure connection pooling
- [ ] Enable backups
- [ ] Set up monitoring
- [ ] Configure alerts
- [ ] Test data import procedures
- [ ] Verify query performance
- [ ] Document custom procedures
- [ ] Train operations team
- [ ] Schedule maintenance tasks
- [ ] Document disaster recovery plan

---

## 📞 Quick Contact Scenarios

**Database is down**
1. Check pg_stat_activity for blocking queries
2. Review recent queries in pg_stat_statements
3. Check disk space: `df -h /var/lib/postgresql`
4. Review PostgreSQL logs
5. Initiate failover if standby available

**Performance degradation**
1. Run ANALYZE to update statistics
2. Check for missing indexes (pg_stat_user_indexes)
3. Review slow query log
4. Run EXPLAIN ANALYZE on top queries
5. Check cache hit ratio

**Data corruption suspected**
1. Take immediate backup
2. Run pg_dump to verify consistency
3. Check transaction logs
4. Review audit_logs for suspicious activity
5. Contact database team for investigation

---

**Last Updated**: May 24, 2026  
**Schema Version**: 1.0  
**PostgreSQL Version**: 12+  
**Status**: Production Ready ✅
