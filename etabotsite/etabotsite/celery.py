from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
import logging
import django
from django.conf import settings
from django.apps import apps

logger = logging.getLogger('celery')
logger.info('celery logger info.')
# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'etabotsite.settings')

django.setup()
# print('celery os.environ: {}'.format(os.environ))
app = Celery('etabotapp')
# Celery will apply all configuration keys with defined namespace
app.config_from_object('django.conf:settings')
# app.config_from_object(settings, namespace='CELERY')
# Load tasks from all registered apps
app.autodiscover_tasks(related_name='django_tasks')
# app.autodiscover_tasks(
#     lambda: [n.name for n in apps.get_app_configs()],
#     related_name='django_tasks')

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

# email_reports_crontab_args = settings.CUSTOM_SETTINGS.get(
#     'email_reports_crontab_args',
#     {'hour': 10})   # Midnight Pacific time is 8am UTC

#Schedule our daily reports for 1am. An hour after the predicitions are.
# commented out currently since sending out reports is done part of etabotapp.django_tasks.estimate_all
# app.conf.beat_schedule = {
#     'send_daily_reports': {
#         'task':'etabotapp.django_tasks.send_daily_project_report',
#         'schedule': crontab(**email_reports_crontab_args)
#     }
# }


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


# test_task = {
#         'task': 'tasks.estimate_all',
#         'schedule': 10.0
#     }
logging.info('celery.py finished')
