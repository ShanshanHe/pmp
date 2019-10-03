import sys
import os
import logging

logging.getLogger().setLevel(logging.DEBUG)

sys.path.append(os.path.abspath('etabotapp'))
import TMSlib.TMS as TMSlib
import TMSlib.data_conversion as dc

sys.path.pop(0)

from django.db import models
from jsonfield import JSONField


from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from user_activation import ActivationProcessor

from encrypted_model_fields.fields import EncryptedCharField
from django.utils.translation import gettext as _


# class ValidatorTMScredentials(object):
#     def __init__(self):
#         pass

#     def set_context(self, *args, **kwargs):
#         # Determine if this is an update or a create operation.
#         # In `__call__` we can then use that information to modify the validation behavior.
#         logging.debug('set_context args: {}'.format(args))
#         logging.debug('set_context kwargs: {}'.format(kwargs))
#         self.is_update = serializer_field.parent.instance is not None
#         self.serializer_field = serializer_field
#         logging.debug("serializer_field: {}".format(serializer_field))
#         logging.debug("serializer_field.parent: {}".format(serializer_field.parent))

#     def __call__(self, password):


class TMS(models.Model):
    """This class represents the TMS account model.

    TODO: avoid duplicate endpoint/password combinations."""
    owner = models.ForeignKey(
        'auth.User',
        related_name='TMSAccounts',
        on_delete=models.CASCADE)
    endpoint = models.CharField(max_length=60)
    username = models.CharField(max_length=60)
    password = EncryptedCharField(max_length=60)
    type = models.CharField(max_length=20, choices=TMSlib.TMS_TYPES)
    connectivity_status = JSONField(null=True)

    def __str__(self):
        return "{}@{}".format(self.username, self.endpoint)


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
    velocities = JSONField(null=True)
    project_settings = JSONField(null=True)
    # jobs = JSONField(null=True)

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


@receiver(post_save, sender=TMS)
def parse_tms(sender, instance, created, **kwargs):
    if created:
        logging.debug('new TMS instance created - parsing projects')
        parse_projects_for_TMS(instance, **kwargs)
    else:
        logging.debug('saving existing TMS - no need to parse projects')


def parse_projects_for_TMS(instance, **kwargs):
    """Parse projects for the given TMS.

    Creates new Django model projects objects with parsed data.

    Arguments:
        instance - Django TMS object instance
    """
    logging.debug('parse_tms started with kwargs: {}'.format(kwargs))
    existing_projects = Project.objects.filter(project_tms=instance.id)
    TMS_w1 = TMSlib.TMSWrapper(
        instance,
        projects=existing_projects)
    TMS_w1.init_ETApredict([])

    projects_dict = TMS_w1.ETApredict_obj.eta_engine.projects
    velocities = TMS_w1.ETApredict_obj.user_velocity_per_project
    logging.debug('parse_tms: velocities found: {}'.format(velocities))

    existing_projects_dict = {}
    for p in existing_projects:
        existing_projects_dict[p.name] = p

    new_projects = []
    updted_projects = []
    if projects_dict is not None:
        for project_name, attrs in projects_dict.items():
            velocity_json = dc.get_velocity_json(
                velocities, project_name)

            if project_name not in existing_projects_dict:
                new_django_project = Project(
                    owner=instance.owner,
                    project_tms=instance,
                    name=project_name,
                    mode=attrs.get('mode', 'unknown mode'),
                    open_status=attrs.get('open_status', ''),
                    velocities=velocity_json,
                    grace_period=attrs.get('grace_period', 12.0),
                    work_hours=attrs.get('work_hours', {}),
                    vacation_days=attrs.get('vacation_days', {}),
                    project_settings=attrs.get('project_settings', {}))
                new_django_project.save()
                new_projects.append(project_name)
            else:
                p.velocities = velocity_json
                p.project_settings = attrs.get(
                    'project_settings', p.project_settings)
                p.mode = attrs.get('mode', p.mode)
                p.save()
                updted_projects.append(project_name)
    logging.debug('parse_tms has finished')
    return "New projects found and parsed: {}. \
 Updated existing projects: {}".format(
        ', '.join(new_projects),
        ', '.join(updted_projects))
