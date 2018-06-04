from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status, mixins
from rest_framework.response import Response
from .serializers import UserSerializer, ProjectSerializer, TMSSerializer
from .models import Project
from .models import TMS
from .permissions import IsOwner
from django.views.decorators.csrf import ensure_csrf_cookie
import logging
logging.getLogger().setLevel(logging.DEBUG)

@ensure_csrf_cookie
def index(request, path='', format=None):
    """
    Renders the Angular2 SPA
    """
    print('format = "{}"'.format(format))
    return render(request, 'index.html')


class UserCreateView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""

    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self, *args, **kwargs):
        return User.objects.all().filter(username=self.request.user.username)


class UserDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """This class handles the http GET, PUT and DELETE requests."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)

    def get_queryset(self, *args, **kwargs):
        return User.objects.all().filter(username=self.request.user.username)


class TMSCreateView(generics.ListCreateAPIView):
    queryset = TMS.objects.all()
    serializer_class = TMSSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)

    def perform_create(self, serializer):
        """Save the post data when creating a new TMS account."""
        logging.debug('TMSCreateView serializer.save started')
        serializer.save(owner=self.request.user)
        logging.debug('TMSCreateView serializer.save finished')

    def get_queryset(self, *args, **kwargs):
        return TMS.objects.all().filter(owner=self.request.user)


class TMSDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """This class handles the http GET, PUT and DELETE requests."""

    queryset = TMS.objects.all()
    serializer_class = TMSSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)

    def get_queryset(self, *args, **kwargs):
        return TMS.objects.all().filter(owner=self.request.user)


class TMSUpdateView(generics.GenericAPIView, mixins.UpdateModelMixin):
    '''
    You just need to provide the field which is to be modified.
    '''
    queryset = TMS.objects.all()
    serializer_class = TMSSerializer

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ProjectCreateView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)

    def perform_create(self, serializer):
        """Save the post data when creating a new user."""
        serializer.save(owner=self.request.user)

    def get_queryset(self, *args, **kwargs):
        return Project.objects.all().filter(owner=self.request.user)


class ProjectDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """This class handles the http GET, PUT and DELETE requests."""

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)

    def get_queryset(self, *args, **kwargs):
        return Project.objects.all().filter(owner=self.request.user)


class ProjectUpdateView(generics.GenericAPIView, mixins.UpdateModelMixin):
    '''
    You just need to provide the field which is to be modified.
    '''
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
