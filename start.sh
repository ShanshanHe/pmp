#!/bin/bash

echo Starting Gunicorn.

#make sure we are at project root /usr/src/app
cd $PROJECT_ROOT

if [ ! -f $PROJECT_ROOT/.build ]; then
  echo "Collecting and compiling statics"
  pushd etabotsite
  python manage.py collectstatic --noinput
  python manage.py migrate --run-syncdb
  popd
  date > $PROJECT_ROOT/.build
fi

cd etabotsite
exec gunicorn etabotsite.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3