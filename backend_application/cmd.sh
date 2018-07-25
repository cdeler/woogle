#!/bin/bash

set -e

if [ "$ENV" = 'DEV' ]; then
  echo "Running Development Server"
  exec python "manage.py" runserver 0.0.0.0:8000
else
  echo "Running Production Server"
  exec uwsgi --ini /app/woogle/uwsgi.ini --http :8000

fi