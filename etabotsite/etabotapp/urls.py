from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token
from .views import UserCreateView, TMSCreateView, TMSUpdateView, ProjectCreateView
from .views import UserDetailsView, TMSDetailsView, ProjectUpdateView, ProjectDetailsView
from .views import EstimateTMSView

urlpatterns = {
    #angular
    # catch-all pattern for compatibility with the Angular routes
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/users/', UserCreateView.as_view(), name='account-create'),
    url(r'^api/users/(?P<pk>[0-9]+)/$', UserDetailsView.as_view(), name='details'),
    url(r'^api/tms/$', TMSCreateView.as_view(), name="create"),
    url(r'^api/tms/update/(?P<pk>[0-9]+)/$', TMSUpdateView.as_view(), name="tms_update"),
    url(r'^api/tms/(?P<pk>[0-9]+)/$', TMSDetailsView.as_view(), name="details"),
    url(r'^api/projects/$', ProjectCreateView.as_view(), name="create"),
    url(r'^api/projects/update/(?P<pk>[0-9]+)/$', ProjectUpdateView.as_view(), name="project_update"),
    url(r'^api/projects/(?P<pk>[0-9]+)/$', ProjectDetailsView.as_view(), name="details"),
    url(r'^api/get-token/', obtain_auth_token),
    url(r'^api/estimate/', EstimateTMSView.as_view(), name="estimate_tms")

}

urlpatterns = format_suffix_patterns(urlpatterns)
