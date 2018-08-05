from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import UserSerializer, ProjectSerializer, TMSSerializer
from .models import Project, TMS
from .permissions import IsOwnerOrReadOnly, IsOwner
from .TMSlib.TMS import TMSTypes, TMSWrapper

import logging
logging.getLogger().setLevel(logging.DEBUG)


@ensure_csrf_cookie
def index(request, path='', format=None):
    """
    Renders the Angular2 SPA
    """
    print('format = "{}"'.format(format))
    return render(request, 'index.html')


class UserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny(),)

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
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwner,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TMSViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = TMS.objects.all()
    serializer_class = TMSSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwner,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class EstimateTMSView(APIView):

    def get(self, request, format=None):
        tms_id = request.query_params.get('tms', None)
        tms_set = TMS.objects.all().filter(owner=self.request.user, id=tms_id)
        # here we need to call an estimate method that takes TMS object which
        # includes TMS credentials
        for tms in tms_set:
            tms_wrapper = TMSWrapper(TMSTypes.JIRA, tms.endpoint, tms.username,
                                     '')
            tms_wrapper.estimate_tasks()

        return Response(tms_set, status=status.HTTP_200_OK)
