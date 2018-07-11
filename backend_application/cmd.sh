#!/bin/bash
set -e

# while ! curl db:5432; do sleep 3; done
# while ! nc -z db 5432; do sleep 3; done
sleep 5

if [ "$ENV" = 'DEV' ]; then
  echo "Running Development Server"
  exec python "manage.py" runserver 0.0.0.0:8000
else
  echo "Running Production Server"
  exec uwsgi --http 0.0.0.0:9090 --wsgi-file /app/manage.py \
             --callable app --stats 0.0.0.0:9191
fi
