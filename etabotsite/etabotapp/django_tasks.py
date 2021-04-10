"""Django tasks for celery."""

from celery import shared_task
import celery as clry
from .models import Project, TMS, CeleryTask
from .models import parse_projects_for_TMS
from django.contrib.auth.models import User
import logging
import etabotapp.eta_tasks as eta_tasks
import datetime
from kombu.utils.uuid import uuid

celery = clry.Celery()
celery.config_from_object('django.conf:settings')

#
# def celery_task_update(func):
#     """Decorator for:
#     Updating a job in the database (as CeleryTask) """
#
#     def inner(*args, **kwargs):
#
#         # After completion of the celery task, update its end time and status via this decorator
#         celery_task_record = func(*args, **kwargs)
#         # ^^ capturing result not record so should be returining result instead
#         # can fish out the kwargs for task_id and then update the record end time
#         celery_task_record.end_time = datetime.datetime.now()
#         celery_task_record.status = 'DN'
#         # try to see if we can pass a custom task_id rather than a uuid
#         return celery_task_record
#
#     return inner


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


@shared_task
def estimate_all(**kwargs): # Put kwargs into a decorator
    """Estimate ETA for all tasks for all users."""

    tms_set = TMS.objects.all()
    logging.info( 'starting generating ETAs for the following TMS entries ({}): {}'.format(len(tms_set), tms_set))
    global_params = {
        'push_updates_to_tms': True
    }
    results = []
    for tms in tms_set:
        projects = Project.objects.all().filter(project_tms_id=tms.id)
        projects_ids = [p.id for p in projects]

        celery_task_record = celery_task_record_creator(
            name='etabotapp.django_tasks.estimate_ETA_for_TMS_project_set_ids',
            owner=tms.owner
        )

        result = celery.send_task(
            celery_task_record.task_name,
            args=(tms.id, projects_ids, global_params),
            owner=celery_task_record.owner,
            task_id=celery_task_record.task_id
        )

        # OLD CODE
        # result = celery.send_task('etabotapp.django_tasks.estimate_ETA_for_TMS_project_set_ids',
        # (tms.id, projects_ids, global_params))

        # OLD CODE
        # result, celery_task = celery.send_task_helper('etabotapp.django_tasks.estimate_ETA_for_TMS_project_set_ids',
        #                                               args=(tms.id, projects_ids, global_params), owner=tms.owner)

        logging.info('submitted celery job {} for tms {}, projects {}'.format(result.task_id, tms, projects))
        results.append(result)

        # Update the celery_task_record_object with the end time
        celery_task_record.end_time = datetime.datetime.now()

    return True


def get_tms_by_id(tms_id) -> TMS:
    logging.info('searching for TMS with id: {}'.format(tms_id))
    tms_list = TMS.objects.all().filter(
            pk=tms_id)
    logging.info('found TMSs: {}'.format(tms_list))
    if len(tms_list) > 1:
        raise NameError('TMS id "{}" is not unique'.format(tms_id))
    elif tms_list is None or len(tms_list) == 0:
        logging.warning('no TMS found with id {}'.format(tms_id))
        return None
    else:
        tms = tms_list[0]
    return tms


@shared_task
def estimate_ETA_for_TMS_project_set_ids(
        tms_id,
        projects_set_ids,
        params):
    """Generate ETAs for a given TMS and set of projects."""
    # Instead of using celery send want to use celery send helper
    # Start timer
    tms = get_tms_by_id(tms_id)
    if tms is None:
        raise NameError('cannot find TMS with id {}'.format(tms_id))

    celery_task_record = celery_task_record_creator(
        name='etabotapp.django_tasks.estimate_ETA_for_TMS_project_set_ids',
        owner=tms.owner
    )

    projects_set = Project.objects.all().filter(pk__in=projects_set_ids)
    logging.info('found projects_set: {}'.format(projects_set))
    if 'simulate_failure' in params:
        raise NameError('Simulating failure')

    eta_tasks.estimate_ETA_for_TMS(tms, projects_set, **params)

    # End timer
    celery_task_record.end_time = datetime.datetime.now()


@shared_task
def parse_projects_for_tms_id(
        tms_id,
        params):
    """Parse projects for the given TMS id."""
    tms = get_tms_by_id(tms_id)
    if tms is None:
        raise NameError('cannot find TMS with id {}'.format(tms_id))

    celery_task_record = celery_task_record_creator(
        name='etabotapp.django_tasks.parse_projects_for_tms_id',
        owner=tms.owner
    )

    result = parse_projects_for_TMS(tms, **params)
    tms.connectivity_status['description'] = '{} Import projects result: {}. \n {}'.format(
        datetime.datetime.utcnow().isoformat(),
        result,
        tms.connectivity_status.get('description', ''))
    tms.save()

    # End timer
    celery_task_record.end_time = datetime.datetime.now()


@shared_task
def send_daily_project_report(**kwargs):
    """Generate Daily Email Reports for all Users"""
    logging.info("Sending Emails to all users for Daily Reports!")
    userlist = User.objects.all()
    for user in userlist:
        tms_list = TMS.objects.all().filter(owner=user)
        logging.debug("TMS: {}".format(len(tms_list)))
        for tms in tms_list:
            project_set = Project.objects.all().filter(project_tms_id=tms.id)
            if project_set:

                celery_task_record = celery_task_record_creator(
                    name='etabotapp.django_tasks.send_daily_project_report',
                    owner=tms.owner
                )

                eta_tasks.generate_email_report(tms, project_set, user, **kwargs)

                celery_task_record.end_time = datetime.datetime.now()
