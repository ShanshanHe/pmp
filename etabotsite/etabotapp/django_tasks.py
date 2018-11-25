from datetime import datetime
from celery import shared_task

from celery import Celery

from .models import Project, TMS
import TMSlib.TMS as TMSlib

import logging

# BROKER_URL = getattr(settings, "BROKER_URL", None)

# celery = Celery('tasks', broker=BROKER_URL)

@shared_task
def estimate_all():
    # Estimate ETA for all tasks
    tms_set = TMS.objects.all()
    logging.info(
        'starting generating ETAs for the \
following TMS entries ({}): {}'.format(
            len(tms_set), tms_set))
    for tms in tms_set:
        logging.info('generating ETAs for TMS {}'.format(tms))
        try:
            project_set = Project.objects.all().filter(project_tms_id=tms.id)
            if project_set:
                logging.info('generating ETAs for TMS {} Projects: {}'.format(
                    tms, project_set))
                try:
                    tms_wrapper = TMSlib.TMSWrapper(tms)
                    tms_wrapper.init_ETApredict(project_set)
                    tms_wrapper.estimate_tasks()
                except Exception as e:
                    logging.error('Could not generate ETAs for TMS {} \
    Projects {} due to "{}"'.format(tms, project_set, e))
            else:
                logging.info('no projects found for TMS {}'.format(tms))
        except Exception as e2:
            logging.info('Could not generate ETAs for TMS {} due to'.format(
                tms, e2))
    return True
