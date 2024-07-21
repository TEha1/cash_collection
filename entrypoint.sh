#!/bin/sh

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Run scheduled jobs
echo "Run scheduled jobs..."
python manage.py crontab add

# Start the server
echo "Starting server..."
exec "$@"
