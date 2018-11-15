from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'etabotsite.settings')
app = Celery('etabotapp')
# Celery will apply all configuration keys with defined namespace
app.config_from_object('django.conf:settings')
# Load tasks from all registered apps
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'estimate-at-midnight': {
        'task': 'etabotapp.django_tasks.estimate_all',
        'schedule': crontab(hour=8)  # Midnight Pacific time is 8am UTC
    },
}

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
