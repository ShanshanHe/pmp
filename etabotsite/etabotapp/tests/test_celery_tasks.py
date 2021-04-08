"""

Purpose:
- test CeleryTask model from models.py
- test CeleryTask creation and field updates from django_tasks.py (called on estimate_all)

Author: Etash Kalra

Date Created: 03/27/2021

"""

from django.test import TestCase
from django.contrib.auth.models import User
from etabotapp.models import Project, TMS
from etabotapp import eta_tasks as et
from etabotapp import django_tasks as dt
from django.conf import settings
import logging
from .models import CeleryTask


test_tms_data = getattr(settings, "TEST_TMS_DATA", {})

class TestCeleryTasks(TestCase):

    def setUp(self):
        # We want to go ahead and originally create a user.
        self.user = User.objects.create_user('testuser',
                                             'testuser@example.com',
                                             'testpassword')

        # Test user must have valid email to test!
        logging.debug('self.user.email: {}'.format(self.user.email))
        self.assertTrue('testuser@example.com' == self.user.email)

        self.tms = TMS(owner=self.user, **test_tms_data)
        self.tms.save()
        self.project_name = "ETAbot-Demo"
        self.project_mode = "scrum"
        self.project_open_status = "ToDo"
        self.project_grace_period = "24"
        self.project_work_hours = {
            1: (10, 14), 2: (16, 20), 3: (10, 14), 4: (16, 18), 5: (20, 21), 6: (23, 23), 0: (9, 10)}
        self.project_vacation_days = [
            ('2017-04-21', '2017-04-30'),
            ('2017-05-16', '2017-05-19'),
            ('2017-05-24', '2017-05-24'),
            ('2017-05-29', '2017-05-29')]
        self.project = Project(owner=self.user, project_tms=self.tms,
                               name=self.project_name,
                               mode=self.project_mode,
                               open_status=self.project_open_status,
                               grace_period=self.project_grace_period,
                               work_hours=self.project_work_hours,
                               vacation_days=self.project_vacation_days,
                               project_settings={})
        self.project.save()

    def test_celery_task_record_for_estimate_all(self):
        """Ensure that celery tasks records are created and added as objects within the models database
        when estimate_all() method is run."""
        # created_celery_task = dt.estimate_all._original()

        created_celery_task = dt.estimate_all()
        task_id = created_celery_task.task_id
        task_name = created_celery_task.task_name
        start_time = created_celery_task.start_time
        end_time = created_celery_task.end_time
        status = created_celery_task.status
        owner = task_id = created_celery_task.owner
        meta_data = created_celery_task.meta_data

        # Ensure unique task_id
        objects_in_db = CeleryTask.objects.filter(task_id=task_id)
        num_in_db = objects_in_db.count()
        self.assertEqual(num_in_db, 1)

        self.assertEqual(objects_in_db[0].task_name, task_name)
        self.assertEqual(objects_in_db[0].start_time, start_time)
        self.assertEqual(objects_in_db[0].end_time, end_time)
        self.assertEqual(objects_in_db[0].status, status)
        self.assertEqual(objects_in_db[0].owner, owner)
        self.assertEqual(objects_in_db[0].meta_data, meta_data)



