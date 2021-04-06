from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import redirect
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import UserSerializer, ProjectSerializer, TMSSerializer
from .models import OAuth1Token, OAuth2Token, OAuth2CodeRequest
from .models import atlassian_redirect_uri
from .models import TMS, Project
from .models import oauth
from .permissions import IsOwnerOrReadOnly, IsOwner
# import etabotapp.TMSlib.TMS as TMSlib
# import etabotapp.TMSlib.data_conversion as dc
from .user_activation import ActivationProcessor, ResponseCode
import etabotapp.email_toolbox as email_toolbox
# import threading
import json
# import mimetypes
import logging
import celery as clry
# import os

from django.conf import settings
import datetime
import pytz
import hashlib
import etabotapp.TMSlib.Atlassian_API as Atlassian_API
# import oauth_support

logger = logging.getLogger('django')

AUTHLIB_OAUTH_CLIENTS = getattr(settings, "AUTHLIB_OAUTH_CLIENTS", False)

LOCAL_MODE = getattr(settings, "LOCAL_MODE", False)
if LOCAL_MODE:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

celery = clry.Celery()
celery.config_from_object('django.conf:settings')
# celery_app = clry.Celery('etabotapp')


@ensure_csrf_cookie
def index(request, path='', format=None):
    """
    Renders the Angular2 SPA
    """
    logging.debug('format = "{}"'.format(format))
    logging.debug('path = "{}"'.format(path))
    logging.debug('request = "{}"'.format(request))
    response = render(request, 'index.html')
    logging.debug('response: {}'.format(response))
    return response


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def activate(request):
    logging.debug('activate API started')
    post_data = json.loads(request.body)
    logging.debug('user activate post_data: "{}"'.format(post_data))
    code = ActivationProcessor.activate_user(post_data['token'])
    body = dict()
    status_code = 500

    if code == ResponseCode.DECRYPTION_ERROR:
        body['message'] = 'Token is invalid. Please contact ETAbot.'
        body['status'] = 1
    elif code == ResponseCode.EXPIRATION_ERROR:
        body['message'] = (
            'Account confirmation link has expired, we have sent a new '
            'activation link, please check your email!')
        body['status'] = 2
    elif code == ResponseCode.EXPIRATION_RESEND_ERROR:
        body['message'] = (
            'Account confirmation link has expired, activation email resend '
            'failed, please try register again!')
        body['status'] = 6
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
    post_data = json.loads(request.body)
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
    """
    serializer_class = TMSSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwner,)

    def get_queryset(self):
        # if self.request.user.is_superuser:
        #     return TMS.objects.all()
        return TMS.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        res = serializer.save(owner=self.request.user)


class ParseTMSprojects(APIView):

    def get(self, request, format=None):
        logging.debug('request.query_params: "{}"'.format(
            request.query_params))
        response_message = ''
        celery_task_ids = []
        try:
            tms_set = get_tms_set_by_id(request)
        except Exception as e:
            response_message = 'Failed to parse tms id due to "{}"'.format(e)
            logging.error(response_message)
            return Response(
                response_message,
                status=status.HTTP_400_BAD_REQUEST)
        logging.debug('starting projects parsing for tms_set: {}'.format(
            tms_set))
        try:
            res_messages = []
            for tms in tms_set:
                parse_tms_kwargs = {}
                celery_task = celery.send_task(
                    'etabotapp.django_tasks.parse_projects_for_tms_id',
                    (tms.id, parse_tms_kwargs))
                logging.info('celerty task sent, celery id ={}'.format(celery_task))
                celery_task_ids.append(celery_task.task_id)
                res_messages.append('stared celery task id {} for tms id {}'.format(
                    celery_task.task_id, tms.id))
            response_message = '\n'.join(res_messages)
        except Exception as e:
            logging.debug('parse_projects_for_TMS failed due to {}'.format(e))
            if 'not connected to JIRA' in str(e):
                response_message = 'Issue with connecting to JIRA. \
Please update your login credentials.'
            else:
                response_message = 'unknown error. If the issue persists, \
please contact us at hello@etabot.ai.'
            logging.error(response_message)
            return Response(
                response_message,
                status=status.HTTP_400_BAD_REQUEST)

        return Response(
            json.dumps({
                'result': response_message,
                'celery_task_ids': celery_task_ids}),
            status=status.HTTP_200_OK)


class AtlassianOAuth(APIView):
    def get(self, request):
        """Redirect to Atlassian for granting access to user data."""
        # logging.debug(vars(request))
        oauth_name = 'atlassian'

        permissions = request.GET.get('permissions')
        logging.debug(permissions)

        scope = AUTHLIB_OAUTH_CLIENTS.get(oauth_name, {}).get('client_kwargs', {}).get('scope')
        if permissions == 'in ETAbot only':
            scope = scope.replace('write:jira-work ', '')

        timestamp = pytz.utc.localize(datetime.datetime.utcnow())
        state = hashlib.sha256(('{}{}'.format(request.user, timestamp)).encode('utf-8')).hexdigest()
        logging.debug('state={}'.format(state))
        resp = oauth.atlassian.authorize_redirect(
            request, atlassian_redirect_uri,
            state=state,
            scope=scope)

        logging.debug(resp)
        logging.debug(vars(resp))
        oa2cr = OAuth2CodeRequest(
            owner=request.user,
            name=oauth_name,
            timestamp=timestamp,
            state=state)
        oa2cr.save()

        return Response(
            json.dumps({'redirect_url': resp.url}),
            status=status.HTTP_200_OK)


class AtlassianOAuthCallback(APIView):
    """API for Atlassian to callback after consent screen."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Receive authorization code from JIRA OAuth."""
        """Provided as a query parameter called code. This code can be
        exchanged for an access token.

        TODO: setup framework for getting access token and storing it."""
        logging.info(request.GET)
        # logging.info(request.GET.get('code'))
        logging.debug(oauth.atlassian.__dict__)
        state = request.GET.get('state')
        logging.debug('state={}'.format(state))
        try:
            token = oauth.atlassian.authorize_access_token(
                request, redirect_uri=atlassian_redirect_uri)

            logging.debug('token={}'.format(token))
        except Exception as e:
            logging.error('cannot get token due to: "{}"'.format(e))
            return redirect('/error_page')
        if token.get('expires_in') is not None:
            try:
                token['expires_in'] = int(token['expires_in'])
            except Exception as e:
                token['expires_in'] = 3600 * 24 * 30
        else:
            token['expires_in'] = 3600 * 24 * 365

        users_set = OAuth2CodeRequest.objects.all().filter(
            state=state)

        if len(users_set) == 0:
            error_message = 'no user found with such auth code request. please try again.'
            logging.warning(error_message)
            return Response(
                error_message,
                status=status.HTTP_400_BAD_REQUEST)
        elif len(users_set) > 1:
            error_message = 'Auth code request collision. please try again.'
            logging.warning(error_message)
            return Response(
                error_message,
                status=status.HTTP_400_BAD_REQUEST)
        else:
            pass
        user = users_set[0].owner
        logging.debug('user: {}, username {}'.format(
            user, user.username))
        token_item = OAuth2Token(
            owner=user,
            name='atlassian',
            token_type=token['token_type'],
            access_token=token['access_token'],
            refresh_token=token['refresh_token'],
            expires_at=token['expires_at'])

        token_item.save()
        logging.debug('token saved: {}'.format(vars(token_item)))

        new_tms_ids = self.add_update_atlassian_tms(user, token_item)
        tms_ids_list_string = construct_new_tms_ids_query_params(new_tms_ids)
        return redirect('/tmss' + tms_ids_list_string)

    def add_update_atlassian_tms(self, owner, token_item):
        """Get all available systems for the token and pass to Django models.

        Return list of ids for newly created TMS Django models
        """
        atlassian = Atlassian_API.AtlassianAPI(token_item)
        resources = atlassian.get_accessible_resources()
        logging.debug(resources)
        new_tms_ids = []
        for resource in resources:
            TMSs = TMS.objects.all().filter(
                endpoint=resource['url'],
                owner=owner)
            logging.debug('found TMSs with endpoint {}: {}'.format(
                resource['url'], TMSs))
            if len(TMSs) == 0:
                logging.debug('creating new TMS for {}'.format(resource['url']))
                new_TMS = TMS(
                    owner=owner,
                    endpoint=resource['url'],
                    type='JI',
                    name=resource.get('name'),
                    params=resource,
                    oauth2_token=token_item)
                new_TMS.save()
                new_tms_ids.append(new_TMS.id)
                logging.debug('created new TMS {}'.format(new_TMS))
            else:
                for existing_TMS in TMSs:
                    logging.debug('updating {}'.format(existing_TMS))
                    existing_TMS.params = resource
                    existing_TMS.endpoint = resource['url']
                    existing_TMS.name = resource.get('name')
                    existing_TMS.oauth2_token = token_item
                    existing_TMS.save()
                    logging.debug('updated {}'.format(existing_TMS))
        logging.debug('add_update_atlassian_tms is done')
        return new_tms_ids


