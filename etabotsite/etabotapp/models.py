import sys
import os
import logging

logging.getLogger().setLevel(logging.DEBUG)

sys.path.append(os.path.abspath('etabotapp'))
import TMSlib.TMS as TMSlib

sys.path.pop(0)

from django.db import models
from jsonfield import JSONField

from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .user_activation import ActivationProcessor

from encrypted_model_fields.fields import EncryptedCharField
from django.utils.translation import gettext as _


class TMS(models.Model):
    """This class represents the TMS account model."""
    owner = models.ForeignKey('auth.User', related_name='TMSAccounts',
                              on_delete=models.CASCADE)
    endpoint = models.CharField(max_length=60)
    username = models.CharField(max_length=60)
    password = EncryptedCharField(max_length=60)
    type = models.CharField(max_length=20, choices=TMSlib.TMS_TYPES)

    def __str__(self):
        return self.username


class Project(models.Model):
    """This class represents the project model."""
    # jiraacount = models.ForeignKey(JIRAAccount, on_delete=models.CASCADE)
    owner = models.ForeignKey('auth.User', related_name='projects',
                              on_delete=models.CASCADE)
    project_tms = models.ForeignKey(TMS, on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    mode = models.CharField(max_length=60)  # scrum or kanban
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
        user = User.objects.get(pk=instance.id)
        user.is_active = False
        user.save()

        ActivationProcessor.email_token(user)


# This receiver handles TMS credential check before saving it.
@receiver(pre_save, sender=TMS)
def validate_tms_credential(sender, instance, **kwargs):
    logging.debug('validate_tms_credential started')
    TMS_w1 = TMSlib.TMSWrapper(instance)
    TMS_w1.connect_to_TMS(instance.password)
    logging.debug('validate_tms_credential finished')

@receiver(post_save, sender=TMS)
def parse_tms(sender, instance, **kwargs):
    logging.debug('parse_tms started')
    TMS_w1 = TMSlib.TMSWrapper(
        instance,
        projects=Project.objects.filter(project_tms=instance.id))
    TMS_w1.init_ETApredict([])
    projects_dict = TMS_w1.ETApredict_obj.eta_engine.projects
    if projects_dict is not None:
        for project_name, attrs in projects_dict.items():
            django_project = Project(
                owner=instance.owner,
                project_tms=instance,
                name=project_name,
                mode=attrs.get('mode', 'unknown mode'),
                open_status=attrs.get('open_status', ''),
                grace_period=attrs.get('grace_period', 12.0),
                work_hours=attrs.get('work_hours', '{}'),
                vacation_days=attrs.get('vacation_days', '{}'))
            django_project.save()

    logging.debug('parse_tms has finished')
