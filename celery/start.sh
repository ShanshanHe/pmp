#!/bin/bash

echo Starting Celery.

#make sure we are at project root /usr/src/app
cd $PROJECT_ROOT
cd etabotsite

celery -A etabotsite worker -l info --max-tasks-per-child=1
