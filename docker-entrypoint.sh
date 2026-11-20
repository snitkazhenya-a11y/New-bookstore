#!/bin/sh

echo "Waiting for PostgreSQL..."
python -c "
import socket, time, os
db_host = os.environ.get('DB_HOST', 'db_a')
db_port = int(os.environ.get('DB_PORT', 5432))
while True:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((db_host, db_port))
        s.close()
        break
    except socket.error:
        time.sleep(1)
"
echo "PostgreSQL started successfully!"

if [ "$1" = "gunicorn" ] || [ "$run_migrations" = "true" ]; then
    echo "Running database migrations..."
    python manage.py migrate

    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

exec "$@"