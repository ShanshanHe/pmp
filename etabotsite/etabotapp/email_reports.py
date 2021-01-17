"""
Author: Chad Lewis
April 2020

This script contains all the class information needed to send daily
email reports to users.

"""
import base64
import logging
import smtplib
import time
from typing import List

from django.conf import settings
# from django.contrib.auth.models import User
from django.template.loader import render_to_string
# from django.utils.encoding import force_bytes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# from enum import Enum
import etabotapp.email_toolbox as email_toolbox
from etabotapp.TMSlib.interface import BasicReport

SYS_DOMAIN = getattr(settings, "SYS_DOMAIN", "127.0.0.1")
SYS_EMAIL = getattr(settings, "SYS_EMAIL", None)
SYS_EMAIL_PWD = getattr(settings, "SYS_EMAIL_PWD", None)
EMAIL_HOST = getattr(settings, "EMAIL_HOST", None)
EMAIL_PORT = getattr(settings, "EMAIL_PORT", None)
TOKEN_EXPIRATION_PERIOD = getattr(
    settings, "EMAIL_TOKEN_EXPIRATION_PERIOD_MS", 24 * 60 * 60 * 1000)
EMAIL_SUBJECT = '[ETAbot] Please verify your email'
TOKEN_LINK = '{}/verification/activate/{}'


class EmailReportProcess(object):
    @staticmethod
    def send_email(msg):
        email_toolbox.EmailWorker.send_email(msg)

    @staticmethod
    def generate_html_report(user, formatted_reports: List[BasicReport]):
        msg_body = render_to_string('project_report_email.html', {
            'username': user.username,
            'reports': formatted_reports})
        return msg_body

    @staticmethod
    def format_email_msg(user, html_report: str):
        # Format the Msg for email.
        msg = MIMEMultipart()
        msg['From'] = '"ETAbot" <no-reply@etabot.ai>'
        msg['To'] = user.email
        msg['Subject'] = '[ETAbot] Your ETAs Report'
        msg_body = html_report
        msg.attach(MIMEText(msg_body, 'html'))
        logging.info("User Email: {}".format(user.email))
        return msg
