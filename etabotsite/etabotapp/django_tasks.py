from datetime import datetime
from celery import shared_task

from celery import Celery
# import logging

# BROKER_URL = getattr(settings, "BROKER_URL", None)

# celery = Celery('tasks', broker=BROKER_URL)

@shared_task
def estimate_all():
    # Estimate ETA for all tasks
    tms_set = TMS.objects.all()
    for tms in tms_set:
        project_set = Project.objects.all().filter(project_tms_id=tms.id)
        if project_set:
            tms_wrapper = TMSlib.TMSWrapper(tms)
            tms_wrapper.init_ETApredict(project_set)
            tms_wrapper.estimate_tasks()
    return True
