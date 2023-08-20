#!/bin/bash

celery -A core beat -s /tmp/celerybeat-schedule -l INFO
