#!/bin/bash

python3 manage.py migrate

python3 manage.py collectstatic --no-input --clear

gunicorn core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --access-logfile /var/log/gunicorn/access.log
