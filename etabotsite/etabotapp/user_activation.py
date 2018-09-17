import base64
import logging
import time

from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from enum import Enum

logging.getLogger().setLevel(logging.INFO)

email_subject = 'Welcome to ETAbot'
sys_domain = '127.0.0.1:8000'
sys_email = 'wuhao101@gmail.com'
token_expiration_period = 1 * 60 * 1000


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
            encoded_token = base64.urlsafe_b64encode(force_bytes(plain_token))
            token_str = encoded_token.decode('utf-8')

            message = render_to_string('acc_active_email.html', {
                'username': user.username,
                'domain': sys_domain,
                'token': token_str
            })

            user.email_user(subject=email_subject, message=message, from_email=sys_email)
            logging.info('Successfully send activation email to User %s ' % user.username)
        except Exception as ex:
            logging.error('Failed to send  activation email to User %s: %s' % (user.username, str(ex)))
            raise ex

    @staticmethod
    def activate_user(token):
        try:
            now_millis = int(round(time.time() * 1000))
            token_bytes = force_bytes(token)
            plain_token = base64.urlsafe_b64decode(token_bytes).decode('utf-8')
            uid_and_time = plain_token.split('/')
            uid = int(uid_and_time[0])
            email_time = int(uid_and_time[1])
            time_delta = now_millis - email_time
        except (IndexError, UnicodeDecodeError, ValueError) as ex:
            logging.error('Failed to decrypt the token: %s' % str(ex))
            return ResponseCode.DECRYPTION_ERROR

        user = User.objects.get(pk=uid)

        if user is not None and user.is_active is False:
            if time_delta > token_expiration_period:
                logging.error('Token already expired')
                return ResponseCode.EXPIRATION_ERROR
            else:
                user.is_active = True
                user.save()
                logging.info('Successfully activate User %s' % user.username)
                return ResponseCode.SUCCESS
        elif user is not None and user.is_active is True:
            logging.error('User %s is already activated' % user.username)
            return ResponseCode.ALREADY_ACTIVATE_ERROR
        else:
            logging.error('User does not exist')
            return ResponseCode.NOT_EXIST_ERROR

