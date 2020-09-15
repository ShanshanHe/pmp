"""
Author: Chad Lewis
September 2020

This script handles the email logger for email admins.

"""

import base64
import logging
import smtplib
import time


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum


class EmailWorker(object):
    @staticmethod
    def send_email(msg, EMAIL_HOST, EMAIL_PORT, SYS_EMAIL, SYS_EMAIL_PWD):
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


class SendEmailAlert(logging.StreamHandler):
    def __init__(self, SYS_DOMAIN, SYS_EMAIL, SYS_EMAIL_PWD, EMAIL_HOST, EMAIL_PORT, ADMINS):
        self.SYS_DOMAIN = SYS_DOMAIN
        self.SYS_EMAIL = SYS_EMAIL
        self.SYS_EMAIL_PWD = SYS_EMAIL_PWD
        self.EMAIL_HOST = EMAIL_HOST
        self.EMAIL_PORT = EMAIL_PORT
        self.ADMINS = ADMINS
    def emit(self, record):
        logging.info("SENDING EMAIL!!!!!!!!!!!!!!!!!!!!!!")
        self.email_from = '"ETAbot" <no-reply@etabot.ai>'
        self.email_to = self.ADMINS
        self.email_subjet = "Email Alert for Django Error"
        msg = EmailWorker.format_email_msg(email_from,self.email_to, self.email_subjet, "TEST!")
        EmailWorker.send_email(self.EMAIL_HOST, self.EMAIL_PORT, self.SYS_EMAIL, self.SYS_EMAIL_PWD)
