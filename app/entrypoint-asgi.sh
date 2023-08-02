#!/bin/bash

python3 manage.py collectstatic --no-input --clear

daphne -b 0.0.0.0 -p 8000 online_events.asgi:application
