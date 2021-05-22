"""
Author: Chad Lewis
April 2020

This script contains all the class information needed to send daily
email reports to users.

"""
import logging
import socket
import pandas as pd
from typing import List, Dict

from django.conf import settings
from django.template.loader import render_to_string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import etabotapp.email_toolbox as email_toolbox
from etabotapp.TMSlib.interface import HierarchicalReportNode, BasicReport

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
    def generate_html_report(user, reports: Dict[str, HierarchicalReportNode]):
        formatted_reports = []
        for project, project_report in reports.items():
            project_formatted_reports = []
            for basic_report in project_report.all_reports():
                project_formatted_reports.append(basic_report)
            if len(project_formatted_reports) == 0:
                project_formatted_reports.append(BasicReport.empty_report(project))
                email_toolbox.EmailWorker.send_email(email_toolbox.EmailWorker.format_email_msg(
                    'no-reply@etabot.ai', 'hello@etabot.ai', 'no reports generated',
                    'user: "{}" \n project: "{}"'.format(user.username, project)
                ))

            formatted_reports = formatted_reports + project_formatted_reports
        if len(formatted_reports) == 0:
            formatted_reports.append(BasicReport.empty_report('Something went wrong. Our apologies.'))
            email_toolbox.EmailWorker.send_email(email_toolbox.EmailWorker.format_email_msg(
                'no-reply@etabot.ai', 'hello@etabot.ai', 'no reports generated',
                'user: "{}" \n projects: "{}"'.format(user.username, reports.keys())
            ))
        msg_body = render_to_string('report_email.html', {
            'username': user.username,
            'reports': formatted_reports,
            'host': socket.gethostname()})
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
