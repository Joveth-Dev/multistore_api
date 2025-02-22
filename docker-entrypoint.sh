#!/bin/bash

# Apply database migrations
echo "Making migrations..."
python manage.py makemigrations
echo "Migrating to database..."
python manage.py migrate

echo "Collect static files..."
python manage.py collectstatic --no-input

# Start server
echo "Starting server..."
gunicorn multistore_api.wsgi:application --bind=0.0.0.0:8000 --reload --reload-engine='inotify'