def construct_new_tms_ids_query_params(new_tms_ids):
    tms_ids_list_string = ''
    if len(new_tms_ids) > 0:
        tms_ids_list_string = '?' + '&'.join([
            'new_tms_ids={}'.format(tms_id) for tms_id in new_tms_ids])
    return tms_ids_list_string


def get_tms_set_by_id(request):
    """Return tms_set on success or request Response."""
    logging.debug(request.user)
    tms_id = request.query_params.get('tms')

    tms_id = int(tms_id)
    logging.debug('int tms_id: "{}"'.format(tms_id))
    tms_set = TMS.objects.all().filter(
        owner=request.user,
        id=tms_id)
    if len(tms_set) == 0:
        raise NameError('No TMS found with tms_id={} for user {}'.format(
            tms_id, request.user))

    return tms_set


def get_projects_by_tms(user, tms_id):
    return [
        pj.id for pj in Project.objects.all().filter(
            owner=user,
            project_tms_id=tms_id)
    ]


def check_celery_worker_available():
    logging.debug('checking celery workers availability')
    # result = celery_app.control.ping(timeout=0.5)
    # logging.debug('checking celery workers availability: {}'.format(result))
    # if len(result) == 0:
    #     raise NameError('no celery workers available')


def estimate_tms(user, tms, global_params, project_id=None):
    if project_id:
        projects = [int(project_id)]
    else:
        projects = get_projects_by_tms(
            user, tms.id
        )
    logging.debug('projects: "{}"'.format(projects))
    check_celery_worker_available()
    result = celery.send_task(
        'etabotapp.django_tasks.estimate_ETA_for_TMS_project_set_ids',
        (tms.id, projects, global_params))

    # todo: stores task_id in database for this user
    return result.task_id


