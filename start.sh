#!/usr/bin/env bash
set -e

echo "Checking database migrations..."

# Check current migration
CURRENT=$(alembic current)
HEAD=$(alembic heads)

if [ "$CURRENT" != "$HEAD" ]; then
    echo "Database not at latest revision. Running migrations..."
    alembic upgrade head
else
    echo "Database already up to date."
fi

echo "Starting Gunicorn..."

exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 2