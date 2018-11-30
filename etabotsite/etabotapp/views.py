from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import UserSerializer, ProjectSerializer, TMSSerializer
from .models import Project, TMS
from .permissions import IsOwnerOrReadOnly, IsOwner
import TMSlib.TMS as TMSlib
import TMSlib.data_conversion as dc

from .user_activation import ActivationProcessor, ResponseCode


import json
import mimetypes
import logging
logging.getLogger().setLevel(logging.DEBUG)


@ensure_csrf_cookie
def index(request, path='', format=None):
    """
    Renders the Angular2 SPA
    """
    # logging.debug('format = "{}"'.format(format))
    # logging.debug('path = "{}"'.format(path))
    # logging.debug('request = "{}"'.format(request))
    response = render(request, 'index.html')
    # logging.debug('response: {}'.format(response))
    return response


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def activate(request):
    logging.debug('activate API started')
    post_data = json.loads(request.body.decode(encoding='utf-8'))
    logging.debug('user activate post_data: "{}"'.format(post_data))
    code = ActivationProcessor.activate_user(post_data['token'])
    body = dict()
    status_code = 500

    if code == ResponseCode.DECRYPTION_ERROR:
        body['message'] = 'Token is invalid. Please contact ETAbot.'
        body['status'] = 1
    elif code == ResponseCode.EXPIRATION_ERROR:
        body['message'] = 'Account confirmation link has expired!'
        body['status'] = 2
    elif code == ResponseCode.ALREADY_ACTIVATE_ERROR:
        body['message'] = 'You were already activated. Please login with your account!'
        body['status'] = 3
    elif code == ResponseCode.NOT_EXIST_ERROR:
        body['message'] = 'The user does not exist!'
        body['status'] = 4
    elif code == ResponseCode.SUCCESS:
        body['message'] = 'Thank you for your confirmation. Please login with your account!'
        body['status'] = 5
        status_code = 200

    return HttpResponse(json.dumps(body), content_type='application/json', status=status_code)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def email_verification(request):
    logging.debug('activate API started')
    post_data = json.loads(request.body.decode(encoding='utf-8'))
    user = User.objects.get(pk=post_data['uid'])
    body = dict()

    try:
        ActivationProcessor.email_token(user)
        body['message'] = 'Successfully sent activation email to User {}'.format(user.username)
        return HttpResponse(json.dumps(body), content_type='application/json', status=200)
    except Exception as ex:
        logging.error('Failed to send activation email to User %s: %s' % (user.username, str(ex)))
        body['message'] = 'Failed to send activation email to User {}'.format(user.username)
        return HttpResponse(json.dumps(body), content_type='application/json', status=500)


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
        objects2return = Project.objects.filter(owner=self.request.user)
        logging.debug('ProjectViewSet get_queryset:{}'.format(objects2return))
        for o in objects2return:
            logging.debug('{}: project_tms_id="{}"'.format(
                o, o.project_tms_id))
        return objects2return

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
                    'Invalid tms_id: "{}". Error: {}'.format(
                        tms_id, e),
                    status=status.HTTP_400_BAD_REQUEST)
            if len(tms_set) == 0:
                return Response(
                    'No TMS found with tms_id="{}" for user {}.'.format(
                        tms_id, self.request.user),
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            tms_set = TMS.objects.all().filter(owner=self.request.user)
        logging.debug('request.query_params: "{}"'.format(
            request.query_params))
        logging.debug('tms_id: "{}"'.format(tms_id))

        logging.debug('found tms: {}'.format(tms_set))
        if len(tms_set) == 0:
            return Response(
                'No TMS found for user {}'.format(self.request.user),
                status=status.HTTP_400_BAD_REQUEST)
        # here we need to call an estimate method that takes TMS object which
        # includes TMS credentials
        for tms in tms_set:
            project_id = request.query_params.get('project_id', None)
            if project_id is not None:
                project_id = int(project_id)
                logging.debug('subsetting project_id="{}"'.format(project_id))
                projects_set = Project.objects.all().filter(
                    owner=self.request.user,
                    project_tms_id=tms.id,
                    id=project_id)
            else:
                projects_set = Project.objects.all().filter(
                    owner=self.request.user,
                    project_tms_id=tms.id)
            logging.debug('projects_set: "{}"'.format(projects_set))
            tms_wrapper = TMSlib.TMSWrapper(tms)
            tms_wrapper.init_ETApredict(projects_set)

            project_names = []
            for project in projects_set:
                project.velocities = dc.get_velocity_json(
                    tms_wrapper.ETApredict_obj.user_velocity_per_project,
                    project.name)
                project.save()
                project_names.append(project.name)

            tms_wrapper.estimate_tasks(project_names=project_names)

        return Response(
            'TMS account to estimate: %s' % tms_set, status=status.HTTP_200_OK)
