from .models import Project, TMS, CeleryTask
from kombu.utils.uuid import uuid
import datetime
import functools
from .views import *
import logging
import celery as clry
celery = clry.Celery()
celery.config_from_object('django.conf:settings')


def celery_task_record_creator(name, owner):
    unique_task_id = uuid()
    celery_task_record = CeleryTask.objects.create(
        task_id=unique_task_id,
        task_name=name,
        start_time=datetime.datetime.now(),
        end_time=None,
        status='PN',
        owner=owner,
        meta_data=None
    )

    return celery_task_record


def send_celery_task_with_tracking(name, args, owner=None, **kwargs):
    """Create a record for tracking celery task and submit the celery task.

    :args: tuple of positional arguments to ass to celery.send_task"""
    celery_task_record = celery_task_record_creator(name=name, owner=owner)
    kwargs['task_id'] = celery_task_record.task_id
    result = celery.send_task(name, args=args, kwargs=kwargs, task_id=celery_task_record.task_id)
    return result


def celery_task_update(func):
    """Decorator for:
    Updating a job in the database (as CeleryTask) """
    @functools.wraps(func)
    def inner(*args, **kwargs):

        try:
            logging.debug('celery_task_update decorator is starting celery function. ')
            result = func(*args, **kwargs)
            result_status = 'DN'
            logging.info('Celery task function executed.')
        except Exception as e:
            logging.error('Celery task failed due to "{}"'.format(e))
            result_status = 'FL'

        # End timer
        task_id = kwargs.get("task_id")
        if task_id is not None:
            celery_task_records = CeleryTask.objects.all().filter(pk=task_id)
            if len(celery_task_records) == 1:
                celery_task_record = celery_task_records[0]
                celery_task_record.end_time = datetime.datetime.now()
                celery_task_record.status = result_status
                celery_task_record.save()
                logging.info('updated celery task_id={} with status={}'.format(task_id, result_status))
            else:
                logging.error('not unique celery_task_record found, length={}'.format(len(celery_task_records)))
        else:
            logging.warning('no celery task id passed for tracking.')
        return result

    return inner

