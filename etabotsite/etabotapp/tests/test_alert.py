"""Purpose: tests the email alert functionality with errors in djago


Author: Chad Lewis

date created: 2020-09-14
"""

from django.test import TestCase
from django.contrib.auth.models import User
from etabotapp.models import Project, TMS
from etabotapp import django_tasks as dt
from django.conf import settings
from unittest.mock import MagicMock
import logging
from etabotapp.email_alert import SendEmailAlert

test_tms_data = getattr(settings, "TEST_TMS_DATA", {})


class TestEmailAlert(TestCase):
    """
    This testing class will test all the functions associated with handling
    errors and above and emailing alerts to admins. Each test goal is below:
        test_logger_on_exception: Tests that our logger exception method is called
            when an exception is raised.
        test_send_email_alert_emit: Tests that when our exception is raised the
            handler actually emits the signal to email.

    """
    def __init__(self, *args, **kwargs):
        super(TestEmailAlert, self).__init__(*args, **kwargs)
        self.SYS_DOMAIN = getattr(settings, "SYS_DOMAIN", "127.0.0.1")
        self.SYS_EMAIL = getattr(settings, "SYS_EMAIL", None)
        self.SYS_EMAIL_PWD = getattr(settings, "SYS_EMAIL_PWD", None)
        self.EMAIL_HOST = getattr(settings, "EMAIL_HOST", None)
        self.EMAIL_PORT = getattr(settings, "EMAIL_PORT", None)

    def test_logger_on_exception(self):
        '''
        Tests that our logger exception method is called when an exception
        is raised.
        Utilizes a mock method to catch the call to logger exception.
        '''
        logger = logging.getLogger(__name__)
        logger.exception = MagicMock(name='exception')

        #Log the test and setup the mock exception
        logger.info("Testing Email Alert with Divide by Zero Error!")
        #We want to cause an error that's garunteed to throw an error and log!

        try:
            fail = 1/0
        except Exception as e:
            logger.exception('Test Alert in test_logger_on_exception')

        #Run some tests on the logger call
        #We will test if the exception has been called.
        #We will test if the exception has called with the correct Parameters
        logger.exception.assert_called_once()
        logger.exception.assert_called_once_with('Test Alert in test_logger_on_exception')

    def test_send_email_alert_emit(self):
            '''
            Tests that when our exception is raised the handler actually emits
            the signal to email.
            Utilizes a mock method and a replacement handler for the root
            logger. We replace root logger mail_admins handler with our own.
            Then mock the SendEmailAlert.emit method.
            '''
            logger = logging.getLogger()
            logger.info("Testing test_send_email_alert_emit")
            ADMIN_EMAILS = []
            handler = SendEmailAlert(self.SYS_DOMAIN,
                                     self.SYS_EMAIL,
                                     self.SYS_EMAIL_PWD,
                                     self.EMAIL_HOST,
                                     self.EMAIL_PORT,
                                     ADMIN_EMAILS)
            handler.emit = MagicMock(name='emit')
            logger.info("Setting Handler!")
            logger.handlers[0] = handler

            logger.exception("Test Alert in test_logger_email!")
            handler.emit.assert_called_once()

    def test_alert_email_sent(self):
        '''
        Tests that once an exception has been logged and the Handler is active
        that the send_email method in EmailAlertWorker is called.
        '''
        logger = logging.getLogger()
        logger.info("Testing test_alert_email_sent")
        ADMIN_EMAILS = ["testuser@fake.com"]

        handler = SendEmailAlert(self.SYS_DOMAIN,
                                 self.SYS_EMAIL,
                                 self.SYS_EMAIL_PWD,
                                 self.EMAIL_HOST,
                                 self.EMAIL_PORT,
                                 ADMIN_EMAILS)
        emailWorker = handler._emailAlertWorker

        emailWorker.send_email = MagicMock(name="send_email")
        logger.handlers[0] = handler
        logger.exception("Test Alert in test_alert_email_sent")
        emailWorker.send_email.assert_called_once()
