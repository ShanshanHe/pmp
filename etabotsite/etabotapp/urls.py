from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import UserViewSet, ProjectViewSet, TMSViewSet, EstimateTMSView
from .views import index
from .views import activate
from .views import email_verification
from django.contrib.auth import views as auth_views

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

    url(r'^api/verification/activate/', activate, name='activate'),
    url(r'^api/verification/send-email/', email_verification, name='email_verification'),

    url(r'^api/activate/(?P<token>[0-9A-Za-z|=]+)/?',
        activate, name='activate'),
    # password reset
    url(r'^account/password_reset/$',
        auth_views.PasswordResetView.as_view(),
        {'post_reset_redirect': '/account/password_reset/done/',
         'template_name': 'account/password_reset.html',
         'email_template_name': 'account/password_reset_email.html'},
        name="password_reset"),
    # password reset done
    url(r'^account/password_reset/done/$',
        auth_views.PasswordResetDoneView.as_view(),
        {'template_name': 'account/password_reset_done.html'},
        name='password_reset_done'),
    # password reset confirm
    url(r'^account/password_reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(),
        {'template_name': 'account/password_reset_confirm.html',
         'post_reset_redirect': '/account/password_reset/complete/'},
        name="password_reset_confirm"),
    url(r'^account/password_reset/complete/$',
        auth_views.PasswordResetCompleteView.as_view(),
        {'template_name': 'account/password_reset_complete.html'},
        name='password_reset_complete'),

    # catch-all pattern for compatibility with the Angular routes
    url(r'^(?P<path>.*)$', index),
    # url(r'^$', index)
]
