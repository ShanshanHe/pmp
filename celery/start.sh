#!/bin/bash

echo Starting Celery.

#make sure we are at project root /usr/src/app
cd $PROJECT_ROOT
cd etabotsite

nohup celery -A etabotsite worker -l info &
celery -A etabotsite beat -l INFO
