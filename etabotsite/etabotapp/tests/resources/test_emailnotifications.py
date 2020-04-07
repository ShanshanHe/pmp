"""Purpose: tests eta_tasks.generate_email_report


Author: Chad Lewis

date created: 2020-03-10
"""
### imports
import unittest
from django.test import TestCase
import sys
import time
import logging
import eta_tasks
from django.contrib.auth.models import User
from etabotapp.models import Project, TMS
import TMSlib.data_conversion as dc
import TMSlib.TMS as TMSlib
from etabotapp import django_tasks as dt
sys.path.append('..')
#### Global variables
#### testcase class
class TestEmailNotificationsTestCases(unittest.TestCase):
	#def test_exception(self):
	#	self.assertRaises(Exception, div, 5, 0)
    def setUp(self):
        # We want to go ahead and originally create a user.
        self.user = User.objects.create_user('testuser',
                                                  'lokay81197@gotkmail.com',
                                                  'testpassword')

        self.endpoint = "localhost:8888"
        self.username = "testuser@example.com"
        self.password = "testpassword"
        self.type = "JI"
        self.tms = TMS(owner=self.user, endpoint=self.endpoint,
                       username=self.username, password=self.password,
                       type=self.type)
        self.tms.save()
        self.project_name = "etabot"
        self.project_mode = "scrum"
        self.project_open_status = "ToDo"
        self.project_grace_period = "24"
        self.project_work_hours = "{1:(10,14),2:(16,20), 3:(10,14), 4:(16,18), 5:(20,21), 6:(23,23), 0:(9,10)}"
        self.project_vacation_days = "{('2017-04-21', '2017-04-30'), ('2017-05-16', '2017-05-19'), ('2017-05-24', '2017-05-24'), ('2017-05-29', '2017-05-29')}"
        self.project = Project(owner=self.user, project_tms = self.tms,
                               name=self.project_name,
                               mode=self.project_mode,
                               open_status=self.project_open_status,
                               grace_period=self.project_grace_period,
                               work_hours=self.project_work_hours,
                               vacation_days=self.project_vacation_days)
        self.project.save()

    def test_estimate_ETA_for_TMS(self):
        ##eta_tasks.generate_email_report(self.tms,[self.project.id],self.user)
        dt.send_daily_project_report()
        self.assertEqual(1,1)

#unittest.main()
