'''
Email method

'''
import base64
import logging
import smtplib
import time

from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum

SYS_DOMAIN = getattr(settings, "SYS_DOMAIN", "127.0.0.1")
SYS_EMAIL = getattr(settings, "SYS_EMAIL", None)
SYS_EMAIL_PWD = getattr(settings, "SYS_EMAIL_PWD", None)
EMAIL_HOST = getattr(settings, "EMAIL_HOST", None)
EMAIL_PORT = getattr(settings, "EMAIL_PORT", None)


class EmailWorker(object):
    @staticmethod
    def send_email(msg):
        try:
            logging.debug('starting send_email.')
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            server.set_debuglevel(1)
            server.ehlo()
            server.starttls()
            logging.debug('login("{}","***")'.format(SYS_EMAIL))
            server.login(SYS_EMAIL, SYS_EMAIL_PWD)

            server.send_message(msg)
            del server

            logging.info('Successfully sent email')
        except Exception as ex:
            logging.error('Failed to send email')

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
