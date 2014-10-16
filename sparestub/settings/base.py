"""
Django settings for sparestub project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

import dj_database_url
from utils.miscellaneous import get_env_variable


BASE_DIR = os.path.dirname(os.path.dirname(__file__))


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
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required by allauth and zinnia
    'contact',
    'registration',
    'user_profile',
    'photos',
    'utils',
    'djrill',

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


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/


# Parse database configuration from $DATABASE_URL
DATABASES['default'] =  dj_database_url.config()

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
AWS_BUCKET_NAME = 'sparestub'

SOCIAL_EMAIL_ADDRESS = 'shout@sparestub.com'