from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import UserSerializer, ProjectSerializer, TMSSerializer
from .models import Project, TMS
from .permissions import IsOwnerOrReadOnly, IsOwner
import TMSlib.TMS as TMSlib
from .user_activation import ActivationProcessor, ResponseCode

import logging
logging.getLogger().setLevel(logging.DEBUG)


@ensure_csrf_cookie
def index(request, path='', format=None):
    """
    Renders the Angular2 SPA
    """
    # print('format = "{}"'.format(format))
    return render(request, 'index.html')


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def activate(request, token):
    logging.debug('activate API started')
    code = ActivationProcessor.activate_user(token)

    if code == ResponseCode.DECRYPTION_ERROR:
        return Response('Token is invalid. Please contact ETAbot.')
    elif code == ResponseCode.EXPIRATION_ERROR:
        return Response('Token already expired!')
    elif code == ResponseCode.ALREADY_ACTIVATE_ERROR:
        return Response('The user was already activated!')
    elif code == ResponseCode.NOT_EXIST_ERROR:
        return Response('The user does not exist!')
    elif code == ResponseCode.SUCCESS:
        return Response('The user is successfully activated!')
    else:
        return Response('Something wrong!')


class UserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny(),)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(owner=self.request.user)

    def get_permissions(self):
        # allow non-authenticated user to create via POST
        return (permissions.AllowAny() if self.request.method == 'POST'
                else IsOwnerOrReadOnly()),


class ProjectViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwner,)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Project.objects.all()
        return Project.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TMSViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    serializer_class = TMSSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwner,)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return TMS.objects.all()
        return TMS.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class EstimateTMSView(APIView):

    def get(self, request, format=None):
        tms_id = request.query_params.get('tms', None)
        if tms_id is not None:
            try:
                tms_id = int(tms_id)
                tms_set = TMS.objects.all().filter(
                    owner=self.request.user,
                    id=tms_id)
            except Exception as e:
                return Response(
                    'Invalid tms_id: "{}"'.format(tms_id),
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            tms_set = TMS.objects.all().filter(owner=self.request.user)
        logging.debug('request.query_params: "{}"'.format(
            request.query_params))
        logging.debug('tms_id: "{}"'.format(tms_id))

        logging.debug('found tms: {}'.format(tms_set))
        # here we need to call an estimate method that takes TMS object which
        # includes TMS credentials
        for tms in tms_set:
            projects_set = Project.objects.all().filter(
                owner=self.request.user, project_tms_id=tms.id)

            tms_wrapper = TMSlib.TMSWrapper(tms)
            tms_wrapper.init_ETApredict(projects_set)
            tms_wrapper.estimate_tasks(projects_set)

        return Response(
            'TMS account to estimate: %s' % tms_set, status=status.HTTP_200_OK)
