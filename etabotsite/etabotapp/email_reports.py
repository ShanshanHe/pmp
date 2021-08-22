"""
Author: Chad Lewis
April 2020

This script contains all the class information needed to send daily
email reports to users.

"""
import logging
import socket
from datetime import datetime

import pandas as pd
from typing import List, Dict, Tuple, Union

from django.conf import settings
from django.template.loader import render_to_string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import etabotapp.email_toolbox as email_toolbox
from etabotapp.TMSlib.interface import HierarchicalReportNode, BasicReport

logger = logging.getLogger()

SYS_DOMAIN = getattr(settings, "SYS_DOMAIN", "127.0.0.1")
SYS_EMAIL = getattr(settings, "SYS_EMAIL", None)
SYS_EMAIL_PWD = getattr(settings, "SYS_EMAIL_PWD", None)
EMAIL_HOST = getattr(settings, "EMAIL_HOST", None)
EMAIL_PORT = getattr(settings, "EMAIL_PORT", None)
TOKEN_EXPIRATION_PERIOD = getattr(
    settings, "EMAIL_TOKEN_EXPIRATION_PERIOD_MS", 24 * 60 * 60 * 1000)
EMAIL_SUBJECT = '[ETAbot] Please verify your email'
TOKEN_LINK = '{}/verification/activate/{}'


def logs2html(logs: Union[None, List[Tuple[datetime, str]]]):
    if logs is None:
        return '<b>no logs available.</b>'
    logs_html = '<table class="df_table">\n<tr><td>UTC</td><td>step time, s</td><td>log</td></tr>'
    t1 = None
    for log in logs:
        t2 = log[0]
        if t1 is not None:
            dt = (t2 - t1).seconds
        else:
            dt = ''
        logs_html += '\n<tr><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
            t2, dt, log[1])
        t1 = t2
    logs_html += '\n</table>'
    return logs_html


class EmailReportProcess(object):
    @staticmethod
    def send_email(msg):
        email_toolbox.EmailWorker.send_email(msg)

    @staticmethod
    def generate_html_report(user, reports: Dict[str, HierarchicalReportNode], logs=None) -> (str, str):
        """Return (report_email, full_report) tuple."""
        formatted_reports = []
        html_logs = logs2html(logs)
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
            report = BasicReport.empty_report('Something went wrong. Our apologies.')
            report.short_html = '<h1>Something went wrong. Our apologies.</h1><br><h2>Logs:</h2><br>' + html_logs
            formatted_reports.append(report)
            email_toolbox.EmailWorker.send_email(email_toolbox.EmailWorker.format_email_msg(
                'no-reply@etabot.ai', 'hello@etabot.ai', 'no reports generated',
                'user: "{}" \n projects: "{}"\n logs: {}'.format(user.username, reports.keys(), html_logs)
            ))
        report_email = render_to_string('report_email.html', {
            'username': user.username,
            'reports': formatted_reports,
            'host': socket.gethostname()})

        full_report = render_to_string('full_report.html', {
            'username': user.username,
            'reports': formatted_reports,
            'host': socket.gethostname(),
            'logs': html_logs})

        return report_email, full_report

    @staticmethod
    def format_email_msg(user, html_report: str, images=None):
        # Format the Msg for email.
        msg = MIMEMultipart('related')
        msg['From'] = '"ETAbot" <no-reply@etabot.ai>'
        msg['To'] = user.email
        msg['Subject'] = '[ETAbot] Your ETAs Report'
        msg_body = html_report
        msg.attach(MIMEText(msg_body, 'html'))
        if images is not None:
            for image in images:
                msg.attach(image)
        else:
            logger.debug('no images to attach.')
        logger.info("User Email: {}".format(user.email))
        return msg
