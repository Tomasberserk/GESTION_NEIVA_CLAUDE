# 13 — Runbook

## Standard Operating Procedures (SOP)

This runbook defines operational recovery procedures for the single deployable application.

## 1. Database backups and disaster recovery

- **Daily Backup Command (automated cron):**
  ```bash
  pg_dump -Fc -v -d "$DATABASE_URL" -f "backup_$(date +%Y%m%d_%H%M%S).dump"
  ```
- **Disaster Recovery Restore (Target < 30 minutes):**
  ```bash
  pg_restore --clean --if-exists --no-acl --no-owner -d "$DATABASE_URL" backup_target.dump
  ```

## 2. Applying migrations in production

Database migrations are executed automatically during Render deployment or manually via:
```bash
alembic upgrade head
```
If a migration fails, verify the schema state using `alembic current` and rollback with
`alembic downgrade -1` before redeploying.

## 3. Secret and key rotation

1. Generate new 64-character hex secret: `openssl rand -hex 32`.
2. Update `SECRET_KEY` and `SUPERADMIN_KEY` in the Render Environment Variables tab.
3. Trigger a rolling restart: active JWT tokens remain valid until expiration (480 min).

## 4. Mitigating high lock contention on checkout

If `pg_stat_activity` shows queries waiting on `productos` locks during rush hour:
1. Identify blocking PID: `SELECT pid, query, age(clock_timestamp(), query_start) FROM pg_stat_activity WHERE wait_event_type = 'Lock';`
2. Terminate hung long-running read query: `SELECT pg_cancel_backend(pid);`

---

**Related:** [`./observability.md`](./observability.md) · [`../06-data/migrations.md`](../06-data/migrations.md)
