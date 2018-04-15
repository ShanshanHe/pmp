from rest_framework.permissions import BasePermission
from .models import Project
from .models import TMS
from django.contrib.auth.models import User

class IsOwner(BasePermission):
    """Custom permission class to allow only bucketlist owners to edit them."""

    def has_object_permission(self, request, view, obj):
        """Return True if permission is granted to the bucketlist owner."""
        if isinstance(obj, Project):
            return obj.owner == request.user
        if isinstance(obj, TMS):
            return obj.owner == request.user
        if isinstance(obj, User):
            return obj.id == request.user.id
        return False