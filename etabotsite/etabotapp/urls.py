from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import UserViewSet, ProjectViewSet, TMSViewSet, EstimateTMSView
from .views import index
from .views import activate

router = DefaultRouter()
router.register(r'users', UserViewSet, base_name='users')
router.register(r'projects', ProjectViewSet, base_name='projects')
router.register(r'tms', TMSViewSet, base_name='tms')

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api/auth/',
        include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/get-token/', obtain_auth_token),
    url(r'^api/estimate/', EstimateTMSView.as_view(), name="estimate_tms"),
    url(
        r'^api/activate/(?P<token>[0-9A-Za-z|=]+)',
        activate, name='activate'),

    # catch-all pattern for compatibility with the Angular routes
    url(r'^(?P<path>.*)$', index),
    # url(r'^$', index)
]
