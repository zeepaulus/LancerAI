# Deployment Rollback Runbook

## Normal Deployment State

`scripts/deploy/compose_deploy.sh` writes deployment metadata under `.deploy/` on the server:

- `.deploy/current.env`: current backend/frontend image tags.
- `.deploy/previous.env`: previous backend/frontend image tags.
- `.deploy/next.env`: in-progress deployment state.

PostgreSQL backups are written to `backups/postgres-<timestamp>.sql` before migrations.

## Roll Back Application Images

From the deployment host:

```bash
cd /path/to/lancerai
BACKEND_IMAGE=ghcr.io/<owner>/lancerai-backend:<previous-tag> \
FRONTEND_IMAGE=ghcr.io/<owner>/lancerai-frontend:<previous-tag> \
ENV_FILE=.env \
COMPOSE_PROJECT_NAME=lancerai-production \
docker compose -f docker-compose.prod.yml up -d backend celery_worker frontend nginx
```

Or use the helper:

```bash
cd /path/to/lancerai
ENV_FILE=.env COMPOSE_PROJECT_NAME=lancerai-production bash scripts/deploy/compose_rollback.sh
```

## Failed Migration Handling

Alembic migrations can change data. Image rollback does not automatically undo schema or data migrations.

1. Stop application writers if the database is in an uncertain state.
2. Inspect the failed migration and Alembic current revision.
3. If safe, apply an Alembic downgrade for the failed revision.
4. If downgrade is unsafe or unavailable, restore the pre-deploy PostgreSQL backup.
5. Re-run `/ready` before opening traffic.

## Restore Database Backup

Example:

```bash
cd /path/to/lancerai
docker compose -f docker-compose.prod.yml exec -T postgres dropdb -U "$POSTGRES_USER" "$POSTGRES_DB"
docker compose -f docker-compose.prod.yml exec -T postgres createdb -U "$POSTGRES_USER" "$POSTGRES_DB"
docker compose -f docker-compose.prod.yml exec -T postgres psql -U "$POSTGRES_USER" "$POSTGRES_DB" < backups/postgres-YYYYMMDDTHHMMSSZ.sql
```

Confirm the exact database name and backup file before running destructive restore commands.

## Verify Health

```bash
curl -fsS http://localhost/health
curl -fsS http://localhost/ready
curl -fsS http://localhost/
docker compose -f docker-compose.prod.yml ps
```

## Communication Checklist

- State which image tag failed and which tag is restored.
- State whether migrations ran.
- State whether a DB backup restore was required.
- Link the failed GitHub Actions run.
- Record follow-up work before the next production deploy.
