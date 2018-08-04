from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from .models import Project, TMS


class UserSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
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

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'],
                                        validated_data['email'],
                                        validated_data['password'])
        return user

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = User
        fields = (
        'id', 'username', 'password', 'email', 'projects', 'TMSAccounts')
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
