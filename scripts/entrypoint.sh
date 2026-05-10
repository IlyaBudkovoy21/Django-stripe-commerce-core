#!/bin/sh
set -e

if [ "${DATABASE_ENGINE}" = "django.db.backends.postgresql" ]; then
  DB_HOST="${DATABASE_HOST:-db}"
  DB_PORT="${DATABASE_PORT:-5432}"

  echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."
  until nc -z "${DB_HOST}" "${DB_PORT}"; do
    sleep 1
  done
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ "${CREATE_SUPERUSER}" = "True" ] || [ "${CREATE_SUPERUSER}" = "true" ]; then
  python manage.py ensure_superuser --from-env
fi

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