class EstimateTMSView(APIView):

    def post(self, request, format=None):
        """Triggers ETA updates for a particular tms_id or all.

        TODO: implement params per project."""

        logging.debug('request.user: {}, username {}'.format(
            request.user, request.user.username))

        logging.debug('self.request.user: {}, self.username {}'.format(
            self.request.user, self.request.user.username))

        post_data = {}
        if request.body:
            logging.debug('request.body: {}'.format(request.body))
            post_data = json.loads(request.body)

        logging.debug('post_data: {}'.format(post_data))
        logging.debug('request.query_params: "{}"'.format(
            request.query_params))

        if request.query_params.get('tms') is None:
            # no tms id given, estimate for all TMS for this user
            tms_set = TMS.objects.all().filter(owner=self.request.user)
        else:
            try:
                tms_set = get_tms_set_by_id(request)
            except Exception as e:
                return Response(
                    {
                        "error":
                            "No TMS found with tms_id=\"{}\" for user {} due "
                            "to: {}".format(
                                request.query_params.get('tms'),
                                self.request.user, e)
                    },
                    status=status.HTTP_400_BAD_REQUEST)

        logging.debug('found tms: {}'.format(tms_set))
        if len(tms_set) == 0:
            return Response(
                'No TMS found for user {}'.format(self.request.user),
                status=status.HTTP_400_BAD_REQUEST)
        # here we need to call an estimate method that takes TMS object which
        # includes TMS credentials
        # threads = []
        global_params = post_data.get('params', {})
        logging.debug('estimate call global_params: {}'.format(global_params))

        tms_id_to_celery_task_id = {
            tms.id: estimate_tms(
                self.request.user, tms, global_params,
                request.query_params.get('project_id', None))
            for tms in tms_set
        }

        response_message = 'TMS account to estimate:{}. \
Number of tasks sent: {}'.format(tms_set, len(tms_id_to_celery_task_id))
        return Response(
            data=tms_id_to_celery_task_id,
            status=status.HTTP_200_OK)


class VoteView(APIView):
    """Collecting votes."""

    def post(self, request):
        logging.debug('vote view get started')
        post_data = {}
        if request.body:
            logging.debug('request.body: {}'.format(request.body))
            post_data = json.loads(request.body)

        choice = post_data.get('choice')
        subject = 'user "{}" votes: "{}"'.format(
                request.user,
                choice)
        msg_body = str(post_data)
        msg = email_toolbox.EmailWorker.format_email_msg(
            'no-reply@etabot.ai',
            'hello@etabot.ai; alex@etabot.ai',
            subject,
            msg_body)
        email_toolbox.EmailWorker.send_email(msg)
        logging.debug('vote view get finished')
        return Response(
            status=status.HTTP_200_OK)


class CeleryTaskStatusView(APIView):

    def get(self, request, id):
        """
        Get celery task status for a particular celery task id.
        """
        # https://stackoverflow.com/questions/9034091/how-to-check-task-status-in-celery
        logging.debug('CeleryTaskStatusView GET started')
        task_id = id
        logging.debug('CeleryTaskStatusView GET started with id={}'.format(id))
        if not task_id:
            response_dict = {'error': 'Celery task id not provided!'}
            logging.debug('CeleryTaskStatusView GET returning {}'.format(response_dict))
            return Response(
                response_dict,
                status=status.HTTP_400_BAD_REQUEST)
        logging.debug('task status: {}'.format(
            celery.AsyncResult(task_id).status))
        response_dict = {
            task_id: celery.AsyncResult(task_id).status,
            '{}_result'.format(task_id): str(celery.AsyncResult(task_id).result)
        }
        logging.debug('CeleryTaskStatusView GET returning {}'.format(response_dict))
        return Response(
            data=response_dict,
            status=status.HTTP_200_OK)
