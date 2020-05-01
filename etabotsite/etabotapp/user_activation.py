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
import email_toolbox
from requests.utils import quote

logging.getLogger().setLevel(logging.INFO)
# logging.getLogger().setLevel(logging.DEBUG)

SYS_DOMAIN = getattr(settings, "SYS_DOMAIN", "127.0.0.1")
SYS_EMAIL = getattr(settings, "SYS_EMAIL", None)
SYS_EMAIL_PWD = getattr(settings, "SYS_EMAIL_PWD", None)
EMAIL_HOST = getattr(settings, "EMAIL_HOST", None)
EMAIL_PORT = getattr(settings, "EMAIL_PORT", None)
TOKEN_EXPIRATION_PERIOD = getattr(
    settings, "EMAIL_TOKEN_EXPIRATION_PERIOD_MS", 24 * 60 * 60 * 1000)
EMAIL_SUBJECT = '[ETAbot] Please verify your email'
TOKEN_LINK = '{}/verification/activate/{}'

logging.info('SYS_DOMAIN: "{}"'.format(SYS_DOMAIN))
logging.info('SYS_EMAIL: "{}"'.format(SYS_EMAIL))
# logging.debug('SYS_EMAIL_PWD: "{}"'.format(SYS_EMAIL_PWD))
logging.info('EMAIL_HOST: "{}"'.format(EMAIL_HOST))
logging.info('EMAIL_PORT: "{}"'.format(EMAIL_PORT))
logging.info('TOKEN_EXPIRATION_PERIOD: "{}"'.format(TOKEN_EXPIRATION_PERIOD))


class ResponseCode(Enum):
    DECRYPTION_ERROR = 1
    EXPIRATION_ERROR = 2
    ALREADY_ACTIVATE_ERROR = 3
    NOT_EXIST_ERROR = 4
    SUCCESS = 5


class ActivationProcessor(object):
    @staticmethod
    def email_token(user):
        try:
            now_millis = int(round(time.time() * 1000))
            plain_token = str(user.id) + "/" + str(now_millis)
            logging.debug('plain_token: "{}"'.format(plain_token))
            encoded_token = base64.urlsafe_b64encode(force_bytes(plain_token))
            logging.debug('encoded_token: "{}"'.format(encoded_token))
            token_str = quote(encoded_token.decode('utf-8'))
            logging.debug('token_str: "{}"'.format(token_str))

            msg = MIMEMultipart()
            msg['From'] = '"ETAbot" <no-reply@etabot.ai>'
            msg['To'] = user.email
            msg['Subject'] = EMAIL_SUBJECT
            hyper_link = TOKEN_LINK.format(SYS_DOMAIN, token_str)
            msg_body = render_to_string('acc_active_email.html', {
                'username': user.username,
                'link': hyper_link,
            })
            msg.attach(MIMEText(msg_body, 'html'))

            email_toolbox.EmailWorker.send_email(msg)

            logging.info('Successfully sent activation email to User %s '
                         % user.username)
        except Exception as ex:
            logging.error('Failed to send activation email to User %s: %s'
                          % (user.username, str(ex)))
            raise ex

    @staticmethod
    def activate_user(token):
        logging.debug('activating user with token "{}"'.format(token))
        try:
            now_millis = int(round(time.time() * 1000))
            token_bytes = force_bytes(token)
            plain_token = base64.urlsafe_b64decode(token_bytes).decode('utf-8')
            uid_and_time = plain_token.split('/')
            uid = int(uid_and_time[0])
            logging.debug('user id: {}'.format(uid))
            logging.debug('uid_and_time[1]: {}'.format(uid_and_time[1]))
            email_time = int(uid_and_time[1])
            time_delta = now_millis - email_time
        except (IndexError, UnicodeDecodeError, ValueError) as ex:
            logging.error('Failed to decrypt the token: %s' % str(ex))
            return ResponseCode.DECRYPTION_ERROR

        logging.debug('decrypted uid: {}'.format(uid))
        user = User.objects.get(pk=uid)

        if user is not None and user.is_active is False:
            if time_delta > TOKEN_EXPIRATION_PERIOD:
                logging.error('Token has expired')
                return ResponseCode.EXPIRATION_ERROR
            else:
                user.is_active = True
                user.save()
                logging.info('Successfully activated User %s' % user.username)
                return ResponseCode.SUCCESS
        elif user is not None and user.is_active is True:
            logging.error('User %s is already activated' % user.username)
            return ResponseCode.ALREADY_ACTIVATE_ERROR
        else:
            logging.error('User does not exist')
            return ResponseCode.NOT_EXIST_ERROR
