"""
Author: Chad Lewis
September 2020

This script handles the email logger for email admins.

We are required to repeat the email_toolbox to ensure that it can be used
without a looping import.
"""

import base64
import logging
import smtplib
import time


from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum

logger = logging.getLogger(__name__)



class EmailAlertWorker(object):
    @staticmethod
    def send_email(msg, EMAIL_HOST, EMAIL_PORT, SYS_EMAIL, SYS_EMAIL_PWD):
        try:
            logger.debug('starting send_email.')
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            server.set_debuglevel(1)
            server.ehlo()
            server.starttls()
            #logger.debug('login("{}","***")'.format(SYS_EMAIL))
            server.login(SYS_EMAIL, SYS_EMAIL_PWD)

            server.send_message(msg)
            del server

            logger.info('Successfully sent email')
        except Exception as ex:
            logger.error('Failed to send email')

    @staticmethod
    def format_email_msg(
            from_field,
            to_field,
            subject_field,
            msg_body):
        #Format the Msg for email.
        msg = MIMEMultipart()
        msg['From'] = from_field
        msg['To'] = to_field
        msg['Subject'] = subject_field
        msg_body = msg_body
        msg.attach(MIMEText(msg_body, 'html'))
        return msg


#

#
class SendEmailAlert(logging.StreamHandler):
    """ Send Email Alerts on Errors and above

        SendEmailAlert is a subclass of logging.StreamHandler
        It is used in the custom logger outlined in settings.py
        It will use the EmailAlertWorker to send emails to listed admins.

        All variables are defined in custom_settings.json.
    """
    def __init__(self, SYS_DOMAIN,
                SYS_EMAIL,
                SYS_EMAIL_PWD,
                EMAIL_HOST,
                EMAIL_PORT,
                ADMINS):
        logging.StreamHandler.__init__(self)
        self.SYS_DOMAIN = SYS_DOMAIN
        self.SYS_EMAIL = SYS_EMAIL
        self.SYS_EMAIL_PWD = SYS_EMAIL_PWD
        self.EMAIL_HOST = EMAIL_HOST
        self.EMAIL_PORT = EMAIL_PORT
        self.ADMINS = ADMINS

    def emit(self, record):
        '''This method is called automatically when handling a log'''

        self.email_from = '"ETAbot" <no-reply@etabot.ai>'
        self.email_subjet = "Email Alert for Django Error"
        #Send an Email to all admins
        for emailTo in self.ADMINS:
            print(emailTo)
            msg = EmailAlertWorker.format_email_msg(self.email_from,emailTo, self.email_subjet, self.format(record))
            EmailAlertWorker.send_email(msg,self.EMAIL_HOST, self.EMAIL_PORT, self.SYS_EMAIL, self.SYS_EMAIL_PWD)
