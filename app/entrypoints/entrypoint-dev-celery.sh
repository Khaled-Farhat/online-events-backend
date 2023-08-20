#!/bin/bash

celery -A core worker -B -s /tmp/celerybeat-schedule -l INFO
