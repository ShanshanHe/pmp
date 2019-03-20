from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.models import User
from .models import Project, TMS
from django.conf import settings
import logging
import TMSlib.TMS as TMSlib
from copy import copy

LOCAL_MODE = getattr(settings, "LOCAL_MODE", False)


class UserSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""
    email_validators = []
    if not LOCAL_MODE:
        email_validators.append(UniqueValidator(queryset=User.objects.all()))

    email = serializers.EmailField(
        required=True,
        validators=email_validators
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(min_length=8, write_only=True)
    projects = serializers.PrimaryKeyRelatedField(
        many=True, required=False, queryset=Project.objects.all()
    )
    TMSAccounts = serializers.PrimaryKeyRelatedField(
        many=True, required=False, queryset=TMS.objects.all()
    )
    is_active = serializers.BooleanField(
        required=False
    )

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'],
                                        validated_data['email'],
                                        validated_data['password'])
        user.is_active = False
        return user

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = User
        fields = (
            'id', 'username', 'password',
            'email', 'is_active', 'projects', 'TMSAccounts')
        write_only_fields = ('password',)
        read_only_fields = ('id',)


class TMSSerializer(serializers.ModelSerializer):
    """Serializer to map the model instance into json format."""
    owner = serializers.ReadOnlyField(source='owner.username')

    logging.debug('TMSSerializer owner: {}'.format(owner))

    class Meta:
        """Map this serializer to a model and their fields."""
        model = TMS
        fields = ('id', 'owner', 'endpoint', 'username', 'password', 'type')

    def validate(self, val_input):
        """Validate credentials and endpont result in successful login."""
        logging.debug('validate_tms_credential started')
        logging.debug('self.initial_data: {}'.format(self.initial_data))
        logging.debug('val_input: {}'.format(val_input))
        logging.debug('context: {}'.format(self.context))
        owner = self.context['request'].user
        logging.debug('owner: {}'.format(owner))
        logging.debug('request method: {}'.format(
            self.context['request'].method))
        if self.context['request'].method == 'POST':
            endpoint = self.initial_data['endpoint']
            username = self.initial_data['username']
            if TMS.objects.filter(
                        endpoint=endpoint,
                        owner=owner,
                        username=username).exists():
                raise serializers.ValidationError(
                        'Combination {}@{} already exists for this user'.format(
                            username, endpoint))
            logging.debug(
                'validated username/endpoint combination uniqueness current user')

        if self.context['request'].method == 'PATCH':
            tms = self.instance
            logging.debug(tms.password)
            for k, v in self.initial_data.items():
                setattr(tms, k, v)
            logging.debug(tms.password)
            # logging.debug(tms.password)
            instance = tms
        else:
            instance = TMS(**self.initial_data)
        TMS_w1 = TMSlib.TMSWrapper(instance)
        error = TMS_w1.connect_to_TMS(instance.password)
        if error is not None:
            if 'Unauthorized (401)' in error:
                raise serializers.ValidationError('Unable to log in due to "Unauthorized (401)"\
 error - please check username/email and password')
            elif 'cannot connnect to TMS JIRA' in error:
                raise serializers.ValidationError('cannot connnect to TMS JIRA - please check\
 inputs and try again. If the issue persists, please report the issue to \
hello@etabot.ai')
            else:
                raise serializers.ValidationError('Unrecognized error has occurred - please check\
inputs and try again. If the issue persists, please report the issue to \
hello@etabot.ai')

        logging.debug('validate_tms_credential finished')
        return val_input


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer to map the model instance into json format."""
    owner = serializers.ReadOnlyField(source='owner.username')
    work_hours = serializers.JSONField()
    vacation_days = serializers.JSONField()
    velocities = serializers.JSONField()
    project_settings = serializers.JSONField()

    class Meta:
        """Map this serializer to a model and their fields."""
        model = Project
        fields = (
            'id',
            'project_tms_id',
            'name',
            'owner',
            'mode',
            'open_status',
            'grace_period',
            'work_hours',
            'vacation_days',
            'velocities',
            'project_settings')
        # read_only_fields = ('mode', 'name')
