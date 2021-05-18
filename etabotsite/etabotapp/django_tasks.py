"""Django tasks for celery."""

from celery import shared_task
import celery as clry
from .models import Project, TMS, CeleryTask
from .models import parse_projects_for_TMS
from django.contrib.auth.models import User
import logging
import etabotapp.eta_tasks as eta_tasks
import datetime
from .celery_tracking import *


celery = clry.Celery()
celery.config_from_object('django.conf:settings')


@celery_task_update
@shared_task
def estimate_all(task_id=None, **kwargs): # Put kwargs into a decorator
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

        result = celery.send_task(
            'etabotapp.django_tasks.estimate_ETA_for_TMS_project_set_ids',
            args=(tms.id, projects_ids, global_params),
            owner=tms.owner,
            task_id=task_id
        )

        # OLD CODE
        # result = celery.send_task('etabotapp.django_tasks.estimate_ETA_for_TMS_project_set_ids',
        # (tms.id, projects_ids, global_params))

        # OLD CODE
        # result, celery_task = celery.send_task_helper('etabotapp.django_tasks.estimate_ETA_for_TMS_project_set_ids',
        #                                               args=(tms.id, projects_ids, global_params), owner=tms.owner)

        logging.info('submitted celery job {} for tms {}, projects {}'.format(result.task_id, tms, projects))
        results.append(result)

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


@celery_task_update
@shared_task
def estimate_ETA_for_TMS_project_set_ids(
        tms_id,
        projects_set_ids,
        params,
        task_id=None):
    """Generate ETAs for a given TMS and set of projects."""
    # Instead of using celery send want to use celery send helper
    # Start timer
    tms = get_tms_by_id(tms_id)
    if tms is None:
        raise NameError('cannot find TMS with id {}'.format(tms_id))

    projects_set = Project.objects.all().filter(pk__in=projects_set_ids)
    logging.info('found projects_set: {}'.format(projects_set))
    if 'simulate_failure' in params:
        raise NameError('Simulating failure')

    eta_tasks.estimate_ETA_for_TMS(tms, projects_set, **params)


@celery_task_update
@shared_task
def parse_projects_for_tms_id(
        tms_id,
        params,
        task_id=None):
    """Parse projects for the given TMS id."""
    tms = get_tms_by_id(tms_id)
    if tms is None:
        raise NameError('cannot find TMS with id {}'.format(tms_id))
    result = parse_projects_for_TMS(tms, **params)
    tms.connectivity_status['description'] = '{} Import projects result: {}. \n {}'.format(
        datetime.datetime.utcnow().isoformat(),
        result,
        tms.connectivity_status.get('description', ''))
    tms.save()


@celery_task_update
@shared_task
def send_daily_project_report(task_id=None,**kwargs):
    """Generate Daily Email Reports for all Users"""
    logging.info("Sending Emails to all users for Daily Reports!")
    userlist = User.objects.all()
    for user in userlist:
        tms_list = TMS.objects.all().filter(owner=user)
        logging.debug("TMS: {}".format(len(tms_list)))
        for tms in tms_list:
            project_set = Project.objects.all().filter(project_tms_id=tms.id)
            if project_set:
                eta_tasks.generate_email_report(tms, project_set, user, **kwargs)
