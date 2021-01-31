"""Purpose: tests eta_tasks


Authors: Chad Lewis, Alex Radnaev

date created: 2020-03-10
"""

from django.test import TestCase
from django.contrib.auth.models import User
from etabotapp.models import Project, TMS
from etabotapp import eta_tasks as et
from etabotapp import django_tasks as dt
from django.conf import settings
import logging


test_tms_data = getattr(settings, "TEST_TMS_DATA", {})


class TestEmailNotificationsTestCases(TestCase):
    def setUp(self):
        # We want to go ahead and originally create a user.
        self.user = User.objects.create_user('testuser',
                                             'testuser@example.com',
                                             'testpassword')

        #Test user must have valid email to test!
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

    def test_send_daily_project_report(self):
        # eta_tasks.generate_email_report(self.tms,[self.project.id],self.user)
        dt.send_daily_project_report(
            include_active_sprints=True,
            include_future_sprints=True,
            include_backlog=True,
            pickle_df=False)
        # If we make it here with no exits, assert a pass.
        self.assertEqual(1, 1)

    def test_estimate_ETA_for_TMS(self):
        assert isinstance(self.project, Project)
        assert isinstance(self.project.project_settings, dict)
        et.estimate_ETA_for_TMS(self.tms, [self.project])
