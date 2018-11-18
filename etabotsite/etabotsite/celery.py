from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
import logging
from django.conf import settings

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'etabotsite.settings')
# print('celery os.environ: {}'.format(os.environ))
app = Celery('etabotapp')
# Celery will apply all configuration keys with defined namespace
app.config_from_object('django.conf:settings')
# Load tasks from all registered apps
app.autodiscover_tasks(related_name='django_tasks')

# print('settings: {}'.format(settings))
# print('LOCAL_MODE: {}'.format(settings.LOCAL_MODE))
# print('custom_settings: {}'.format(settings.CUSTOM_SETTINGS))

crontab_args = settings.CUSTOM_SETTINGS.get(
    'eta_crontab_args',
    {'hour': 8})   # Midnight Pacific time is 8am UTC

app.conf.beat_schedule = settings.CUSTOM_SETTINGS.get(
    'eta_beat_schedule',
    {'estimate-at-midnight': {
        'task': 'etabotapp.django_tasks.estimate_all',
        'schedule': crontab(**crontab_args)
    }})


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


# test_task = {
#         'task': 'tasks.estimate_all',
#         'schedule': 10.0
#     }
