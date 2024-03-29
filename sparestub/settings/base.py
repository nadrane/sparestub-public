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
SECRET_KEY = 'fmwJ774fU>kuGW/4Tx]/7Fwk4GvGEFn@FNXn4n6z7(F;,{gH,3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required by allauth and zinnia
    'django.contrib.humanize',
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
    'asks',
    'stripe_data',
    'compressor',
    'djangosecure',

    # All needed for zinnia
    #'django_comments',
    #'mptt',
    #'tagging',
    #'zinnia',
)

SITE_ID = 1  # Needed for allauth

TEMPLATE_CONTEXT_PROCESSORS = (
  'django.contrib.auth.context_processors.auth',
  'django.core.context_processors.i18n',
  'django.core.context_processors.request',       # Required by allauth template tags
  'zinnia.context_processors.version',  # Optional - for Zinnia
  'utils.context_processors.environment',
  'utils.context_processors.ticket_types',
  'utils.context_processors.stripe_public_key',
)

MIDDLEWARE_CLASSES = (
    'djangosecure.middleware.SecurityMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = ('registration.backends.user_backend.UserBackend',)

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
FORMAT_MODULE_PATH = 'formats'

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

TEMPLATE_DIRS = (
    # Location of base.html and a couple others
    os.path.join(BASE_DIR, 'templates'),

    # Locations of email templates
    os.path.join(os.path.dirname(BASE_DIR), 'registration', 'email_templates'),
    os.path.join(os.path.dirname(BASE_DIR), 'messages', 'email_templates'),
    os.path.join(os.path.dirname(BASE_DIR), 'contact', 'email_templates'),
    os.path.join(os.path.dirname(BASE_DIR), 'asks', 'email_templates'),
    os.path.join(os.path.dirname(BASE_DIR), 'tickets', 'email_templates'),
)

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

STATICFILES_FINDERS = ("django.contrib.staticfiles.finders.FileSystemFinder",
                       "django.contrib.staticfiles.finders.AppDirectoriesFinder"
                       )

AUTH_USER_MODEL = 'registration.User'  # We wrote a custom user model that is used everywhere.

AWS_ACCESS_KEY_ID = get_env_variable('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = get_env_variable('AWS_SECRET_ACCESS_KEY')

AWS_QUERYSTRING_EXPIRE = 99999999  # This cannot be a small number! When we compress our files offline, they are set to
                                   # expire this many seconds from the creation date. We obviously can't have our static
                                   # files ever reaching this expiration date, or S3 will give us a 403 error.
AWS_IS_GZIPPED = True
AWS_QUERYSTRING_AUTH = False

SOCIAL_EMAIL_ADDRESS = 'shout@sparestub.com'
SOCIAL_EMAIL_NAME = 'SpareStub'

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static_root')

MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media_root')

# These files will actually be read from a socket stream on the PRD and STG servers since the CSV file won't exist locally
DEFAULT_ZIP_CODE_CSV = os.path.join(ROOT_DIR, 'locations', 'static', 'locations', 'csv', 'zip_code_database.csv')
DEFAULT_ZIP_CODE_JSON = os.path.join(ROOT_DIR, 'locations', 'static', 'locations', 'json', 'zip_code_database.json')
DEFAULT_CITY_LIST_JSON = os.path.join(ROOT_DIR, 'locations', 'static', 'locations', 'json', 'cities.json')

LOGIN_URL = '/registration/login_redirect/'
LOGIN_REDIRECT_URL = '/'

SEND_EMAILS = False  # Default to sending emails unless a specific settings file disables it
# django-compressor settings

COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter', 'compressor.filters.cssmin.CSSMinFilter']
COMPRESS_JS_FILTERS = ['compressor.filters.closure.ClosureCompilerFilter']
COMPRESS_CLOSURE_COMPILER_BINARY = "java -jar " + os.path.join(os.path.dirname(BASE_DIR), "closure-compiler/compiler.jar")
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
STATICFILES_FINDERS += ('compressor.finders.CompressorFinder',)

# Celery Configuration
BROKER_TRANSPORT_OPTIONS = {'fanout_prefix': True}
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_SERIALIZER = 'json'

# django-secure
SECURE_SSL_REDIRECT = False