#!/bin/sh

echo "Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "PostgreSQL started successfully!"

if [ "$1" = "gunicorn" ] || [ "$run_migrations" = "true" ]; then
    echo "Running database migrations..."
    python manage.py migrate

    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

exec "$@"