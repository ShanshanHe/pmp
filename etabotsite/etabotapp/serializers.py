from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from .models import Project, TMS
from django.conf import settings

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

    class Meta:
        """Map this serializer to a model and their fields."""
        model = TMS
        fields = ('id', 'owner', 'endpoint', 'username', 'password', 'type')


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer to map the model instance into json format."""
    owner = serializers.ReadOnlyField(source='owner.username')
    work_hours = serializers.JSONField()
    vacation_days = serializers.JSONField()

    class Meta:
        """Map this serializer to a model and their fields."""
        model = Project
        fields = ('id', 'name', 'owner', 'mode', 'open_status', 'grace_period',
                  'work_hours', 'vacation_days')
        # read_only_fields = ('mode', 'name')
