"""
Django settings for sparestub project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Standard Imports
import os
import dj_database_url
import logging

# SpareStub Imports
from utils.miscellaneous import get_env_variable


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '3iy-!-d$!pc_ll$#$elg&cpr@*tfn-d5&n9ag=)%#()t$$5%5^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required by allauth and zinnia
    'haystack',
    'djrill',
    'contact',
    'registration',
    'user_profile',
    'tickets',
    'locations',
    'photos',
    'utils',
    'reviews',
    'messages',

    # All needed for zinnia
    #'django_comments',
    #'mptt',
    #'tagging',
    #'zinnia',
)

SITE_ID = 1 # Needed for allauth

TEMPLATE_CONTEXT_PROCESSORS = (
  'django.contrib.auth.context_processors.auth',
  'django.core.context_processors.i18n',
  'django.core.context_processors.request',       # Required by allauth template tags
  'zinnia.context_processors.version',  # Optional
  'utils.context_processors.environment',
  'utils.context_processors.ticket_types',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin
    "django.contrib.auth.backends.ModelBackend",
)

MANDRILL_API_KEY = get_env_variable('MANDRILL_API_KEY')
EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"

ROOT_URLCONF = 'sparestub.urls'

WSGI_APPLICATION = 'sparestub.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'
CURRENT_TIME_ZONE = 'EST'

USE_I18N = True

USE_L10N = True

USE_THOUSAND_SEPARATOR = True  # We expect currency input to contain thousands separators.
                               # They are inserted by the utoNumeric library.

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/


# Parse database configuration from $DATABASE_URL
DATABASES = dict()
DATABASES['default'] = dj_database_url.config()

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

TEMPLATE_DIRS = (
    # Location of base.html and a couple others
    os.path.join(BASE_DIR, 'templates'),
)


AUTH_USER_MODEL = 'registration.User'  # We wrote a custom user model that is used everywhere.

AWS_ACCESS_KEY_ID = get_env_variable('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = get_env_variable('AWS_SECRET_ACCESS_KEY')

SOCIAL_EMAIL_ADDRESS = 'shout@sparestub.com'
SOCIAL_EMAIL_NAME = 'SpareStub'

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static_root')

MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media_root')

DEFAULT_ZIP_CODE_CSV = os.path.join(ROOT_DIR, 'locations', 'zip_code_database.csv')
DEFAULT_ZIP_CODE_JSON = os.path.join(ROOT_DIR, 'locations', 'static', 'locations', 'json', 'zip_code_database.json')
DEFAULT_CITY_LIST_JSON = os.path.join(ROOT_DIR, 'locations', 'static', 'locations', 'json', 'cities.json')

LOGIN_URL = '/registration/login_redirect/'