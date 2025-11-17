# Database Migrations with Alembic

This directory contains database migration scripts for the GOST document formatter application.

## Overview

We use Alembic for database schema versioning and migrations. Alembic allows us to:
- Track database schema changes over time
- Apply and rollback migrations
- Generate migrations automatically or manually
- Work with async SQLAlchemy

## Setup

Alembic is already configured and ready to use. The configuration files are:
- `/backend/alembic.ini` - Main Alembic configuration
- `/backend/alembic/env.py` - Environment configuration (async support)
- `/backend/alembic/versions/` - Migration scripts

## Common Commands

All commands should be run from the `backend` directory.

### Check current migration status

```bash
alembic current
```

### View migration history

```bash
alembic history --verbose
```

### Create a new migration (auto-generate)

Alembic can automatically detect changes to your SQLAlchemy models:

```bash
alembic revision --autogenerate -m "Add new column to documents table"
```

**Important**: Always review auto-generated migrations before applying them!

### Create a new migration (manual)

For complex changes, create an empty migration and edit it manually:

```bash
alembic revision -m "Add custom index"
```

Then edit the generated file in `alembic/versions/`.

### Apply migrations (upgrade to latest)

```bash
alembic upgrade head
```

### Apply specific migration

```bash
alembic upgrade <revision_id>
```

### Rollback one migration

```bash
alembic downgrade -1
```

### Rollback to specific migration

```bash
alembic downgrade <revision_id>
```

### Rollback all migrations

```bash
alembic downgrade base
```

## Migration File Structure

Each migration file contains:

```python
"""Description of migration

Revision ID: 001
Revises: None
Create Date: 2024-11-17 12:00:00
"""

def upgrade() -> None:
    """Apply changes (forward migration)."""
    # Your upgrade SQL/operations
    pass

def downgrade() -> None:
    """Revert changes (rollback migration)."""
    # Your downgrade SQL/operations
    pass
```

## Best Practices

### 1. Always Review Auto-Generated Migrations

Auto-generate is convenient but not perfect. Always review migrations before applying:
- Check that all changes are captured
- Verify data type mappings
- Ensure indexes are created/dropped correctly
- Check for any custom logic needed

### 2. Test Migrations

Before deploying:
1. Test upgrade on development database
2. Test downgrade to ensure rollback works
3. Test upgrade again to verify idempotency

```bash
# Test cycle
alembic upgrade head    # Apply migration
alembic downgrade -1    # Rollback
alembic upgrade head    # Apply again
```

### 3. Data Migrations

For migrations that modify data (not just schema):

```python
def upgrade() -> None:
    # Use op.execute() for data changes
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE documents SET template_name = 'gost_vkr' WHERE template_name IS NULL")
    )
```

### 4. Handling Enums

When adding/modifying PostgreSQL enums:

```python
def upgrade() -> None:
    # Add new value to enum
    op.execute("ALTER TYPE documentstatus ADD VALUE 'archived'")

def downgrade() -> None:
    # Enums cannot be easily downgraded in PostgreSQL
    # Consider creating new enum and migrating data
    pass
```

### 5. Add Indexes for Performance

```python
def upgrade() -> None:
    op.create_index(
        'ix_documents_status_created',
        'documents',
        ['status', 'created_at']
    )

def downgrade() -> None:
    op.drop_index('ix_documents_status_created', table_name='documents')
```

## Working with Multiple Developers

### Pulling Latest Changes

When pulling code that includes new migrations:

```bash
git pull origin main
alembic upgrade head  # Apply new migrations
```

### Merge Conflicts

If two developers create migrations simultaneously:

```bash
# List migrations
alembic heads

# Merge branches (creates merge migration)
alembic merge <rev1> <rev2> -m "Merge migrations"
```

## Production Deployment

### Before Deploying

1. Test all migrations in staging environment
2. Backup production database
3. Have rollback plan ready

### Deployment Process

```bash
# 1. Stop application (to prevent writes during migration)
docker-compose down backend

# 2. Backup database
pg_dump -h localhost -U postgres gost_formatter > backup_$(date +%Y%m%d).sql

# 3. Apply migrations
docker-compose run backend alembic upgrade head

# 4. Start application
docker-compose up -d
```

### Rollback Plan

If something goes wrong:

```bash
# Rollback migrations
alembic downgrade -1

# Or restore from backup
psql -h localhost -U postgres gost_formatter < backup_20241117.sql
```

## Docker Integration

Migrations can be run in Docker:

```bash
# Apply migrations in running container
docker-compose exec backend alembic upgrade head

# Or run as one-off command
docker-compose run backend alembic upgrade head
```

### Automatic Migrations on Startup

To automatically run migrations when container starts, add to `docker-compose.yml`:

```yaml
services:
  backend:
    command: sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0"
```

**Note**: Be cautious with auto-migrations in production!

## Troubleshooting

### "Can't locate revision identified by 'XXX'"

The database's migration version doesn't match the code:

```bash
# Check database version
alembic current

# Check available migrations
alembic history

# Force stamp to specific version (careful!)
alembic stamp head
```

### "Target database is not up to date"

Apply pending migrations:

```bash
alembic upgrade head
```

### Migration fails halfway

Alembic doesn't use transactions by default for some operations. If a migration fails:

1. Check what was applied: `alembic current`
2. Manually fix database if needed
3. Mark as complete or rollback: `alembic stamp <revision>`

## Environment Variables

Migrations use the same environment variables as the application:

- `DATABASE_URL` - PostgreSQL connection string
- See `.env.example` for all variables

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
