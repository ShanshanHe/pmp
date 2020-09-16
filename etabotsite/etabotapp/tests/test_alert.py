"""Purpose: tests the email alert functionality with errors in djago


Author: Chad Lewis

date created: 2020-09-14
"""

from django.test import TestCase
from django.contrib.auth.models import User
from etabotapp.models import Project, TMS
from etabotapp import django_tasks as dt
from django.conf import settings
import logging


logger = logging.getLogger(__name__)
test_tms_data = getattr(settings, "TEST_TMS_DATA", {})

class TestEmailAlert(TestCase):
    """
    This test will create an exception to test our error reporting by email.
    The settings of the logger can be changed in etabotsite/settings.py
    logs from this test will show as test_alert and not root.
    """
    def test_failure(self):
        #We want to cause an error that's garunteed to throw an error and log!
        logger.info("Testing Email Alert with Divide by Zero Error!")
        try:
            fail = 1/0
        except Exception as e:
            logger.exception('While testing test_alert in etabotapp/tests/ \
                            the following exception was encountered: \
                            {}'.format(e))
