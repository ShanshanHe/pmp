from .models import Project, TMS, CeleryTask
from kombu.utils.uuid import uuid
import datetime
from .views import *
import logging


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


def send_celery_task_with_tracking(name, *args, owner=None, **kwargs):
    celery_task_record = celery_task_record_creator(name=name, owner=owner)
    kwargs['task_id'] = celery_task_record.task_id
    result = celery.send_task(name, args=args, kwargs=kwargs, task_id=celery_task_record.task_id)
    return result


def celery_task_update(func):
    """Decorator for:
    Updating a job in the database (as CeleryTask) """

    def inner(*args, **kwargs):

        result = func(*args, **kwargs)

        # End timer
        if 'task_id' in kwargs:
            celery_task_record = CeleryTask.objects.all().filter(pk=kwargs["task_id"])
            celery_task_record.end_time = datetime.datetime.now()
            celery_task_record.status = 'DN'
        else:
            logging.warning('no celery task id passed for tracking of estimate_ETA_for_TMS_project_set_ids.')
        return result

    return inner

