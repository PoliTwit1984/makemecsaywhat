#!/bin/bash

{
    # Redirect all stdout/stderr to /dev/null except for critical errors
    exec 1>/dev/null
    exec 2>/dev/null

    # Start Celery worker with absolute minimal logging
    celery -A celeryconfig worker --loglevel=critical --without-gossip --without-mingle --without-heartbeat &

    # Start Celery beat with absolute minimal logging
    celery -A celeryconfig beat --loglevel=critical &

    # Start Gunicorn with absolute minimal logging
    exec gunicorn --bind 0.0.0.0:8000 \
        --log-level critical \
        --access-logfile /dev/null \
        --error-logfile /dev/null \
        --reload \
        --reload-extra-file templates/ \
        --reload-extra-file static/ \
        --timeout 300 \
        --workers 3 \
        --capture-output \
        app:app
} 2>/dev/null
