import sys
import os
import logging

logging.getLogger().setLevel(logging.DEBUG)

sys.path.append(os.path.abspath('etabotapp'))
from .TMSlib.TMS import TMSWrapper, TMSTypes

sys.path.pop(0)

from django.db import models
from jsonfield import JSONField

from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from encrypted_model_fields.fields import EncryptedCharField
from django.utils.translation import gettext as _


class TMS(models.Model):
    """This class represents the jira user model."""
    TMS_TYPE = (
        ('JI', 'JIRA'),
        ('TR', 'Trello'),
    )
    owner = models.ForeignKey('auth.User', related_name='TMSAccounts',
                              on_delete=models.CASCADE)
    endpoint = models.CharField(max_length=60)
    username = models.CharField(max_length=60)
    password = EncryptedCharField(max_length=60)
    type = models.CharField(max_length=20, choices=TMS_TYPE)

    def __str__(self):
        return self.username


class Project(models.Model):
    """This class represents the project model."""
    # jiraacount = models.ForeignKey(JIRAAccount, on_delete=models.CASCADE)
    owner = models.ForeignKey('auth.User', related_name='projects',
                              on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    mode = models.CharField(max_length=60)
    open_status = models.CharField(max_length=60)
    grace_period = models.FloatField()
    work_hours = JSONField()
    vacation_days = JSONField()

    def __str__(self):
        return self.name


# This receiver handles token creation immediately a new user is created.
@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


# This receiver handles TMS credential check before saving it.
@receiver(pre_save, sender=TMS)
def validate_tms_credential(sender, instance, **kwargs):
    logging.debug('validate_tms_credential started')
    TMS_w1 = TMSWrapper(TMSTypes.JIRA, instance.endpoint, instance.username,
                        {})
    TMS_w1.connect_to_TMS(instance.password)
    logging.debug('validate_tms_credential finished')
    logging.debug('instance  ({}): {}'.format(type(instance), instance))
    logging.debug('sender: {}'.format(sender))
    logging.debug('kwargs: {}'.format(kwargs))
    dummy_project1 = Project(
        owner=instance.owner,
        name='Dummy project',
        mode='Scrum',
        open_status='To Do',
        grace_period='4.0',
        work_hours={
            "Monday": [

                {"end": 14, "start": 10},
                {"end": 17, "start": 15}

            ],

            "Thursday": [

                {"end": 14, "start": 10}

            ],

            "Time Zone": "GMT +8",

            "Tuesday": [

                {"end": 14, "start": 10}

            ],
            "Wednesday": [

                {"end": 14, "start": 10},
                {"end": 22, "start": 19}

            ]},
        vacation_days=[

            {"start": "2017-04-01", "end": "2017-05-02"},
            {"start": "2018-07-01", "end": "2018-07-02"}

        ])
    dummy_project1.save()
    logging.debug('dummy_project1 saved')

models.signals.pre_save.connect(validate_tms_credential, sender=TMS)
