#!/bin/bash

echo "Migrating to database..."
python manage.py migrate

echo "Collect static files..."
python manage.py collectstatic --no-input

# management commands
echo "Executing management command: create_superuser"
python manage.py create_superuser
echo "Executing management command: create_store_owner_group"
python manage.py create_store_owner_group

echo "Starting server..."
gunicorn multistore_api.wsgi:application --bind=0.0.0.0:8000 --reload --reload-engine='inotify'
