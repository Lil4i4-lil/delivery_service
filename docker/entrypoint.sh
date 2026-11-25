#!/usr/bin/env bash
set -euo pipefail

cd /app/delivery

until python -c "import psycopg2, os; psycopg2.connect(os.environ['DATABASE_URL'])" 2>/dev/null; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done

if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
    python manage.py migrate --noinput
    python manage.py seed_parcel_types
fi

if [ "${LOAD_KNOWLEDGE:-0}" = "1" ]; then
    python manage.py load_knowledge || true
fi

exec "$@"