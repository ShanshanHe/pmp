from .models import Project, TMS, CeleryTask
from kombu.utils.uuid import uuid
import datetime
from .views import celery


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

    celery.send_task(name, args=args, kwargs=kwargs, task_id=celery_task_record.task_id)


def celery_task_update(func):
    """Decorator for:
    Updating a job in the database (as CeleryTask) """

    def inner(*args, **kwargs):

        # After completion of the celery task, update its end time and status via this decorator
        result = func(*args, **kwargs)
        # ^^ capturing result not record so should be returining result instead
        # can fish out the kwargs for task_id and then update the record end time
        celery_task_record.end_time = datetime.datetime.now()
        celery_task_record.status = 'DN'
        # try to see if we can pass a custom task_id rather than a uuid
    # End timer
        if task_id is not None:
            celery_task_record = CeleryTask.objects.all().filter(pk=task_id)
            celery_task_record.end_time = datetime.datetime.now()
        else:
            logging.warning('no celery task id passed for tracking of estimate_ETA_for_TMS_project_set_ids.')
        return result

    return inner

