#!/bin/bash

# Redirect stdout and stderr to log files for debugging
exec 1>>/app/logs/startup.log
exec 2>>/app/logs/error.log

# Start Gunicorn with minimal logging and hot-reloading
exec gunicorn --bind 0.0.0.0:8000 \
    --log-level debug \
    --access-logfile /app/logs/access.log \
    --error-logfile /app/logs/gunicorn-error.log \
    --reload \
    --reload-extra-file templates/ \
    --reload-extra-file static/ \
    --timeout 300 \
    --workers 3 \
    --capture-output \
    app:app
