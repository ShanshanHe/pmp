"""
Django settings for etabotsite project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import platform
import base64
import datetime
import json
import logging
import subprocess

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

PLATFORM = platform.system()
logging.info("PLATFORM={}".format(PLATFORM))
LOCAL_MODE = True

local_host_url = 'http://127.0.0.1:8000'
prod_host_url = 'https://app.etabot.ai'
custom_settings = {}
try:
    with open('custom_settings.json') as f:
        custom_settings = json.load(f)
    logging.debug('loaded custom_settings.json with keys: \
"{}"'.format(custom_settings.keys()))
    if 'local_host_url' in custom_settings:
        local_host_url = custom_settings['local_host_url']

    if 'prod_host_url' in custom_settings:
        prod_host_url = custom_settings['prod_host_url']

except Exception as e:
    logging.warning('cannot load custom_settings.json due to "{}"'.format(
        e))

HOST_URL = local_host_url if LOCAL_MODE else prod_host_url
logging.info('HOST_URL="{}"'.format(HOST_URL))

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

django_keys = {}
try:
    with open('django_keys_prod.json') as f:
        django_keys = json.load(f)
    if (django_keys['DJANGO_SECRET_KEY'] ==
            'k3ku*za@*z$it7@+6+r46pyjv220++5kn((d)w+gozvleu-fhu' or
            django_keys['DJANGO_FIELD_ENCRYPT_KEY'] ==
            'N4h4avmBpgu_QTDr4k5jO9yUfsMIvfNGnQr21aCLbzw='):
        raise NameError('production keys from django_keys_prod.json are default \
keys - not allowed in production for security reasons')
    logging.info('loaded production keys from django_keys_prod.json')
except Exception as e:
    logging.warning('django_keys_prod.json not loaded due to "{}"'.format(e))
    if LOCAL_MODE:
        logging.warning('production keys "django_keys_prod.json" not found, \
loading default keys in local mode (for production please provide \
"django_keys_prod.json"')
        with open('django_keys.json') as f:
            django_keys = json.load(f)
    else:
        raise NameError('production keys "django_keys_prod.json" not found.\
 Cannot proceed in non-local mode')
logging.debug('loaded django_keys: "{}"'.format(django_keys.keys()))

SECRET_KEY = django_keys['DJANGO_SECRET_KEY']

# Keys used to encrypt the password for TMS accounts
FIELD_ENCRYPTION_KEY = str.encode(django_keys['DJANGO_FIELD_ENCRYPT_KEY'])

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if LOCAL_MODE else False
# DEBUG = True

# Update this in production environment to host ip for security reason
ALLOWED_HOSTS = [
    "*", "app.etabot.ai", "localhost", "127.0.0.1", "0.0.0.0", "dev.etabot.ai"]

# Life span for expiring token
EXPIRING_TOKEN_LIFESPAN = datetime.timedelta(seconds=900)


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'etabotapp',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_expiring_authtoken',
    'corsheaders',
    'encrypted_model_fields',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if LOCAL_MODE:
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

    CORS_ORIGIN_ALLOW_ALL = True
else:
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

ROOT_URLCONF = 'etabotsite.urls'

TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
print('TEMPLATE_DIR = "{}"'.format(TEMPLATE_DIR))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'etabotsite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

local_db = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }

DATABASES = {
    'default': custom_settings.get('db', local_db)
}

logging.debug('database: Engine={} Name={} Host={}'.format(
    DATABASES['default']['ENGINE'],
    DATABASES['default']['NAME'],
    DATABASES['default'].get('HOST')))

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# system email settings

SYS_DOMAIN = local_host_url if LOCAL_MODE else prod_host_url

sys_email_settings = {}
try:
    with open('sys_email_settings.json') as f:
        sys_email_settings = json.load(f)
    logging.info('loaded sys_email_settings.json: {}'.format(
        sys_email_settings.keys()))
except Exception as e:
    logging.warning('Cannot load sys_email_settings due to "{}". \
Will use default values'.format(e))

SYS_EMAIL = sys_email_settings.get('DJANGO_SYS_EMAIL', '')
SYS_EMAIL_PWD = sys_email_settings.get('DJANGO_SYS_EMAIL_PWD', '')
EMAIL_HOST = sys_email_settings.get('DJANGO_EMAIL_HOST', '')
EMAIL_USE_TLS = sys_email_settings.get('DJANGO_EMAIL_USE_TLS', True)
EMAIL_PORT = sys_email_settings.get('DJANGO_EMAIL_PORT', 587)
EMAIL_TOKEN_EXPIRATION_PERIOD_MS = 1000 * sys_email_settings.get(
    'EMAIL_TOKEN_EXPIRATION_PERIOD_S', 24 * 60 * 60)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

api_url = HOST_URL + '/api/'
logging.info('updating UI with api endpoint: "{}"'.format(api_url))
byteOutput = subprocess.check_output(
    ['python', 'set_api_url.py', 'static/ng2_app', api_url],
    cwd='etabotapp/')
print(byteOutput)
logging.info(byteOutput.decode('UTF-8'))

STATIC_URL = '/static/'
STATIC_ROOT = '../static'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True

if LOCAL_MODE:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
else:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
